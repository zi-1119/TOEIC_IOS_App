import Foundation

struct AudioPreviewVariant: Identifiable, Equatable, Sendable {
    enum Kind: String, Sendable {
        case original
        case candidate
    }

    let kind: Kind
    let fileName: String
    let sha256: String

    var id: String { fileName }
    var marker: String { kind == .original ? "A" : "B" }
    var title: String { kind == .original ? "目前原音" : "候選音訊" }
    var detail: String { kind == .original ? "既有版本" : "Karen、念出選項標號、短間隔" }
}

struct AudioPreviewSample: Identifiable, Equatable, Sendable {
    let number: Int
    let groupID: String
    let part: Int
    let title: String
    let note: String
    let original: AudioPreviewVariant
    let candidate: AudioPreviewVariant

    var id: String { groupID }
    var variants: [AudioPreviewVariant] { [original, candidate] }
}

enum AudioPreviewCatalog {
    static let resourceName = "AudioPreview"

    static let samples: [AudioPreviewSample] = [
        sample(
            1, "ag-g-p1-000001", part: 1,
            title: "研究室顯微鏡",
            note: "原音曾回報較混濁，適合先比較清晰度。",
            originalFile: "01-ag-g-p1-000001-A-original.m4a",
            originalSHA256: "684cd4b76474d8dc727975321314eac90c070a2b720a0274f908a82453ebbef9",
            candidateFile: "01-ag-g-p1-000001-B-karen-labels-400ms.m4a",
            candidateSHA256: "8a639bb87401ceb9cc4dd33aacafd997c28a9cf1931f678585eb27e9a1967afe"
        ),
        sample(
            2, "ag-g-p1-000002", part: 1,
            title: "麵包店",
            note: "比較原本英式聲線與候選 Karen 聲線。",
            originalFile: "02-ag-g-p1-000002-A-original.m4a",
            originalSHA256: "08b0874cf58aa9763625ad82b8f4490c219a50d7dcfb8b435f66e402e8cadcde",
            candidateFile: "02-ag-g-p1-000002-B-karen-labels-400ms.m4a",
            candidateSHA256: "b37e752a6c360c46fa373418e68564ebf532aaeb21aad0d00ed0bc4f2f300127"
        ),
        sample(
            3, "ag-g-p1-000003", part: 1,
            title: "Karen 清晰度基準",
            note: "原音已是 Karen；候選只增加標號與短間隔。",
            originalFile: "03-ag-g-p1-000003-A-original.m4a",
            originalSHA256: "5f92a455908bf43b0ee0b6cee6205d275a5ab027577fdc0cfd973d62acbbfade",
            candidateFile: "03-ag-g-p1-000003-B-karen-labels-400ms.m4a",
            candidateSHA256: "44f46c136209bed4daadc1d5705570d38502ab519691291d69ad3bbbdb4d8098"
        ),
        sample(
            4, "ag-g-p2-000004", part: 2,
            title: "問句與三個回應",
            note: "題目句不加標號，只為三個回應加入 A–C。",
            originalFile: "04-ag-g-p2-000004-A-original.m4a",
            originalSHA256: "eb30fe79d8abb0bab1ec6627e51e14ddff30da26289761589c51a08a98bc0848",
            candidateFile: "04-ag-g-p2-000004-B-karen-labels-400ms.m4a",
            candidateSHA256: "512b5f6e441b72d4fae9ff2ad11b4dee6dccb8a315aecfdea4268a840931d9bf"
        ),
        sample(
            5, "ag-g-p2-000002", part: 2,
            title: "雙聲線問答",
            note: "問句維持原聲線，候選回應改用 Karen 並加 A–C。",
            originalFile: "05-ag-g-p2-000002-A-original.m4a",
            originalSHA256: "6cd520ed297f651af8551f17e564f1706de00d70d6cea63a76e6c015bb07dbf6",
            candidateFile: "05-ag-g-p2-000002-B-karen-labels-400ms.m4a",
            candidateSHA256: "382faa974433036b76c568d04bf390fc4e53246d7b8a990ababee521a6fab9cc"
        )
    ]

    static func resourceRootURL(in bundle: Bundle = .main) -> URL? {
        bundle.url(forResource: resourceName, withExtension: nil)
    }

    static func url(
        for variant: AudioPreviewVariant,
        in bundle: Bundle = .main,
        fileManager: FileManager = .default
    ) -> URL? {
        guard let root = resourceRootURL(in: bundle) else { return nil }
        let url = root.appending(path: variant.fileName)
        return fileManager.fileExists(atPath: url.path) ? url : nil
    }

    private static func sample(
        _ number: Int,
        _ groupID: String,
        part: Int,
        title: String,
        note: String,
        originalFile: String,
        originalSHA256: String,
        candidateFile: String,
        candidateSHA256: String
    ) -> AudioPreviewSample {
        AudioPreviewSample(
            number: number,
            groupID: groupID,
            part: part,
            title: title,
            note: note,
            original: AudioPreviewVariant(kind: .original, fileName: originalFile, sha256: originalSHA256),
            candidate: AudioPreviewVariant(kind: .candidate, fileName: candidateFile, sha256: candidateSHA256)
        )
    }
}
