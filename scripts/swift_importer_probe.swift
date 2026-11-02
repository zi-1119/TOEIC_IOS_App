// PRODUCER-SIDE REFERENCE PROBE ONLY (Antigravity, 2026-10-31).
// Uses the current ContentVersionStore API (install(from:), activeCatalog()).
// It is NOT the receiver acceptance test: acceptance of new batches is decided and reported by Codex.
// It never edits App/Swift sources; it is compiled from a throwaway SwiftPM package outside the repo
// that depends on the repo's TOEICPathCore library by path (see scripts/run_swift_importer_probe.sh).
import Foundation
@testable import TOEICPath

let repo = URL(fileURLWithPath: "/Users/ziii/Desktop/TOEIC_IOS_App")
let order = CommandLine.arguments.dropFirst().isEmpty
    ? ["0001", "0002", "0003", "0004", "0005", "0006", "0007", "0011", "0012", "0013", "0014", "0015"]
    : Array(CommandLine.arguments.dropFirst())
let scratch = FileManager.default.temporaryDirectory.appending(path: "AG-ImporterProbe-\(UUID().uuidString)")
defer { try? FileManager.default.removeItem(at: scratch) }

var failures = 0
let store = ContentVersionStore(rootURL: scratch)
for n in order {
    let id = "batch-ag-\(n)"
    do {
        let r = try store.install(from: repo.appending(path: "exports/\(id)"))
        print("INSTALL \(id): batchGroups=\(r.batch.groups.count) batchItems=\(r.batch.groups.flatMap(\.items).count) catalogGroups=\(r.package.groups.count) catalogItems=\(r.package.groups.flatMap(\.items).count)")
    } catch {
        failures += 1
        print("REJECTED \(id): \(error)")
    }
}
do {
    let reopened = ContentVersionStore(rootURL: scratch)
    guard let catalog = try reopened.activeCatalog() else { print("NO ACTIVE CATALOG"); exit(1) }
    let groups = catalog.package.groups
    print("ACTIVE groups=\(groups.count) items=\(Set(groups.flatMap(\.items).map(\.id)).count) assets=\(catalog.package.assets.count)")
    let versions = Dictionary(grouping: groups, by: \.version).mapValues(\.count)
    print("ACTIVE versions=\(versions.sorted { $0.key < $1.key })")
    for asset in catalog.package.assets where !FileManager.default.fileExists(atPath: asset.path) {
        failures += 1
        print("MISSING ASSET FILE \(asset.id)")
    }
    for purpose: ContentPurpose in [.training, .diagnostic, .battle, .mock] {
        let eligible = ContentEligibility.formalGroups(in: groups, for: purpose)
        print("ELIGIBLE \(purpose): groups=\(eligible.count) items=\(eligible.flatMap(\.items).count)")
    }
} catch {
    failures += 1
    print("CATALOG FAILED: \(error)")
}
print(failures == 0 ? "PROBE RESULT: all requested batches installed (producer reference only)" : "PROBE RESULT: \(failures) failure(s)")
exit(failures == 0 ? 0 : 1)
