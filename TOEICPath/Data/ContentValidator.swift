import Foundation

struct ValidationIssue: Identifiable, Hashable, Sendable {
    enum Severity: String, Hashable, Sendable { case error, warning }
    let severity: Severity
    let path: String
    let message: String
    var id: String { "\(severity.rawValue):\(path):\(message)" }
}

struct ContentValidationReport: Hashable, Sendable {
    let issues: [ValidationIssue]
    var errors: [ValidationIssue] { issues.filter { $0.severity == .error } }
    var warnings: [ValidationIssue] { issues.filter { $0.severity == .warning } }
    var isImportable: Bool { errors.isEmpty }
}

enum ContentValidator {
    static let supportedSchemaVersions = Set([1])

    static func validate(_ package: ContentPackage) -> ContentValidationReport {
        var issues: [ValidationIssue] = []
        let manifest = package.manifest

        if !supportedSchemaVersions.contains(manifest.schemaVersion) {
            issues.append(.init(severity: .error, path: "manifest.schemaVersion", message: "不支援的 schema 版本 \(manifest.schemaVersion)"))
        }
        if manifest.locale != "en" {
            issues.append(.init(severity: .warning, path: "manifest.locale", message: "題目語系預期為 en"))
        }
        if manifest.packageID.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty || manifest.contentVersion.isEmpty {
            issues.append(.init(severity: .error, path: "manifest", message: "packageID 與 contentVersion 不可為空"))
        }

        let assetIDs = package.assets.map(\.id)
        appendDuplicates(assetIDs, at: "assets", to: &issues)
        let knownAssets = Set(assetIDs)
        let groupIDs = package.groups.map(\.id)
        appendDuplicates(groupIDs, at: "groups", to: &issues)

        for (groupIndex, group) in package.groups.enumerated() {
            let groupPath = "groups[\(groupIndex)]"
            if group.familyID.isEmpty {
                issues.append(.init(severity: .error, path: "\(groupPath).familyID", message: "題組必須有家族 ID 供去重"))
            }
            if group.items.isEmpty {
                issues.append(.init(severity: .error, path: "\(groupPath).items", message: "題組不可為空"))
            }
            appendDuplicates(group.items.map(\.id), at: "\(groupPath).items", to: &issues)
            validateGroupShape(group, path: groupPath, issues: &issues)

            if let asset = group.audioAssetID, !knownAssets.contains(asset) {
                issues.append(.init(severity: .error, path: "\(groupPath).audioAssetID", message: "找不到音訊素材 \(asset)"))
            }

            for (itemIndex, item) in group.items.enumerated() {
                let itemPath = "\(groupPath).items[\(itemIndex)]"
                let optionIDs = item.options.map(\.id)
                appendDuplicates(optionIDs, at: "\(itemPath).options", to: &issues)
                if !Set(optionIDs).contains(item.correctOptionID) {
                    issues.append(.init(severity: .error, path: "\(itemPath).correctOptionID", message: "正解不在選項中"))
                }
                if item.options.count < 3 || item.options.count > 4 {
                    issues.append(.init(severity: .error, path: "\(itemPath).options", message: "選項數須為 3 或 4"))
                }
                if item.explanation.evidence.isEmpty || item.explanation.zhTW.isEmpty {
                    issues.append(.init(severity: .error, path: "\(itemPath).explanation", message: "必須提供正解證據與繁中詳解"))
                }
                for asset in [item.imageAssetID, item.audioAssetID].compactMap({ $0 }) where !knownAssets.contains(asset) {
                    issues.append(.init(severity: .error, path: itemPath, message: "找不到素材 \(asset)"))
                }
            }
        }

        for part in TOEICPart.allCases where !package.groups.contains(where: { $0.part == part }) {
            issues.append(.init(severity: .warning, path: "groups", message: "題庫尚未涵蓋 \(part.shortTitle)"))
        }
        return ContentValidationReport(issues: issues)
    }

    private static func validateGroupShape(_ group: QuestionGroup, path: String, issues: inout [ValidationIssue]) {
        switch group.part {
        case .part1, .part2:
            if group.items.count != 1 {
                issues.append(.init(severity: .error, path: path, message: "\(group.part.shortTitle) 每組必須恰好一題"))
            }
        case .part3, .part4:
            if group.items.count != 3 {
                issues.append(.init(severity: .error, path: path, message: "\(group.part.shortTitle) 每個音訊題組必須三題"))
            }
        case .part5:
            if group.items.count != 1 {
                issues.append(.init(severity: .error, path: path, message: "Part 5 每組必須恰好一題"))
            }
        case .part6:
            if group.items.count != 4 {
                issues.append(.init(severity: .error, path: path, message: "Part 6 每篇必須四題"))
            }
        case .part7:
            if group.items.count < 2 || group.items.count > 5 {
                issues.append(.init(severity: .error, path: path, message: "Part 7 題組應包含二至五題"))
            }
            if group.documents.isEmpty {
                issues.append(.init(severity: .error, path: "\(path).documents", message: "Part 7 必須有閱讀文件"))
            }
        }
    }

    private static func appendDuplicates(_ values: [String], at path: String, to issues: inout [ValidationIssue]) {
        var seen = Set<String>()
        for value in values where !seen.insert(value).inserted {
            issues.append(.init(severity: .error, path: path, message: "重複 ID：\(value)"))
        }
    }
}

