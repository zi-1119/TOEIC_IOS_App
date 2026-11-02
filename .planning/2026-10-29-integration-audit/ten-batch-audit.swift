import Foundation
@testable import TOEICPath

let repo = URL(fileURLWithPath: "/Users/ziii/Desktop/TOEIC_IOS_App")
let scratch = FileManager.default.temporaryDirectory.appending(path: "TOEIC-TenBatchAudit-\(UUID().uuidString)")
defer { try? FileManager.default.removeItem(at: scratch) }
do {
    let store = ContentVersionStore(rootURL: scratch)
    for n in 1...10 {
        let id = String(format: "batch-ag-%04d", n)
        let stateBefore = try? Data(contentsOf: scratch.appending(path: "state.json"))
        let result: InstalledContentBatch
        do {
            result = try store.install(from: repo.appending(path: "exports/\(id)"))
        } catch {
            let after = try? Data(contentsOf: scratch.appending(path: "state.json"))
            print("REJECTED \(id): \(error); atomic state preserved=\(stateBefore == after)")
            continue
        }
        print("INSTALL \(id): groups=\(result.package.groups.count) items=\(result.package.groups.flatMap(\.items).count) assets=\(result.package.assets.count)")
    }
    let reopened = ContentVersionStore(rootURL: scratch)
    guard let catalog = try reopened.activeCatalog() else { fatalError("missing restored catalog") }
    let package = catalog.package
    print("ACTUAL RESTORED groups=\(package.groups.count) items=\(Set(package.groups.flatMap(\.items).map(\.id)).count) assets=\(package.assets.count)")
    for asset in package.assets { precondition(FileManager.default.fileExists(atPath: asset.path)) }
    for purpose: ContentPurpose in [.training, .diagnostic, .battle, .mock] {
        let groups = ContentEligibility.formalGroups(in: package.groups, for: purpose)
        print("ELIGIBLE \(purpose): groups=\(groups.count) items=\(groups.flatMap(\.items).count)")
    }
    let plan = DailyPlanner.makePlan(groups: package.groups, profile: LocalProfile())
    precondition(plan.groups.allSatisfy { $0.purpose == .training })
    let training = package.groups.filter { $0.purpose == .training }
    precondition(DiagnosticRouter.nextGroup(from: training, selectedGroups: [], responses: []) == nil)
    if let selection = DiagnosticRouter.nextGroup(from: package.groups, selectedGroups: [], responses: []) {
        precondition(selection.group.purpose == .diagnostic)
        print("DIAGNOSTIC ROUTING: \(selection.group.id) uses diagnostic pool")
    }
    let picker = PartPracticeSelector.select(part: .part5, from: package.groups, profile: LocalProfile())
    print("PART5 PICKER: new=\(picker.newGroups.count) review=\(picker.reviewGroups.count)")
    let repeated = try reopened.install(from: repo.appending(path: "exports/batch-ag-0007"))
    precondition(repeated.wasAlreadyInstalled)
    print("PASS restore/reimport/isolation; mock forms=\(catalog.mockForms.count)")
} catch {
    print("FAILED: \(error) / \(error.localizedDescription)")
    exit(1)
}
