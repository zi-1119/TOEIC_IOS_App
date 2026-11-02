import Foundation
@testable import TOEICPath

let repo = URL(fileURLWithPath: "/Users/ziii/Desktop/TOEIC_IOS_App")
let scratch = FileManager.default.temporaryDirectory.appending(path: "TOEIC-SevenBatchAudit-\(UUID().uuidString)")
let store = ContentVersionStore(rootURL: scratch)
defer { try? FileManager.default.removeItem(at: scratch) }
do {
    for number in 1...7 {
        let id = String(format: "batch-ag-%04d", number)
        let result = try store.install(from: repo.appending(path: "exports/\(id)"))
        print("INSTALL \(id): active=\(result.activeBatchIDs.count) groups=\(result.package.groups.count) items=\(result.package.groups.flatMap(\.items).count) assets=\(result.package.assets.count) forms=\(result.mockForms.count)")
    }
    let reopened = ContentVersionStore(rootURL: scratch)
    guard let catalog = try reopened.activeCatalog() else { fatalError("No restored catalog") }
    let package = catalog.package
    precondition(package.groups.count == 51)
    precondition(package.groups.flatMap(\.items).count == 100)
    precondition(Set(package.groups.flatMap(\.items).map(\.id)).count == 100)
    precondition(package.assets.count == 30)
    let lookup = Dictionary(uniqueKeysWithValues: package.assets.map { ($0.id, $0) })
    for asset in package.assets { precondition(FileManager.default.fileExists(atPath: asset.path), asset.path) }
    for group in package.groups where group.part.section == .listening {
        precondition(group.version == 2)
        precondition(lookup[group.audioAssetID ?? ""] != nil)
        precondition(!group.audioSegments.isEmpty)
        if group.part == .part1 {
            for item in group.items { precondition(lookup[item.imageAssetID ?? ""] != nil) }
        }
    }
    for part in TOEICPart.allCases {
        print("PART \(part): \(package.groups.filter { $0.part == part }.flatMap(\.items).count)")
    }
    print("RESTORE PASS: 100 unique items, 27 v2 listening groups, 30 existing assets; forms=\(catalog.mockForms.count)")
    let repeated = try reopened.install(from: repo.appending(path: "exports/batch-ag-0007"))
    precondition(repeated.wasAlreadyInstalled && repeated.package.groups.flatMap(\.items).count == 100)
    print("REIMPORT PASS: no growth")
    if let selection = DiagnosticRouter.nextGroup(from: package.groups, selectedGroups: [], responses: []) {
        print("ISOLATION GAP: diagnostic selected \(selection.group.id) tags=\(selection.group.tags)")
    }
    let base = package.groups.first { $0.part == .part5 }!
    let reserved = QuestionGroup(
        id: "audit-mock-only", version: 1, sourceBatchID: "audit-only", familyID: "audit-mock-family",
        part: base.part, difficulty: base.difficulty, scenario: base.scenario, documents: base.documents,
        items: base.items, audioAssetID: nil, timeLimitSeconds: nil, tags: ["mock"]
    )
    let daily = DailyPlanner.makePlan(groups: [reserved], profile: LocalProfile())
    print("ISOLATION PROBE: daily training selected mock-only groups=\(daily.groups.count) (expected 0)")
} catch {
    print("AUDIT FAILED: \(error) / \(error.localizedDescription)")
    exit(1)
}
