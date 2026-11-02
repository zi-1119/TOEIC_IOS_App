import CryptoKit
import Foundation

struct InstalledContentBatch: Sendable {
    let batch: ImportedContentBatch
    /// The complete merged package after this install, not only the last batch.
    let package: ContentPackage
    let rootURL: URL
    let wasAlreadyInstalled: Bool
    let activeBatchIDs: [String]
    let mockForms: [ResolvedMockExamForm]
}

struct ContentImportIndex: Codable, Hashable, Sendable {
    struct GroupEntry: Codable, Hashable, Sendable {
        let groupID: String
        let version: Int
        let contentHash: String
        let batchID: String
        let familyID: String
        let pool: BatchPool
        let itemIDs: [String]
    }
    var groups: [GroupEntry] = []
}

struct ContentStoreState: Codable, Hashable, Sendable {
    var schemaVersion = 1
    var index = ContentImportIndex()
    var activeBatchIDs: [String] = []
}

struct ContentVersionStore {
    private let rootURL: URL
    private let fileManager: FileManager

    init(rootURL: URL? = nil, fileManager: FileManager = .default) {
        self.fileManager = fileManager
        if let rootURL { self.rootURL = rootURL }
        else {
            let base = fileManager.urls(for: .applicationSupportDirectory, in: .userDomainMask).first!
            self.rootURL = base.appending(path: "TOEICPath/Content", directoryHint: .isDirectory)
        }
    }

    var storageRootURL: URL { rootURL }

    func install(from source: URL) throws -> InstalledContentBatch {
        try fileManager.createDirectory(at: rootURL, withIntermediateDirectories: true)
        let stagingRoot = rootURL.appending(path: "Staging", directoryHint: .isDirectory)
        try fileManager.createDirectory(at: stagingRoot, withIntermediateDirectories: true)
        let staging = stagingRoot.appending(path: UUID().uuidString, directoryHint: .isDirectory)
        try fileManager.copyItem(at: source, to: staging)
        var stagingWasMoved = false
        defer { if !stagingWasMoved { try? fileManager.removeItem(at: staging) } }

        let batch = try ContentBatchImporter.loadAndValidate(directory: staging, fileManager: fileManager)
        let state = try loadState()
        try validateCrossBatch(batch.groups, existing: state.index)

        let versionsRoot = rootURL.appending(path: "Versions", directoryHint: .isDirectory)
        try fileManager.createDirectory(at: versionsRoot, withIntermediateDirectories: true)
        let destination = versionsRoot.appending(path: batch.manifest.batchID, directoryHint: .isDirectory)
        if fileManager.fileExists(atPath: destination.path) {
            let installed = try ContentBatchImporter.loadAndValidate(directory: destination, fileManager: fileManager)
            guard installed.manifest.files == batch.manifest.files else { throw StoreError.batchIDConflict(batch.manifest.batchID) }
            var activatedState = state
            if !activatedState.activeBatchIDs.contains(batch.manifest.batchID) {
                activatedState.activeBatchIDs.append(batch.manifest.batchID)
            }
            let catalog = try mergedCatalog(for: activatedState)
            if activatedState != state { try saveState(activatedState) }
            return .init(batch: installed, package: catalog.package, rootURL: destination,
                         wasAlreadyInstalled: true, activeBatchIDs: activatedState.activeBatchIDs,
                         mockForms: catalog.mockForms)
        }

        let newEntries = try batch.groups.map { group in
            ContentImportIndex.GroupEntry(
                groupID: group.groupID, version: group.version, contentHash: try groupHash(group),
                batchID: batch.manifest.batchID, familyID: group.familyID, pool: group.pool,
                itemIDs: group.items.map(\.itemID)
            )
        }
        var newState = state
        newState.index.groups.append(contentsOf: newEntries)
        if !newState.activeBatchIDs.contains(batch.manifest.batchID) {
            newState.activeBatchIDs.append(batch.manifest.batchID)
        }

        try fileManager.moveItem(at: staging, to: destination)
        stagingWasMoved = true
        do {
            let catalog = try mergedCatalog(for: newState)
            try saveState(newState)
            return .init(batch: batch, package: catalog.package, rootURL: destination,
                         wasAlreadyInstalled: false, activeBatchIDs: newState.activeBatchIDs,
                         mockForms: catalog.mockForms)
        } catch {
            try? fileManager.removeItem(at: destination)
            throw error
        }
    }

    /// Validates and activates a set of immutable batches as one catalog transaction.
    /// No active state changes, and every newly moved version is removed, if any batch
    /// or the final merged catalog fails validation.
    func installAtomically(from sources: [URL]) throws -> InstalledContentCatalog {
        guard !sources.isEmpty else { throw StoreError.emptyActivation }
        try fileManager.createDirectory(at: rootURL, withIntermediateDirectories: true)
        let stagingRoot = rootURL.appending(path: "Staging", directoryHint: .isDirectory)
        try fileManager.createDirectory(at: stagingRoot, withIntermediateDirectories: true)
        let transactionRoot = stagingRoot.appending(path: "seed-\(UUID().uuidString)", directoryHint: .isDirectory)
        try fileManager.createDirectory(at: transactionRoot, withIntermediateDirectories: true)
        defer { try? fileManager.removeItem(at: transactionRoot) }

        var staged: [(directory: URL, batch: ImportedContentBatch)] = []
        for (index, source) in sources.enumerated() {
            let directory = transactionRoot.appending(path: "batch-\(index)", directoryHint: .isDirectory)
            try fileManager.copyItem(at: source, to: directory)
            staged.append((directory, try ContentBatchImporter.loadAndValidate(directory: directory, fileManager: fileManager)))
        }

        let originalState = try loadState()
        var candidateState = originalState
        var seenBatchIDs = Set<String>()
        var pendingMoves: [(staging: URL, destination: URL)] = []
        let versionsRoot = rootURL.appending(path: "Versions", directoryHint: .isDirectory)
        try fileManager.createDirectory(at: versionsRoot, withIntermediateDirectories: true)

        for entry in staged {
            let batch = entry.batch
            guard seenBatchIDs.insert(batch.manifest.batchID).inserted else {
                throw StoreError.duplicateBatchInTransaction(batch.manifest.batchID)
            }
            try validateCrossBatch(batch.groups, existing: candidateState.index)
            let destination = versionsRoot.appending(path: batch.manifest.batchID, directoryHint: .isDirectory)
            if fileManager.fileExists(atPath: destination.path) {
                let installed = try ContentBatchImporter.loadAndValidate(directory: destination, fileManager: fileManager)
                guard installed.manifest.files == batch.manifest.files else {
                    throw StoreError.batchIDConflict(batch.manifest.batchID)
                }
            } else {
                pendingMoves.append((entry.directory, destination))
            }

            let entries = try indexEntries(for: batch)
            for indexEntry in entries where !candidateState.index.groups.contains(where: {
                $0.groupID == indexEntry.groupID && $0.version == indexEntry.version && $0.batchID == indexEntry.batchID
            }) {
                candidateState.index.groups.append(indexEntry)
            }
            if !candidateState.activeBatchIDs.contains(batch.manifest.batchID) {
                candidateState.activeBatchIDs.append(batch.manifest.batchID)
            }
        }

        var movedDestinations: [URL] = []
        do {
            for move in pendingMoves {
                try fileManager.moveItem(at: move.staging, to: move.destination)
                movedDestinations.append(move.destination)
            }
            let catalog = try mergedCatalog(for: candidateState)
            if candidateState != originalState { try saveState(candidateState) }
            return catalog
        } catch {
            for destination in movedDestinations.reversed() { try? fileManager.removeItem(at: destination) }
            throw error
        }
    }

    func activePackage() throws -> ContentPackage? {
        try activeCatalog()?.package
    }

    func activeCatalog() throws -> InstalledContentCatalog? {
        let state = try loadState()
        guard !state.activeBatchIDs.isEmpty else { return nil }
        return try mergedCatalog(for: state)
    }

    func activeBatchIDs() throws -> [String] { try loadState().activeBatchIDs }

    func validateCrossBatch(_ groups: [BatchGroup], existing: ContentImportIndex) throws {
        let encoder = configuredEncoder()
        for group in groups {
            let hash = SHA256.hash(data: try encoder.encode(group)).hex
            if let sameVersion = existing.groups.first(where: { $0.groupID == group.groupID && $0.version == group.version }),
               sameVersion.contentHash != hash {
                throw StoreError.sameVersionDifferentContent(groupID: group.groupID, version: group.version)
            }
            let conflictingItems = Set(existing.groups.filter { $0.groupID != group.groupID }.flatMap(\.itemIDs))
            if let conflict = group.items.map(\.itemID).first(where: { conflictingItems.contains($0) }) {
                throw StoreError.itemIDConflict(conflict)
            }
            if let family = existing.groups.first(where: { $0.familyID == group.familyID && $0.pool != group.pool }) {
                throw StoreError.familyPoolConflict(familyID: family.familyID, oldPool: family.pool, newPool: group.pool)
            }
        }
    }

    static func mergePackages(_ packages: [ContentPackage]) -> ContentPackage? {
        guard !packages.isEmpty else { return nil }
        var selectedByID: [String: QuestionGroup] = [:]
        var orderedIDs: [String] = []
        for package in packages {
            for group in package.groups {
                if selectedByID[group.id] == nil { orderedIDs.append(group.id) }
                if let current = selectedByID[group.id], current.version > group.version { continue }
                selectedByID[group.id] = group
            }
        }
        let groups = orderedIDs.compactMap { selectedByID[$0] }
        let versionInput = groups.sorted { $0.id < $1.id }
            .map { "\($0.id)@\($0.version)@\($0.sourceBatchID)" }.joined(separator: "|")
        let digest = SHA256.hash(data: Data(versionInput.utf8)).hex.prefix(16)
        let assets = Dictionary(
            packages.flatMap(\.assets).map { ($0.id, $0) },
            uniquingKeysWith: { first, _ in first }
        ).values.sorted { $0.id < $1.id }
        return ContentPackage(
            manifest: .init(
                schemaVersion: 1, packageID: "active-batch-catalog", contentVersion: "catalog-\(digest)",
                locale: "en", createdAt: packages.map(\.manifest.createdAt).max() ?? .now,
                generator: "TOEICPath ContentVersionStore", generatorVersion: "2", license: "See source batches"
            ),
            assets: assets,
            groups: groups
        )
    }

    private func mergedCatalog(for state: ContentStoreState) throws -> InstalledContentCatalog {
        var packages: [ContentPackage] = []
        var contexts: [MockFormContractResolver.BatchContext] = []
        for batchID in state.activeBatchIDs {
            let directory = rootURL.appending(path: "Versions/\(batchID)", directoryHint: .isDirectory)
            guard fileManager.fileExists(atPath: directory.path) else { throw StoreError.activeBatchMissing(batchID) }
            let batch = try ContentBatchImporter.loadAndValidate(directory: directory, fileManager: fileManager)
            packages.append(batch.runtimePackage(rootURL: directory))
            contexts.append(.init(
                manifest: batch.manifest,
                manifestSHA256: try manifestSHA256(at: directory),
                groups: batch.groups,
                report: batch.mockFormReport,
                rootURL: directory
            ))
        }
        guard let package = Self.mergePackages(packages) else { throw StoreError.emptyActivation }
        let forms = try MockFormContractResolver.resolve(contexts)
        return .init(package: package, mockForms: forms)
    }

    private func loadState() throws -> ContentStoreState {
        let stateURL = rootURL.appending(path: "state.json")
        if fileManager.fileExists(atPath: stateURL.path) {
            let state = try JSONDecoder().decode(ContentStoreState.self, from: Data(contentsOf: stateURL))
            guard state.schemaVersion == 1 else { throw StoreError.unsupportedStateVersion(state.schemaVersion) }
            return state
        }

        // One-time read compatibility for the former index.json + active.json layout.
        let legacyIndexURL = rootURL.appending(path: "index.json")
        let legacyIndex = fileManager.fileExists(atPath: legacyIndexURL.path)
            ? try JSONDecoder().decode(ContentImportIndex.self, from: Data(contentsOf: legacyIndexURL))
            : ContentImportIndex()
        let legacyActiveURL = rootURL.appending(path: "active.json")
        let activeID = try? JSONDecoder().decode(LegacyActivePointer.self, from: Data(contentsOf: legacyActiveURL)).batchID
        return ContentStoreState(index: legacyIndex, activeBatchIDs: activeID.map { [$0] } ?? [])
    }

    private func saveState(_ state: ContentStoreState) throws {
        try configuredEncoder().encode(state).write(to: rootURL.appending(path: "state.json"), options: .atomic)
    }

    private func groupHash(_ group: BatchGroup) throws -> String {
        SHA256.hash(data: try configuredEncoder().encode(group)).hex
    }

    private func indexEntries(for batch: ImportedContentBatch) throws -> [ContentImportIndex.GroupEntry] {
        try batch.groups.map { group in
            ContentImportIndex.GroupEntry(
                groupID: group.groupID, version: group.version, contentHash: try groupHash(group),
                batchID: batch.manifest.batchID, familyID: group.familyID, pool: group.pool,
                itemIDs: group.items.map(\.itemID)
            )
        }
    }

    private func configuredEncoder() -> JSONEncoder {
        let encoder = JSONEncoder()
        encoder.dateEncodingStrategy = .iso8601
        encoder.outputFormatting = [.sortedKeys]
        return encoder
    }

    private struct LegacyActivePointer: Codable { let batchID: String }

    enum StoreError: LocalizedError {
        case batchIDConflict(String)
        case sameVersionDifferentContent(groupID: String, version: Int)
        case itemIDConflict(String)
        case familyPoolConflict(familyID: String, oldPool: BatchPool, newPool: BatchPool)
        case activeBatchMissing(String)
        case emptyActivation
        case duplicateBatchInTransaction(String)
        case unsupportedStateVersion(Int)
        var errorDescription: String? {
            switch self {
            case .batchIDConflict(let id): "批次 \(id) 已存在，但 manifest 不同。"
            case .sameVersionDifferentContent(let id, let version): "\(id) 版本 \(version) 已存在不同內容，不可覆寫。"
            case .itemIDConflict(let id): "item_id \(id) 已屬於另一題組。"
            case .familyPoolConflict(let id, let old, let new): "family \(id) 已在 \(old.rawValue)，不可再匯入 \(new.rawValue)。"
            case .activeBatchMissing(let id): "啟用中的批次 \(id) 已遺失，未切換到不完整題庫。"
            case .emptyActivation: "沒有可合併的啟用題庫。"
            case .duplicateBatchInTransaction(let id): "同一次安裝重複包含批次 \(id)。"
            case .unsupportedStateVersion(let version): "不支援題庫狀態版本 \(version)。"
            }
        }
    }
}

private extension Digest {
    var hex: String { map { String(format: "%02x", $0) }.joined() }
}
