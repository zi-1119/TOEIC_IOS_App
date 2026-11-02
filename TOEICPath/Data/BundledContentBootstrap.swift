import Foundation

enum BundledSeedContent {
    static let resourceName = "SeedContent"
    static let batchDirectoryNames = (1...7).map { String(format: "batch-ag-%04d", $0) }

    static func rootURL(in bundle: Bundle = .main) -> URL? {
        bundle.url(forResource: resourceName, withExtension: nil)
    }

    static func batchDirectories(rootURL: URL, fileManager: FileManager = .default) throws -> [URL] {
        try batchDirectoryNames.map { name in
            let directory = rootURL.appending(path: name, directoryHint: .isDirectory)
            var isDirectory: ObjCBool = false
            guard fileManager.fileExists(atPath: directory.path, isDirectory: &isDirectory), isDirectory.boolValue else {
                throw BundledSeedError.missingBatch(name)
            }
            return directory
        }
    }
}

enum BundledSeedError: LocalizedError {
    case missingResource
    case missingBatch(String)
    case unexpectedBatchID(directory: String, manifest: String)
    case installInProgress

    var errorDescription: String? {
        switch self {
        case .missingResource:
            "App 內找不到離線題庫資源。請重新建置安裝後再試。"
        case .missingBatch(let name):
            "離線題庫缺少 \(name)，未變更目前題庫。"
        case let .unexpectedBatchID(directory, manifest):
            "離線題庫目錄 \(directory) 的 batch_id 是 \(manifest)，未變更目前題庫。"
        case .installInProgress:
            "離線題庫正在驗證，完成後才能匯入其他批次。"
        }
    }
}

actor BundledContentBootstrapper {
    private let store: ContentVersionStore
    private let fileManager = FileManager.default

    init(rootURL: URL) {
        self.store = ContentVersionStore(rootURL: rootURL)
    }

    func install(rootURL: URL) throws -> InstalledContentCatalog {
        let directories = try BundledSeedContent.batchDirectories(rootURL: rootURL, fileManager: fileManager)
        for (expectedName, directory) in zip(BundledSeedContent.batchDirectoryNames, directories) {
            let batch = try ContentBatchImporter.loadAndValidate(directory: directory, fileManager: fileManager)
            guard batch.manifest.batchID == expectedName else {
                throw BundledSeedError.unexpectedBatchID(directory: expectedName, manifest: batch.manifest.batchID)
            }
        }
        return try store.installAtomically(from: directories)
    }
}
