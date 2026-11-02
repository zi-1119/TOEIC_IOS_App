import Foundation

enum ContentEligibility {
    static func hasApprovedMetadata(_ group: QuestionGroup, for purpose: ContentPurpose) -> Bool {
        group.purpose == purpose
            && group.fixture == false
            && group.contentStatus?.isApprovedForFormalUse == true
    }

    static func isFormallyEligible(_ group: QuestionGroup, for purpose: ContentPurpose) -> Bool {
        hasApprovedMetadata(group, for: purpose)
            && hasRequiredMaterialReferences(group)
            && !group.items.isEmpty
    }

    static func formalGroups(in groups: [QuestionGroup], for purpose: ContentPurpose) -> [QuestionGroup] {
        groups.filter { isFormallyEligible($0, for: purpose) }
    }

    static func hasRequiredMaterialReferences(_ group: QuestionGroup) -> Bool {
        guard group.part.section == .listening else { return true }
        guard group.audioAssetID != nil || group.items.allSatisfy({ $0.audioAssetID != nil }) else { return false }
        if group.part == .part1 {
            return group.items.allSatisfy { $0.imageAssetID != nil }
        }
        return true
    }
}

struct PartPracticeSelection: Hashable, Sendable {
    let newGroups: [QuestionGroup]
    let reviewGroups: [QuestionGroup]
}

enum PartPracticeSelector {
    static func select(part: TOEICPart, from groups: [QuestionGroup], profile: LocalProfile) -> PartPracticeSelection {
        let candidates = ContentEligibility.formalGroups(in: groups, for: .training)
            .filter { $0.part == part }
            .sorted(by: stableOrder)
        let exposedFamilies = Set(profile.exposures.values.flatMap(\.familyIDs))
        return PartPracticeSelection(
            newGroups: candidates.filter { !exposedFamilies.contains($0.familyID) },
            reviewGroups: candidates.filter { exposedFamilies.contains($0.familyID) }
        )
    }

    private static func stableOrder(_ lhs: QuestionGroup, _ rhs: QuestionGroup) -> Bool {
        if lhs.difficulty == rhs.difficulty { return lhs.id < rhs.id }
        return lhs.difficulty < rhs.difficulty
    }
}

struct QuickTestAssembly: Hashable, Sendable {
    let groups: [QuestionGroup]
    let targetItemCount: Int
    let reviewGroupIDs: Set<String>

    var actualItemCount: Int { groups.flatMap(\.items).count }
    var isExactTarget: Bool { actualItemCount == targetItemCount }
    var containsReview: Bool { !reviewGroupIDs.isEmpty }
}

enum QuickTestAssembler {
    static func assemble(
        from groups: [QuestionGroup],
        focus: QuickTestFocus,
        level: QuickTestLevel,
        profile: LocalProfile,
        materialCompleteGroupIDs: Set<String>,
        targetItemCount: Int = 10
    ) -> QuickTestAssembly {
        guard targetItemCount > 0 else {
            return .init(groups: [], targetItemCount: targetItemCount, reviewGroupIDs: [])
        }

        let exposedFamilies = Set(profile.exposures.values.flatMap(\.familyIDs))
        let eligible = ContentEligibility.formalGroups(in: groups, for: .training)
            .filter { materialCompleteGroupIDs.contains($0.id) }
            .filter { group in
                switch focus {
                case .reading: group.part.section == .reading
                case .listening: group.part.section == .listening
                case .mixed: true
                }
            }
            .filter { !$0.items.isEmpty && $0.items.count <= targetItemCount }

        // Active catalogs normally contain one version per family. Keep the best
        // candidate if synthetic or future catalogs temporarily expose more than one.
        let candidates = Dictionary(grouping: eligible, by: \.familyID)
            .values
            .compactMap { familyGroups in
                familyGroups.min { lhs, rhs in
                    candidateComesFirst(lhs, rhs, level: level, exposedFamilies: exposedFamilies)
                }
            }
            .sorted { lhs, rhs in
                candidateComesFirst(lhs, rhs, level: level, exposedFamilies: exposedFamilies)
            }

        var bestByCount: [Int: [QuestionGroup]] = [0: []]
        for candidate in candidates {
            let snapshot = bestByCount
            for (subtotal, selection) in snapshot {
                let nextCount = subtotal + candidate.items.count
                guard nextCount <= targetItemCount else { continue }
                let proposed = selection + [candidate]
                if let existing = bestByCount[nextCount] {
                    if isBetter(proposed, than: existing, level: level, exposedFamilies: exposedFamilies) {
                        bestByCount[nextCount] = proposed
                    }
                } else {
                    bestByCount[nextCount] = proposed
                }
            }
        }

        let actualCount = bestByCount.keys.max() ?? 0
        let selected = (bestByCount[actualCount] ?? []).sorted { lhs, rhs in
            if lhs.part == rhs.part { return lhs.id < rhs.id }
            return lhs.part.rawValue < rhs.part.rawValue
        }
        let reviewIDs = Set(selected.filter { exposedFamilies.contains($0.familyID) }.map(\.id))
        return .init(groups: selected, targetItemCount: targetItemCount, reviewGroupIDs: reviewIDs)
    }

    private static func candidateComesFirst(
        _ lhs: QuestionGroup,
        _ rhs: QuestionGroup,
        level: QuickTestLevel,
        exposedFamilies: Set<String>
    ) -> Bool {
        let lhsSeen = exposedFamilies.contains(lhs.familyID)
        let rhsSeen = exposedFamilies.contains(rhs.familyID)
        if lhsSeen != rhsSeen { return !lhsSeen }
        let lhsDistance = abs(lhs.difficulty.rawValue - level.targetDifficulty.rawValue)
        let rhsDistance = abs(rhs.difficulty.rawValue - level.targetDifficulty.rawValue)
        if lhsDistance != rhsDistance { return lhsDistance < rhsDistance }
        if lhs.part != rhs.part { return lhs.part.rawValue < rhs.part.rawValue }
        return lhs.id < rhs.id
    }

    private static func isBetter(
        _ lhs: [QuestionGroup],
        than rhs: [QuestionGroup],
        level: QuickTestLevel,
        exposedFamilies: Set<String>
    ) -> Bool {
        let lhsNew = lhs.filter { !exposedFamilies.contains($0.familyID) }.count
        let rhsNew = rhs.filter { !exposedFamilies.contains($0.familyID) }.count
        if lhsNew != rhsNew { return lhsNew > rhsNew }

        let lhsPartCoverage = Set(lhs.map(\.part)).count
        let rhsPartCoverage = Set(rhs.map(\.part)).count
        if lhsPartCoverage != rhsPartCoverage { return lhsPartCoverage > rhsPartCoverage }

        let lhsSectionCoverage = Set(lhs.map { $0.part.section }).count
        let rhsSectionCoverage = Set(rhs.map { $0.part.section }).count
        if lhsSectionCoverage != rhsSectionCoverage { return lhsSectionCoverage > rhsSectionCoverage }

        let lhsDistance = lhs.reduce(0) { $0 + abs($1.difficulty.rawValue - level.targetDifficulty.rawValue) }
        let rhsDistance = rhs.reduce(0) { $0 + abs($1.difficulty.rawValue - level.targetDifficulty.rawValue) }
        if lhsDistance != rhsDistance { return lhsDistance < rhsDistance }

        return lhs.map(\.id).joined(separator: "|") < rhs.map(\.id).joined(separator: "|")
    }
}

struct QuickTestResult: Hashable, Sendable {
    let correctCount: Int
    let totalCount: Int
    let elapsedSeconds: Int
    let incorrectItemIDs: [String]

    var accuracy: Double {
        guard totalCount > 0 else { return 0 }
        return Double(correctCount) / Double(totalCount)
    }
}

enum QuickTestScoring {
    static func result(
        responses: [ItemResponse],
        expectedItemCount: Int,
        startedAt: Date,
        submittedAt: Date?
    ) -> QuickTestResult? {
        guard let submittedAt, responses.count == expectedItemCount else { return nil }
        return .init(
            correctCount: responses.filter(\.isCorrect).count,
            totalCount: expectedItemCount,
            elapsedSeconds: max(0, Int(submittedAt.timeIntervalSince(startedAt))),
            incorrectItemIDs: responses.filter { !$0.isCorrect }.map(\.itemID)
        )
    }
}

struct DiagnosticRule: Codable, Hashable, Sendable {
    let version: String
    var promoteAccuracy = 0.80
    var demoteAccuracy = 0.40
    var minimumIndependentGroups = 2
    var minimumShortFormItems = 6
    var targetMinimumItems = 40
    var targetMaximumItems = 60

    static let initial = DiagnosticRule(version: "diagnostic-rule-1.0")
}

struct DiagnosticDecision: Hashable, Sendable {
    enum Action: String, Sendable { case promote, hold, demote, insufficientEvidence }
    let action: Action
    let nextDifficulty: Difficulty
    let reason: String
    let ruleVersion: String
}

enum DiagnosticEngine {
    static func decide(
        current: Difficulty,
        responses: [ItemResponse],
        shortForm: Bool,
        rule: DiagnosticRule = .initial
    ) -> DiagnosticDecision {
        let matching = responses.filter { $0.difficulty == current && $0.condition.isStandard }
        let independentGroups = Set(matching.map(\.groupID)).count
        let minimumItems = shortForm ? rule.minimumShortFormItems : rule.minimumIndependentGroups
        let enough = shortForm
            ? matching.count >= minimumItems && independentGroups >= rule.minimumIndependentGroups
            : independentGroups >= rule.minimumIndependentGroups
        guard enough, !matching.isEmpty else {
            return .init(action: .insufficientEvidence, nextDifficulty: current, reason: "同難度的獨立題組或標準作答量仍不足，先保持等級並補測。", ruleVersion: rule.version)
        }

        let accuracy = Double(matching.filter(\.isCorrect).count) / Double(matching.count)
        if accuracy > rule.promoteAccuracy, let next = Difficulty(rawValue: current.rawValue + 1) {
            return .init(action: .promote, nextDifficulty: next, reason: "同難度穩定證據的正確率高於試用升級門檻，下一組試升至 \(next.label)。", ruleVersion: rule.version)
        }
        if accuracy < rule.demoteAccuracy, let next = Difficulty(rawValue: current.rawValue - 1) {
            return .init(action: .demote, nextDifficulty: next, reason: "同難度穩定證據的正確率低於試用降級門檻，下一組降至 \(next.label) 補強。", ruleVersion: rule.version)
        }
        return .init(action: .hold, nextDifficulty: current, reason: "現有證據落在保持區間，繼續收集同級不同題組。", ruleVersion: rule.version)
    }
}

struct DiagnosticSelection: Hashable, Sendable {
    let group: QuestionGroup
    let reason: String
    let decision: DiagnosticDecision
}

struct DiagnosticSummary: Hashable, Sendable {
    let totalItems: Int
    let standardListeningItems: Int
    let standardReadingItems: Int
    let uncoveredParts: [TOEICPart]
    let hasTargetEvidence: Bool
    let message: String
}

enum DiagnosticRouter {
    static let minimumItemsByPart: [TOEICPart: Int] = [
        .part1: 3, .part2: 6, .part3: 6, .part4: 6,
        .part5: 6, .part6: 4, .part7: 4
    ]

    static func nextGroup(
        from bank: [QuestionGroup],
        selectedGroups: [QuestionGroup],
        responses: [ItemResponse],
        exposedFamilyIDs: Set<String> = [],
        rule: DiagnosticRule = .initial
    ) -> DiagnosticSelection? {
        let currentItemCount = selectedGroups.flatMap(\.items).count
        guard currentItemCount < rule.targetMaximumItems else { return nil }

        let source = ContentEligibility.formalGroups(in: bank, for: .diagnostic)
        let usedGroupIDs = Set(selectedGroups.map(\.id))
        let usedFamilies = Set(selectedGroups.map(\.familyID))
        let candidates = source.filter {
            !usedGroupIDs.contains($0.id)
                && !usedFamilies.contains($0.familyID)
                && !exposedFamilyIDs.contains($0.familyID)
                && currentItemCount + $0.items.count <= rule.targetMaximumItems
        }
        guard !candidates.isEmpty else { return nil }

        let selectedItemCounts = Dictionary(grouping: selectedGroups, by: \.part).mapValues { $0.flatMap(\.items).count }
        let sectionCounts = Dictionary(grouping: selectedGroups, by: { $0.part.section }).mapValues { $0.flatMap(\.items).count }
        let targetSection: TOEICSection = sectionCounts[.listening, default: 0] <= sectionCounts[.reading, default: 0] ? .listening : .reading
        let sectionParts = TOEICPart.allCases.filter { $0.section == targetSection }
        let targetPart = sectionParts.max { lhs, rhs in
            let leftDeficit = max(0, minimumItemsByPart[lhs, default: 1] - selectedItemCounts[lhs, default: 0])
            let rightDeficit = max(0, minimumItemsByPart[rhs, default: 1] - selectedItemCounts[rhs, default: 0])
            if leftDeficit == rightDeficit { return selectedItemCounts[lhs, default: 0] > selectedItemCounts[rhs, default: 0] }
            return leftDeficit < rightDeficit
        } ?? sectionParts[0]

        let currentDifficulty = selectedGroups.last(where: { $0.part.section == targetSection })?.difficulty ?? .d2
        let sectionResponses = responses.filter { $0.part.section == targetSection }
        let decision = DiagnosticEngine.decide(current: currentDifficulty, responses: sectionResponses, shortForm: true, rule: rule)
        let desiredDifficulty = decision.nextDifficulty
        let partCandidates = candidates.filter { $0.part == targetPart }
        let sectionCandidates = candidates.filter { $0.part.section == targetSection }
        let selectionPool = !partCandidates.isEmpty ? partCandidates : !sectionCandidates.isEmpty ? sectionCandidates : candidates
        guard let selected = selectionPool.min(by: { lhs, rhs in
            let leftDistance = abs(lhs.difficulty.rawValue - desiredDifficulty.rawValue)
            let rightDistance = abs(rhs.difficulty.rawValue - desiredDifficulty.rawValue)
            if leftDistance == rightDistance {
                if lhs.part == rhs.part { return lhs.id < rhs.id }
                return lhs.part.rawValue < rhs.part.rawValue
            }
            return leftDistance < rightDistance
        }) else { return nil }

        let coverageReason = selected.part == targetPart
            ? "補足 \(targetPart.shortTitle) 的完整題組覆蓋。"
            : "\(targetPart.shortTitle) 題庫不足，改以同區段的 \(selected.part.shortTitle) 補充證據。"
        let difficultyReason = selected.difficulty == desiredDifficulty
            ? decision.reason
            : "目標為 \(desiredDifficulty.label)，可用題庫最近為 \(selected.difficulty.label)。"
        return DiagnosticSelection(group: selected, reason: "\(coverageReason) \(difficultyReason)", decision: decision)
    }

    static func summary(selectedGroups: [QuestionGroup], responses: [ItemResponse], rule: DiagnosticRule = .initial) -> DiagnosticSummary {
        let partCounts = Dictionary(grouping: selectedGroups, by: \.part).mapValues { $0.flatMap(\.items).count }
        let uncovered = TOEICPart.allCases.filter { partCounts[$0, default: 0] < minimumItemsByPart[$0, default: 1] }
        let standard = responses.filter(\.condition.isStandard)
        let listening = standard.filter { $0.part.section == .listening }.count
        let reading = standard.filter { $0.part.section == .reading }.count
        let total = responses.count
        let enough = total >= rule.targetMinimumItems && uncovered.isEmpty && listening > 0 && reading > 0
        let message: String
        if enough {
            message = "已完成目前規則要求的題量與 Part 覆蓋；結果仍是待試用調整的產品分級。"
        } else if selectedGroups.flatMap(\.items).count < rule.targetMinimumItems {
            message = "題庫或題組覆蓋不足，尚未達到 \(rule.targetMinimumItems) 題的初始證據目標，建議補測。"
        } else {
            message = "題數已達目標，但部分 Part 或標準作答條件的證據仍不足。"
        }
        return .init(totalItems: total, standardListeningItems: listening, standardReadingItems: reading,
                     uncoveredParts: uncovered, hasTargetEvidence: enough, message: message)
    }
}

struct MockExamBlueprint: Hashable, Sendable {
    let counts: [TOEICPart: Int]
    let readingTimeLimitSeconds: Int
    let listeningExpectedSeconds: Int

    static let standard = MockExamBlueprint(
        counts: [.part1: 6, .part2: 25, .part3: 39, .part4: 30, .part5: 30, .part6: 16, .part7: 54],
        readingTimeLimitSeconds: 75 * 60,
        listeningExpectedSeconds: 45 * 60
    )
    var totalItems: Int { counts.values.reduce(0, +) }
}

struct MockExamAssembly: Hashable, Sendable {
    let groups: [QuestionGroup]
    let shortages: [TOEICPart: Int]
    var isReady: Bool { shortages.isEmpty && groups.flatMap(\.items).count == MockExamBlueprint.standard.totalItems }
}

enum MockExamEngine {
    static func assemble(from groups: [QuestionGroup], blueprint: MockExamBlueprint = .standard) -> MockExamAssembly {
        let mockGroups = ContentEligibility.formalGroups(in: groups, for: .mock)
        var selected: [QuestionGroup] = []
        var shortages: [TOEICPart: Int] = [:]
        for part in TOEICPart.allCases {
            let needed = blueprint.counts[part, default: 0]
            let partSelection = exactOrBestSelection(from: mockGroups.filter { $0.part == part }, target: needed)
            selected.append(contentsOf: partSelection)
            let total = partSelection.flatMap(\.items).count
            if total < needed { shortages[part] = needed - total }
        }
        return MockExamAssembly(groups: selected, shortages: shortages)
    }

    private static func exactOrBestSelection(from groups: [QuestionGroup], target: Int) -> [QuestionGroup] {
        guard target > 0 else { return [] }
        let familyChoices = Dictionary(grouping: groups, by: \.familyID)
            .values
            .map { $0.sorted(by: stableOrder) }
            .sorted { ($0.first?.familyID ?? "") < ($1.first?.familyID ?? "") }
        var solutions: [Int: [QuestionGroup]] = [0: []]
        for choices in familyChoices {
            let snapshot = solutions
            for (subtotal, selection) in snapshot {
                for group in choices where subtotal + group.items.count <= target {
                    let next = subtotal + group.items.count
                    if solutions[next] == nil { solutions[next] = selection + [group] }
                }
            }
            if solutions[target] != nil { return solutions[target]! }
        }
        let best = solutions.keys.max() ?? 0
        return solutions[best] ?? []
    }

    private static func stableOrder(_ lhs: QuestionGroup, _ rhs: QuestionGroup) -> Bool {
        if lhs.difficulty == rhs.difficulty { return lhs.id < rhs.id }
        return lhs.difficulty < rhs.difficulty
    }
}

enum ReviewScheduler {
    private static let successIntervalsDays = [1, 3, 7, 21, 45, 90]

    static func updatedState(for response: ItemResponse, previous: ReviewState?, now: Date = .now) -> ReviewState {
        let prior = previous ?? ReviewState(
            itemID: response.itemID, repetitions: 0, masteryEvidence: 0,
            lastFamilyID: nil, lastReviewedAt: now, nextReviewAt: now
        )
        if response.isCorrect {
            let repetitions = min(prior.repetitions + 1, successIntervalsDays.count)
            let interval = successIntervalsDays[max(0, repetitions - 1)]
            let transferEvidence = response.condition.isStandard && prior.lastFamilyID != response.familyID ? 1 : 0
            return ReviewState(
                itemID: response.itemID, repetitions: repetitions,
                masteryEvidence: prior.masteryEvidence + transferEvidence,
                lastFamilyID: response.familyID, lastReviewedAt: now,
                nextReviewAt: Calendar(identifier: .gregorian).date(byAdding: .day, value: interval, to: now) ?? now
            )
        }
        return ReviewState(
            itemID: response.itemID, repetitions: 0, masteryEvidence: prior.masteryEvidence,
            lastFamilyID: response.familyID, lastReviewedAt: now,
            nextReviewAt: Calendar(identifier: .gregorian).date(byAdding: .day, value: 1, to: now) ?? now
        )
    }
}

struct DailyPlan: Hashable, Sendable {
    let groups: [QuestionGroup]
    let reasons: [String: String]
    let estimatedMinutes: Int
}

enum DailyPlanner {
    static func makePlan(
        groups: [QuestionGroup],
        profile: LocalProfile,
        now: Date = .now
    ) -> DailyPlan {
        let budget = max(10, profile.preferences.dailyMinutes)
        let responses = profile.sessions.flatMap(\.responses)
        let seenFamilies = Set(profile.exposures.values.flatMap(\.familyIDs))
        let dueItems = Set(profile.reviewStates.values.filter { $0.nextReviewAt <= now }.map(\.itemID))

        let partAccuracy: [TOEICPart: Double] = Dictionary(uniqueKeysWithValues: TOEICPart.allCases.map { part in
            let partResponses = responses.filter { $0.part == part && $0.condition.isStandard }
            let accuracy = partResponses.isEmpty ? 1 : Double(partResponses.filter(\.isCorrect).count) / Double(partResponses.count)
            return (part, accuracy)
        })

        var candidates: [(QuestionGroup, Int, String)] = ContentEligibility.formalGroups(in: groups, for: .training).map { group in
            if group.items.contains(where: { dueItems.contains($0.id) }) {
                return (group, 0, "到期複習：先鞏固曾答錯或已到間隔的題目。")
            }
            if partAccuracy[group.part, default: 1] < 0.7 {
                return (group, 1, "弱點補強：這個 Part 的標準首答表現較弱。")
            }
            if !seenFamilies.contains(group.familyID) {
                return (group, 2, "新情境：避免只記住原題。")
            }
            return (group, group.difficulty >= .d4 ? 3 : 4, group.difficulty >= .d4 ? "適量挑戰：保留合理高難度題。" : "維持手感：完整題組練習。")
        }
        candidates.sort { lhs, rhs in lhs.1 == rhs.1 ? lhs.0.id < rhs.0.id : lhs.1 < rhs.1 }

        var selected: [QuestionGroup] = []
        var selectedFamilies = Set<String>()
        var reasons: [String: String] = [:]
        var minutes = 0
        for (group, _, reason) in candidates {
            guard selectedFamilies.insert(group.familyID).inserted else { continue }
            let estimate = estimatedMinutes(for: group)
            if !selected.isEmpty && minutes + estimate > budget { continue }
            selected.append(group)
            reasons[group.id] = reason
            minutes += estimate
            if minutes >= budget { break }
        }
        return DailyPlan(groups: selected, reasons: reasons, estimatedMinutes: minutes)
    }

    private static func estimatedMinutes(for group: QuestionGroup) -> Int {
        let perItem = group.part.section == .listening ? 1.2 : group.part == .part7 ? 2.2 : 1.3
        return max(2, Int(ceil(Double(group.items.count) * perItem)))
    }
}
