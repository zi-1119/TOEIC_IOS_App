import CryptoKit
import XCTest
@testable import TOEICPath

final class AudioPreviewCatalogTests: XCTestCase {
    func testCatalogHasFiveCompletePairsAndCandidateIsNeverFormal() throws {
        XCTAssertEqual(AudioPreviewCatalog.samples.count, 5)
        XCTAssertEqual(AudioPreviewCatalog.samples.flatMap(\.variants).count, 10)
        XCTAssertEqual(Set(AudioPreviewCatalog.samples.map(\.groupID)).count, 5)
        XCTAssertEqual(Set(AudioPreviewCatalog.samples.flatMap(\.variants).map(\.fileName)).count, 10)

        for (index, sample) in AudioPreviewCatalog.samples.enumerated() {
            XCTAssertEqual(sample.number, index + 1)
            XCTAssertEqual(sample.original.kind, .original)
            XCTAssertEqual(sample.original.marker, "A")
            XCTAssertEqual(sample.candidate.kind, .candidate)
            XCTAssertEqual(sample.candidate.marker, "B")
            XCTAssertEqual(sample.variants.count, 2)
        }
    }

    func testPreviewCopiesMatchDeclaredHashesAndImmutableSourceBytes() throws {
        let root = URL(fileURLWithPath: #filePath)
            .deletingLastPathComponent()
            .deletingLastPathComponent()
        let copiedRoot = root.appending(path: AudioPreviewCatalog.resourceName, directoryHint: .isDirectory)
        let sourceRoot = root.appending(path: "assets_work/audio-listening-pack-2026-10-31", directoryHint: .isDirectory)

        for variant in AudioPreviewCatalog.samples.flatMap(\.variants) {
            let copied = try Data(contentsOf: copiedRoot.appending(path: variant.fileName))
            let source = try Data(contentsOf: sourceRoot.appending(path: variant.fileName))
            XCTAssertEqual(copied, source, "Preview copy changed: \(variant.fileName)")
            XCTAssertEqual(sha256(copied), variant.sha256, "Hash mismatch: \(variant.fileName)")
        }
    }

    func testPreviewResourcesStayOutsideFormalSeedContent() throws {
        let root = URL(fileURLWithPath: #filePath)
            .deletingLastPathComponent()
            .deletingLastPathComponent()
        let seedRoot = root.appending(path: "SeedContent", directoryHint: .isDirectory)

        for variant in AudioPreviewCatalog.samples.flatMap(\.variants) {
            XCTAssertFalse(
                FileManager.default.fileExists(atPath: seedRoot.appending(path: variant.fileName).path),
                "Preview candidate must not enter formal SeedContent"
            )
        }
    }

    private func sha256(_ data: Data) -> String {
        SHA256.hash(data: data).map { String(format: "%02x", $0) }.joined()
    }
}
