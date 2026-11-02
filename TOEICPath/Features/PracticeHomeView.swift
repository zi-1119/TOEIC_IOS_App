import SwiftUI

struct PracticeHomeView: View {
    @EnvironmentObject private var model: AppModel
    @State private var route: PracticeRoute?

    enum PracticeRoute: Identifiable {
        case diagnostic, part(TOEICPart), mock, mistakes
        var id: String {
            switch self {
            case .diagnostic: "diagnostic"
            case .part(let part): "part-\(part.rawValue)"
            case .mock: "mock"
            case .mistakes: "mistakes"
            }
        }
    }

    var body: some View {
        NavigationStack {
            List {
                Section {
                    Button { route = .diagnostic } label: {
                        practiceRow(icon: "scope", title: "自適應診斷", subtitle: "聽力、閱讀分開找能力邊界")
                    }
                    Button { route = .mock } label: {
                        practiceRow(icon: "timer", title: "完整模考", subtitle: "200 題・固定規格與作答時間")
                    }
                    Button { route = .mistakes } label: {
                        practiceRow(
                            icon: "bookmark",
                            title: "錯題本",
                            subtitle: "\(Set(model.profile.dueItemIDs).count) 題已保存・\(model.dueReviewCount) 題到期"
                        )
                    }
                }

                Section("Part 1–7") {
                    ForEach(TOEICPart.allCases) { part in
                        let groups = model.package.groups.filter {
                            $0.part == part && ContentEligibility.hasApprovedMetadata($0, for: .training)
                        }
                        let completeItems = groups.filter { model.materialAvailability(for: $0) == .complete }.flatMap(\.items).count
                        let previewItems = groups.flatMap(\.items).count - completeItems
                        Button {
                            route = .part(part)
                        } label: {
                            HStack(spacing: 14) {
                                Image(systemName: part.symbol)
                                    .frame(width: 30)
                                    .foregroundStyle(AppTheme.accent)
                                VStack(alignment: .leading, spacing: 3) {
                                    Text("\(part.shortTitle)  \(part.title)").font(.headline)
                                    Text(groups.isEmpty ? "題庫尚未下載" : availabilityText(complete: completeItems, preview: previewItems))
                                        .font(.subheadline).foregroundStyle(.secondary)
                                }
                                Spacer()
                                Image(systemName: groups.isEmpty ? "exclamationmark.circle" : "chevron.right")
                                    .foregroundStyle(.tertiary)
                            }
                            .contentShape(Rectangle())
                            .frame(minHeight: 48)
                        }
                        .disabled(groups.isEmpty)
                    }
                }

                Section("目前題庫") {
                    LabeledContent("版本", value: model.package.manifest.contentVersion)
                    LabeledContent("共同啟用批次", value: "\(model.activeBatchCount)")
                    LabeledContent("題組", value: "\(model.package.groups.count)")
                    LabeledContent("題目", value: "\(model.package.groups.flatMap(\.items).count)")
                    LabeledContent("驗證", value: model.validationReport.isImportable ? "可匯入" : "有錯誤")
                }
            }
            .navigationTitle("練習")
            .sheet(item: $route) { route in
                switch route {
                case .diagnostic:
                    DiagnosticIntroView()
                case .part(let part):
                    PartPracticePickerView(part: part)
                case .mock:
                    MockExamIntroView()
                case .mistakes:
                    MistakesView()
                }
            }
        }
    }

    private func practiceRow(icon: String, title: String, subtitle: String) -> some View {
        HStack(spacing: 14) {
            Image(systemName: icon).font(.title2).foregroundStyle(AppTheme.accent).frame(width: 32)
            VStack(alignment: .leading, spacing: 4) {
                Text(title).font(.headline).foregroundStyle(.primary)
                Text(subtitle).font(.subheadline).foregroundStyle(.secondary)
            }
            Spacer()
            Image(systemName: "chevron.right").foregroundStyle(.tertiary)
        }
        .frame(minHeight: 52)
    }

    private func availabilityText(complete: Int, preview: Int) -> String {
        if preview == 0 { return "\(complete) 題可完整練習" }
        if complete == 0 { return "\(preview) 題素材預覽；不列標準聽力" }
        return "\(complete) 題完整・\(preview) 題素材預覽"
    }
}

struct PartPracticePickerView: View {
    @EnvironmentObject private var model: AppModel
    @Environment(\.dismiss) private var dismiss
    let part: TOEICPart
    @State private var selectedGroup: QuestionGroup?

    private var selection: PartPracticeSelection {
        PartPracticeSelector.select(part: part, from: model.package.groups, profile: model.profile)
    }
    private var newGroups: [QuestionGroup] {
        selection.newGroups.filter { model.materialAvailability(for: $0) == .complete }
    }
    private var reviewGroups: [QuestionGroup] {
        selection.reviewGroups.filter { model.materialAvailability(for: $0) == .complete }
    }
    private var previewGroups: [QuestionGroup] {
        model.package.groups.filter {
            $0.part == part
                && ContentEligibility.hasApprovedMetadata($0, for: .training)
                && model.materialAvailability(for: $0) != .complete
        }
    }

    var body: some View {
        NavigationStack {
            Group {
                if let selectedGroup {
                    SessionView(groups: [selectedGroup], mode: .practice)
                } else if newGroups.isEmpty && reviewGroups.isEmpty && previewGroups.isEmpty {
                    EmptyStateView(icon: "tray", title: "沒有可用的 \(part.shortTitle) 題組", message: "正式練習只會使用 training 用途、非 fixture 且已通過內容狀態的完整題組。")
                } else {
                    List {
                        if !newGroups.isEmpty {
                            Section("未練過的完整題組") {
                                ForEach(newGroups) { group in groupButton(group, label: "新題組") }
                            }
                        }
                        if !reviewGroups.isEmpty {
                            Section("手動複習") {
                                ForEach(reviewGroups) { group in groupButton(group, label: "已看過") }
                            }
                        }
                        if !previewGroups.isEmpty {
                            Section("素材預覽（不計正式作答）") {
                                ForEach(previewGroups) { group in
                                    HStack {
                                        groupLabel(group, status: "不可作答")
                                        Spacer()
                                        Image(systemName: "exclamationmark.triangle").foregroundStyle(.orange)
                                    }
                                }
                            }
                        }
                    }
                    .navigationTitle("\(part.shortTitle) \(part.title)")
                    .toolbar { ToolbarItem(placement: .cancellationAction) { Button("關閉") { dismiss() } } }
                }
            }
        }
    }

    private func groupButton(_ group: QuestionGroup, label: String) -> some View {
        Button { selectedGroup = group } label: {
            HStack {
                groupLabel(group, status: label)
                Spacer()
                Image(systemName: "chevron.right").foregroundStyle(.tertiary)
            }
            .contentShape(Rectangle())
            .frame(minHeight: 48)
        }
    }

    private func groupLabel(_ group: QuestionGroup, status: String) -> some View {
        VStack(alignment: .leading, spacing: 3) {
            Text("\(group.difficulty.label)・\(group.scenario)").font(.headline).foregroundStyle(.primary)
            Text("\(group.items.count) 題・\(status)").font(.subheadline).foregroundStyle(.secondary)
        }
    }
}

struct DiagnosticIntroView: View {
    @EnvironmentObject private var model: AppModel
    @Environment(\.dismiss) private var dismiss
    @State private var started = false

    private var diagnosticBank: [QuestionGroup] {
        ContentEligibility.formalGroups(in: model.package.groups, for: .diagnostic)
            .filter { model.materialAvailability(for: $0) == .complete }
    }
    private var firstSelection: DiagnosticSelection? {
        DiagnosticRouter.nextGroup(
            from: diagnosticBank,
            selectedGroups: [],
            responses: [],
            exposedFamilyIDs: model.exposedFamilyIDs
        )
    }

    var body: some View {
        if started {
            SessionView(groups: firstSelection.map { [$0.group] } ?? [], mode: .diagnostic)
        } else {
            NavigationStack {
                ScrollView {
                    VStack(alignment: .leading, spacing: 20) {
                        Image(systemName: "scope").font(.system(size: 42)).foregroundStyle(AppTheme.accent)
                        Text("先找能力邊界").font(.largeTitle.bold())
                        Text("診斷會分開觀察聽力與閱讀，並以完整題組逐步調整難度。已提交、且已用來選下一組的答案不能回改；交卷後才顯示解析。")
                            .font(.title3).foregroundStyle(.secondary)
                        VStack(alignment: .leading, spacing: 10) {
                            Label("目標 40–60 小題，可能為了完整題組略作調整", systemImage: "list.number")
                            Label("題庫不足時會顯示證據不足，不猜測能力", systemImage: "exclamationmark.triangle")
                            Label("這是可調整的產品規則，不是心理計量校準", systemImage: "slider.horizontal.3")
                        }
                        .readableCard()
                        if diagnosticBank.flatMap(\.items).count < DiagnosticRule.initial.targetMinimumItems {
                            Label("診斷用途池目前只有 \(diagnosticBank.flatMap(\.items).count) 題；不會借用 training、battle 或 mock 題組。題庫不足時結果會標示證據不足。", systemImage: "info.circle")
                                .foregroundStyle(.orange)
                        }
                        Button {
                            guard firstSelection != nil else { return }
                            started = true
                        } label: {
                            Text("開始診斷").frame(maxWidth: .infinity, minHeight: 50)
                        }
                        .buttonStyle(.borderedProminent)
                        .controlSize(.large)
                        .disabled(firstSelection == nil)
                    }
                    .padding()
                }
                .background(AppTheme.warmBackground)
                .toolbar { ToolbarItem(placement: .cancellationAction) { Button("關閉") { dismiss() } } }
            }
        }
    }
}

struct MockExamIntroView: View {
    @EnvironmentObject private var model: AppModel
    @Environment(\.dismiss) private var dismiss
    @State private var running = false
    @State private var errorMessage: String?
    private var assembly: MockExamAssembly { MockExamEngine.assemble(from: model.package.groups) }
    private var activeRuntime: MockExamRuntime? { model.profile.activeMockExam }
    private var selectedForm: MockExamForm? { activeRuntime?.form ?? model.mockExamForm }
    private var runtimeGroups: [QuestionGroup] {
        guard let form = selectedForm else { return assembly.groups }
        let exact = model.mockGroups(for: form)
        if !exact.isEmpty { return exact }
        let byID = Dictionary(uniqueKeysWithValues: model.package.groups.map { ($0.id, $0) })
        return form.orderedGroupIDs.compactMap { byID[$0] }
    }
    private var audioURL: URL? { selectedForm.flatMap(model.mockAudioURL(for:)) }
    private var selectedFormIssues: [String] {
        guard let form = selectedForm else { return ["尚未提供正式模考表單"] }
        var issues = form.validationIssues() + form.contentValidationIssues(groups: model.package.groups)
        if runtimeGroups.count != form.orderedGroupIDs.count { issues.append("找不到模考指定的精確題組版本") }
        if let expected = form.audioTimelineChecksumSHA256,
           let assetID = form.audioTimelineAssetIDs.first,
           model.package.assets.first(where: { $0.id == assetID })?.checksumSHA256?.lowercased() != expected.lowercased() {
            issues.append("模考固定時間線素材雜湊與表單不一致")
        }
        return issues
    }

    var body: some View {
        if running, let runtime = activeRuntime {
            MockExamRunnerView(runtime: runtime, groups: runtimeGroups, audioURL: audioURL)
        } else { NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 20) {
                    Text("完整模考").font(.largeTitle.bold())
                    Text("聽力 100 題，播放時間約 45 分鐘；閱讀 100 題，限時 75 分鐘。作答時不逐題揭曉答案，區段內可回看改答。")
                        .foregroundStyle(.secondary)
                    HStack { metric("200", "總題數"); metric("45", "聽力分鐘"); metric("75", "閱讀分鐘") }
                    if activeRuntime != nil {
                        VStack(alignment: .leading, spacing: 10) {
                            Label("有一份未完成模考", systemImage: "arrow.clockwise.circle.fill").font(.headline).foregroundStyle(AppTheme.accent)
                            Text("截止時間保留原值；重新開啟不會重設時限。")
                                .foregroundStyle(.secondary)
                            if selectedFormIssues.isEmpty, activeRuntime?.phase != .listening || audioURL != nil {
                                Button("繼續模考") { running = true }.buttonStyle(.borderedProminent)
                            } else {
                                blocker(
                                    title: "這份模考目前無法安全續跑",
                                    details: selectedFormIssues + (audioURL == nil && activeRuntime?.phase == .listening
                                        ? ["固定播放時間線素材遺失；原截止時間仍保留，請先恢復相同題庫版本與素材。"] : [])
                                )
                            }
                            Button("捨棄這份模考", role: .destructive) { model.clearMockExam() }.buttonStyle(.bordered)
                        }.readableCard()
                    } else if let form = model.mockExamForm {
                        let formIssues = selectedFormIssues
                        if !formIssues.isEmpty {
                            blocker(title: "模考表單未通過驗證", details: formIssues)
                        } else if audioURL == nil {
                            blocker(title: "固定播放素材尚未就緒", details: ["表單存在，但 App 找不到已驗證的完整時間線音檔；不會用估計秒數假裝聽力可用。"])
                        } else {
                            Label("題目、固定時間線與時限齊全，可以開始", systemImage: "checkmark.circle.fill").foregroundStyle(.green)
                            Button("開始模考") {
                                do { try model.startMockExam(form: form); running = true }
                                catch { errorMessage = error.localizedDescription }
                            }
                            .buttonStyle(.borderedProminent)
                        }
                    } else if assembly.isReady {
                        blocker(
                            title: "題數齊全，但缺少正式組卷與播放時間線",
                            details: ["App 已支援解析 reports/mock-forms.json 增補格式；目前啟用批次尚未提供通過驗證的正式表單與整卷音檔，不會自行平均分配 45 分鐘。"]
                        )
                    } else {
                        VStack(alignment: .leading, spacing: 8) {
                            Label("題庫不足，暫時不能開始完整模考", systemImage: "tray.and.arrow.down")
                                .font(.headline)
                            ForEach(TOEICPart.allCases) { part in
                                if let count = assembly.shortages[part] { Text("\(part.shortTitle) 尚缺 \(count) 題") }
                            }
                            Text("匯入通過驗證的完整題庫包後會自動解鎖。")
                                .foregroundStyle(.secondary)
                        }
                        .readableCard()
                        Button("先做分項練習") {
                            model.selectedTab = 1
                            dismiss()
                        }
                        .buttonStyle(.borderedProminent)
                        .frame(maxWidth: .infinity, minHeight: 48)
                    }
                }
                .padding()
            }
            .background(AppTheme.warmBackground)
            .toolbar { ToolbarItem(placement: .cancellationAction) { Button("關閉") { dismiss() } } }
            .alert("無法開始模考", isPresented: Binding(get: { errorMessage != nil }, set: { if !$0 { errorMessage = nil } })) {
                Button("好") { errorMessage = nil }
            } message: { Text(errorMessage ?? "") }
        } }
    }

    private func metric(_ value: String, _ label: String) -> some View {
        VStack { Text(value).font(.title.bold()); Text(label).font(.caption).foregroundStyle(.secondary) }
            .frame(maxWidth: .infinity).readableCard()
    }

    private func blocker(title: String, details: [String]) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            Label(title, systemImage: "exclamationmark.triangle").font(.headline).foregroundStyle(.orange)
            ForEach(details, id: \.self) { Text($0).font(.subheadline).foregroundStyle(.secondary) }
        }.readableCard()
    }
}

struct MistakesView: View {
    @EnvironmentObject private var model: AppModel
    @Environment(\.dismiss) private var dismiss
    @State private var selectedGroups: [QuestionGroup]?
    private var dueIDs: Set<String> {
        Set(model.profile.reviewStates.values.filter { $0.nextReviewAt <= .now }.map(\.itemID))
    }
    private var mistakeIDs: Set<String> { Set(model.profile.dueItemIDs) }
    private var mistakeGroups: [QuestionGroup] {
        ContentEligibility.formalGroups(in: model.package.groups, for: .training).filter { group in
            model.materialAvailability(for: group) == .complete && group.items.contains { mistakeIDs.contains($0.id) }
        }
    }
    private var dueGroups: [QuestionGroup] {
        mistakeGroups.filter { group in
            group.items.contains { dueIDs.contains($0.id) }
        }
    }
    var body: some View {
        if let selectedGroups {
            SessionView(groups: selectedGroups, mode: .review)
        } else { NavigationStack {
            Group {
                if mistakeGroups.isEmpty {
                    EmptyStateView(icon: "checkmark.circle", title: "目前沒有錯題", message: "完成練習後，答錯的題目會保存在這裡，並依排程提醒複習。")
                } else {
                    List {
                        Section {
                            ForEach(TOEICPart.allCases.filter { part in
                                mistakeGroups.contains { $0.part == part }
                            }) { part in
                                let partGroups = mistakeGroups.filter { $0.part == part }
                                let savedCount = Set(partGroups.flatMap(\.items).filter { mistakeIDs.contains($0.id) }.map(\.id)).count
                                let dueCount = Set(partGroups.flatMap(\.items).filter { dueIDs.contains($0.id) }.map(\.id)).count
                                VStack(alignment: .leading, spacing: 4) {
                                    Label("\(part.shortTitle)・\(part.title)・\(savedCount) 題", systemImage: part.symbol)
                                    Text(dueCount > 0 ? "\(dueCount) 題已到期" : "已保存，尚未到複習時間")
                                        .font(.caption)
                                        .foregroundStyle(dueCount > 0 ? .orange : .secondary)
                                }
                            }
                        }
                        Section {
                            Text("重做會保留完整題組，因此實際作答可能包含同題組的其他題目。")
                                .font(.caption)
                                .foregroundStyle(.secondary)
                            if !dueGroups.isEmpty {
                                Button("開始到期複習") { selectedGroups = dueGroups }
                                    .buttonStyle(.borderedProminent)
                            }
                            if dueGroups.isEmpty {
                                Button("重做錯題（完整題組 \(mistakeGroups.flatMap(\.items).count) 題）") { selectedGroups = mistakeGroups }
                                    .buttonStyle(.borderedProminent)
                            } else {
                                Button("重做錯題（完整題組 \(mistakeGroups.flatMap(\.items).count) 題）") { selectedGroups = mistakeGroups }
                                    .buttonStyle(.bordered)
                            }
                        }
                    }
                }
            }
            .navigationTitle("錯題本")
            .toolbar { ToolbarItem(placement: .cancellationAction) { Button("關閉") { dismiss() } } }
        } }
    }
}
