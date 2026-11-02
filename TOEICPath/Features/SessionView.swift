import AVFoundation
import Combine
import SwiftUI
import UIKit

@MainActor
private final class PracticeAudioPlayer: ObservableObject {
    enum Status: Equatable { case idle, playing, failed(String) }
    struct PlaybackEnvironment: Equatable {
        let route: String
        let displayRoute: String
        let sampleRate: Double
    }
    @Published private(set) var status: Status = .idle
    @Published private(set) var completedFullPlayback = false
    @Published private(set) var lastPlaybackEnvironment: PlaybackEnvironment?
    private var player: AVAudioPlayer?
    private var stopTask: Task<Void, Never>?

    func play(url: URL, rate: Double, segment: AudioSegment? = nil) {
        stop()
        if segment == nil { completedFullPlayback = false }
        do {
            let session = AVAudioSession.sharedInstance()
            try session.setCategory(.playback, mode: .spokenAudio)
            try session.setActive(true)
            let outputs = session.currentRoute.outputs
            lastPlaybackEnvironment = .init(
                route: outputs.map { $0.portType.rawValue }.joined(separator: ","),
                displayRoute: outputs.map(Self.displayName(for:)).joined(separator: "、"),
                sampleRate: session.sampleRate
            )
            let player = try AVAudioPlayer(contentsOf: url)
            player.enableRate = rate != 1
            if player.enableRate { player.rate = Float(rate) }
            if let segment { player.currentTime = TimeInterval(segment.startMilliseconds) / 1_000 }
            player.prepareToPlay()
            guard player.play() else { throw PlaybackError.cannotStart }
            self.player = player
            status = .playing
            let sourceDurationMilliseconds = segment.map { max(1, $0.endMilliseconds - $0.startMilliseconds) }
                ?? max(1, Int(player.duration * 1_000))
            let playbackNanoseconds = UInt64(Double(sourceDurationMilliseconds) / max(rate, 0.1) * 1_000_000)
            let isFullPlayback = segment == nil
            stopTask = Task { @MainActor [weak self] in
                try? await Task.sleep(nanoseconds: playbackNanoseconds)
                guard !Task.isCancelled else { return }
                self?.finishPlayback(completedFull: isFullPlayback)
            }
        } catch {
            status = .failed(error.localizedDescription)
        }
    }

    func stop() {
        stopTask?.cancel()
        stopTask = nil
        player?.stop()
        player = nil
        status = .idle
    }

    func resetCompletion() { completedFullPlayback = false }

    private static func displayName(for output: AVAudioSessionPortDescription) -> String {
        switch output.portType {
        case .builtInSpeaker: "iPhone 喇叭"
        case .headphones, .headsetMic: "有線耳機"
        case .bluetoothA2DP, .bluetoothHFP, .bluetoothLE: "藍牙裝置"
        case .airPlay: "AirPlay"
        default: output.portName
        }
    }

    private func finishPlayback(completedFull: Bool) {
        stopTask = nil
        player?.stop()
        player = nil
        if completedFull { completedFullPlayback = true }
        status = .idle
    }

    private enum PlaybackError: LocalizedError {
        case cannotStart
        var errorDescription: String? { "音訊無法開始播放。" }
    }
}

enum SessionPresentationStyle {
    case standard
    case quickTest
}

struct SessionView: View {
    @EnvironmentObject private var model: AppModel
    @Environment(\.dismiss) private var dismiss
    @Environment(\.accessibilityVoiceOverEnabled) private var voiceOverEnabled
    @Environment(\.dynamicTypeSize) private var dynamicTypeSize
    @Environment(\.scenePhase) private var scenePhase
    let groups: [QuestionGroup]
    let mode: SessionMode
    let presentation: SessionPresentationStyle

    @State private var sessionGroups: [QuestionGroup]
    @State private var index = 0
    @State private var selections: [String: String] = [:]
    @State private var responses: [ItemResponse] = []
    @State private var submittedItemIDs = Set<String>()
    @State private var showTranscript = false
    @State private var showListeningTools = false
    @State private var transcriptUsed = false
    @State private var playbackRate = 1.0
    @State private var replayCount = 0
    @State private var hasPlayed = false
    @State private var sentenceModeUsed = false
    @State private var currentSegmentIndex = 0
    @State private var lastPlayedSegmentIndex: Int?
    @State private var interrupted = false
    @State private var appBackgrounded = false
    @State private var completedAudioGroupIDs = Set<String>()
    @State private var showExitConfirmation = false
    @State private var startedAt = Date.now
    @State private var sessionStartedAt = Date.now
    @State private var submittedAt: Date?
    @State private var didFinish = false
    @State private var didStartSession = false
    @State private var sessionStartError: String?
    @State private var recordedExposureKeys = Set<String>()
    @StateObject private var audioPlayer = PracticeAudioPlayer()

    init(
        groups: [QuestionGroup],
        mode: SessionMode,
        presentation: SessionPresentationStyle = .standard
    ) {
        self.groups = groups
        self.mode = mode
        self.presentation = presentation
        _sessionGroups = State(initialValue: groups)
    }

    private var entries: [(QuestionGroup, QuestionItem)] {
        sessionGroups.flatMap { group in group.items.map { (group, $0) } }
    }
    private var current: (QuestionGroup, QuestionItem)? { entries.indices.contains(index) ? entries[index] : nil }
    private var revealsImmediately: Bool {
        presentation != .quickTest && [.practice, .review].contains(mode)
    }
    private var nextPracticeGroup: QuestionGroup? {
        guard presentation == .standard, mode == .practice, let part = sessionGroups.first?.part else { return nil }
        return PartPracticeSelector.select(part: part, from: model.package.groups, profile: model.profile)
            .newGroups.first { candidate in
                !sessionGroups.contains(where: { $0.id == candidate.id })
                    && model.materialAvailability(for: candidate) == .complete
            }
    }

    var body: some View {
        NavigationStack {
            Group {
                if didFinish { completionView }
                else if let sessionStartError {
                    EmptyStateView(icon: "exclamationmark.triangle", title: "無法開始作答", message: sessionStartError)
                }
                else if let (group, item) = current { questionView(group: group, item: item) }
                else { EmptyStateView(icon: "tray", title: "沒有可作答題目", message: "請返回並更新題庫。") }
            }
            .background(AppTheme.warmBackground.ignoresSafeArea())
            .navigationTitle(modeTitle)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button(didFinish ? "完成" : "結束", systemImage: "xmark") {
                        if didFinish || sessionStartError != nil {
                            dismiss()
                        } else {
                            showExitConfirmation = true
                        }
                    }
                }
                if !didFinish {
                    ToolbarItem(placement: .principal) {
                        Text("\(index + 1) / \(entries.count)").font(.subheadline.monospacedDigit())
                    }
                }
            }
            .confirmationDialog("要結束這次作答嗎？", isPresented: $showExitConfirmation) {
                Button("結束且不保存", role: .destructive) { model.abortActiveSession(); dismiss() }
                Button("繼續作答", role: .cancel) { }
            }
        }
        .interactiveDismissDisabled(!didFinish && sessionStartError == nil)
        .onAppear {
            startSessionIfNeeded()
            recordCurrentExposureIfNeeded()
        }
        .onChange(of: index) { _, _ in recordCurrentExposureIfNeeded() }
        .onDisappear {
            audioPlayer.stop()
            if !didFinish { model.abortActiveSession() }
        }
        .onChange(of: scenePhase) { _, phase in
            if phase == .inactive || phase == .background {
                if audioPlayer.status == .playing { interrupted = true }
                if phase == .background { appBackgrounded = true }
                audioPlayer.stop()
            }
        }
    }

    private func questionView(group: QuestionGroup, item: QuestionItem) -> some View {
        let isSubmitted = submittedItemIDs.contains(item.id)
        return ScrollView {
            VStack(alignment: .leading, spacing: 18) {
                if presentation == .quickTest {
                    StatusPill(icon: group.part.symbol, text: "\(group.part.shortTitle)・\(group.part.title)", color: AppTheme.accent)
                } else {
                    StatusPill(icon: group.part.symbol, text: "\(group.part.shortTitle)・\(group.difficulty.label)", color: AppTheme.accent)
                }

                if group.part.section == .listening { listeningControls(group: group, item: item) }
                ForEach(group.documents) { document in
                    DocumentCard(document: document, itemIDs: group.items.map(\.id))
                }

                if let prompt = item.prompt, group.part.rawValue > 2 || isSubmitted {
                    Text(QuestionDisplayText.render(prompt, itemIDs: group.items.map(\.id)))
                        .font(.title3.bold()).textSelection(.enabled).readableCard()
                } else if group.part == .part1 {
                    photoView(item: item)
                }

                VStack(spacing: 10) {
                    ForEach(item.options) { option in
                        optionButton(
                            option, item: item, submitted: isSubmitted,
                            hidesText: group.part.rawValue <= 2 && !isSubmitted,
                            hiddenTextLabel: group.part == .part1 ? "音訊敘述" : "音訊回應"
                        )
                    }
                }

                if isSubmitted && revealsImmediately {
                    ExplanationView(item: item, selectedID: selections[item.id])
                }

                if presentation != .quickTest {
                    answerActionButton(group: group, item: item, isSubmitted: isSubmitted)
                }
            }
            .padding()
        }
        .safeAreaInset(edge: .bottom, spacing: 0) {
            if presentation == .quickTest {
                answerActionButton(group: group, item: item, isSubmitted: isSubmitted)
                    .padding(.horizontal)
                    .padding(.vertical, 10)
                    .background(.bar)
            }
        }
    }

    private func answerActionButton(
        group: QuestionGroup,
        item: QuestionItem,
        isSubmitted: Bool
    ) -> some View {
        Button {
            if isSubmitted || !revealsImmediately { advance() }
            else { submit(group: group, item: item) }
        } label: {
            Text(actionTitle(isSubmitted: isSubmitted))
                .frame(maxWidth: .infinity, minHeight: 50)
        }
        .buttonStyle(.borderedProminent)
        .controlSize(.large)
        .disabled(selections[item.id] == nil && !isSubmitted)
    }

    private func listeningControls(group: QuestionGroup, item: QuestionItem) -> some View {
        Group {
            if presentation == .quickTest {
                quickTestListeningControls(group: group, item: item)
            } else {
                standardListeningControls(group: group, item: item)
            }
        }
    }

    private func standardListeningControls(group: QuestionGroup, item: QuestionItem) -> some View {
        let audioURL = model.assetURL(for: item.audioAssetID ?? group.audioAssetID)
        let isSubmitted = submittedItemIDs.contains(item.id)
        let hidesStandardText = group.part.rawValue <= 2 && !isSubmitted
        let transcriptLocked = mode == .mockExam || mode == .battle || (mode == .diagnostic && !isSubmitted)
        return VStack(alignment: .leading, spacing: 12) {
            if hidesStandardText {
                Label(
                    group.part == .part1
                        ? "Part 1 標準作答不顯示敘述文字；四句音訊依序對應 A、B、C、D，送出後會顯示全文。"
                        : "Part 2 標準作答不顯示問句與回應文字；音訊先播放問句，再依序播放 A、B、C，送出後會顯示全文。",
                    systemImage: "ear"
                )
                .font(.subheadline).foregroundStyle(.secondary)
            }
            HStack {
                Button {
                    if hasPlayed { replayCount += 1 }
                    hasPlayed = true
                    if let audioURL { audioPlayer.play(url: audioURL, rate: playbackRate) }
                } label: { Label(hasPlayed ? "重播" : "播放", systemImage: "play.circle.fill") }
                    .buttonStyle(.bordered)
                    .disabled(audioURL == nil)
                Menu("\(playbackRate.formatted())×") {
                    Button("正常 1×") { playbackRate = 1 }
                    Button("慢速 0.8×") { playbackRate = 0.8 }
                }
                .disabled(audioURL == nil)
                Spacer()
                if item.transcript != nil {
                    Button(showTranscript ? "隱藏逐字稿" : "輔助逐字稿") {
                        showTranscript.toggle()
                        if showTranscript { transcriptUsed = true }
                    }
                    .disabled(transcriptLocked)
                }
            }
            if item.transcript != nil, transcriptLocked {
                Label("逐字稿在此模式的作答期間鎖定，避免改變標準測驗條件。", systemImage: "lock.fill")
                    .font(.caption).foregroundStyle(.secondary)
            } else if item.transcript != nil, hidesStandardText, !showTranscript {
                Text("練習時可開啟「輔助逐字稿」；開啟後仍可作答，但結果會與標準聽力分開記錄。")
                    .font(.caption).foregroundStyle(.secondary)
            }
            if let audioURL, !group.audioSegments.isEmpty {
                Button("播放下一段：\(segmentLabel(group: group, index: currentSegmentIndex))（\(currentSegmentIndex + 1)/\(group.audioSegments.count)）", systemImage: "text.line.first.and.arrowtriangle.forward") {
                    sentenceModeUsed = true
                    hasPlayed = true
                    let segment = group.audioSegments[currentSegmentIndex]
                    lastPlayedSegmentIndex = currentSegmentIndex
                    audioPlayer.play(url: audioURL, rate: playbackRate, segment: segment)
                    currentSegmentIndex = (currentSegmentIndex + 1) % group.audioSegments.count
                }
                .buttonStyle(.bordered)
                if let lastPlayedSegmentIndex {
                    Text("\(audioPlayer.status == .playing ? "正在播放" : "剛播放")：\(segmentLabel(group: group, index: lastPlayedSegmentIndex))")
                        .font(.caption).foregroundStyle(.secondary)
                }
            }
            if showTranscript, let transcript = item.transcript {
                Text(transcript).font(.body).textSelection(.enabled)
                Label("使用逐字稿的結果會與標準條件分開記錄", systemImage: "accessibility")
                    .font(.caption).foregroundStyle(.orange)
            } else if audioURL == nil {
                Label("音訊素材尚未下載，這題不能算標準聽力證據。", systemImage: "exclamationmark.triangle")
                    .font(.caption).foregroundStyle(.orange)
            } else {
                Text(audioStatusText).font(.caption).foregroundStyle(audioStatusIsFailure ? .red : .secondary)
            }
            if let environment = audioPlayer.lastPlaybackEnvironment {
                Label("輸出：\(environment.displayRoute)", systemImage: "speaker.wave.2")
                    .font(.caption).foregroundStyle(.secondary)
            }
        }
        .floatingSurface()
    }

    private func quickTestListeningControls(group: QuestionGroup, item: QuestionItem) -> some View {
        let audioURL = model.assetURL(for: item.audioAssetID ?? group.audioAssetID)
        let hidesStandardText = group.part.rawValue <= 2
        return VStack(alignment: .leading, spacing: 12) {
            if hidesStandardText {
                Label(
                    group.part == .part1
                        ? "音訊中的四個敘述依序對應畫面上的 A、B、C、D；交卷前不顯示文字。"
                        : "音訊會先播放問句，再依序播放 A、B、C；交卷前不顯示文字。",
                    systemImage: "ear"
                )
                .font(.subheadline)
                .foregroundStyle(.secondary)
            }

            Button {
                if hasPlayed { replayCount += 1 }
                hasPlayed = true
                if let audioURL { audioPlayer.play(url: audioURL, rate: playbackRate) }
            } label: {
                Label(hasPlayed ? "重新播放" : "播放音訊", systemImage: "play.circle.fill")
                    .frame(maxWidth: .infinity, minHeight: 48)
            }
            .buttonStyle(.borderedProminent)
            .disabled(audioURL == nil)

            if audioURL == nil {
                Label("音訊素材尚未就緒，這個題組不應進入快速測驗。", systemImage: "exclamationmark.triangle")
                    .font(.caption)
                    .foregroundStyle(.orange)
            } else {
                Text(audioStatusText)
                    .font(.caption)
                    .foregroundStyle(audioStatusIsFailure ? .red : .secondary)
            }

            DisclosureGroup("聽力工具", isExpanded: $showListeningTools) {
                VStack(alignment: .leading, spacing: 12) {
                    Menu("播放速度：\(playbackRate.formatted())×") {
                        Button("正常 1×") { playbackRate = 1 }
                        Button("慢速 0.8×") { playbackRate = 0.8 }
                    }

                    if let audioURL, !group.audioSegments.isEmpty {
                        Button(
                            "播放下一段：\(segmentLabel(group: group, index: currentSegmentIndex))",
                            systemImage: "text.line.first.and.arrowtriangle.forward"
                        ) {
                            sentenceModeUsed = true
                            hasPlayed = true
                            let segment = group.audioSegments[currentSegmentIndex]
                            lastPlayedSegmentIndex = currentSegmentIndex
                            audioPlayer.play(url: audioURL, rate: playbackRate, segment: segment)
                            currentSegmentIndex = (currentSegmentIndex + 1) % group.audioSegments.count
                        }
                        .buttonStyle(.bordered)
                    }

                    if item.transcript != nil {
                        Button(showTranscript ? "隱藏輔助文字" : "顯示輔助文字") {
                            showTranscript.toggle()
                            if showTranscript { transcriptUsed = true }
                        }
                        if hidesStandardText && !showTranscript {
                            Text("開啟後仍可作答，但結果會記為使用輔助，不列入標準聽力條件。")
                                .font(.caption)
                                .foregroundStyle(.secondary)
                        }
                    }

                    if showTranscript, let transcript = item.transcript {
                        Text(transcript)
                            .textSelection(.enabled)
                        Label("已使用文字輔助", systemImage: "accessibility")
                            .font(.caption)
                            .foregroundStyle(.orange)
                    }
                }
                .padding(.top, 8)
            }
        }
        .readableCard()
    }

    @ViewBuilder
    private func photoView(item: QuestionItem) -> some View {
        if let url = model.assetURL(for: item.imageAssetID), let image = UIImage(contentsOfFile: url.path) {
            Image(uiImage: image)
                .resizable().scaledToFit()
                .accessibilityLabel("Part 1 作答照片")
                .frame(maxWidth: .infinity).readableCard()
        } else {
            VStack(spacing: 14) {
                Image(systemName: "photo.badge.exclamationmark").font(.system(size: 40)).foregroundStyle(.secondary)
                Text("照片素材尚未下載").font(.headline)
                Text("缺少照片的作答不會算作標準條件證據。")
                    .font(.subheadline).foregroundStyle(.secondary)
            }
            .frame(maxWidth: .infinity).readableCard()
        }
    }

    private func optionButton(
        _ option: AnswerOption,
        item: QuestionItem,
        submitted: Bool,
        hidesText: Bool,
        hiddenTextLabel: String
    ) -> some View {
        let selected = selections[item.id] == option.id
        let correct = submitted && revealsImmediately && item.correctOptionID == option.id
        let wrong = submitted && revealsImmediately && selected && !correct
        let spokenResult = correct ? "，正確答案" : wrong ? "，你的答案，錯誤" : selected ? "，已選取" : ""
        return Button {
            guard !submitted else { return }
            selections[item.id] = option.id
        } label: {
            HStack(alignment: .top, spacing: 18) {
                Text(option.id).font(.headline).frame(width: 30, height: 30)
                    .background((correct ? Color.green : wrong ? Color.red : selected ? AppTheme.accent : .secondary).opacity(0.14), in: Circle())
                Text(hidesText ? hiddenTextLabel : option.text)
                    .multilineTextAlignment(.leading).frame(maxWidth: .infinity, alignment: .leading)
                if correct { Image(systemName: "checkmark.circle.fill").foregroundStyle(.green) }
                else if wrong { Image(systemName: "xmark.circle.fill").foregroundStyle(.red) }
            }
            .padding(14)
            .frame(minHeight: 52)
            .background(AppTheme.card, in: RoundedRectangle(cornerRadius: 14))
            .overlay { RoundedRectangle(cornerRadius: 14).stroke(selected ? AppTheme.accent : .clear, lineWidth: 2) }
        }
        .buttonStyle(.plain)
        .accessibilityLabel((hidesText ? "選項 \(option.id)" : "選項 \(option.id)，\(option.text)") + spokenResult)
        .accessibilityAddTraits(selected ? .isSelected : [])
    }

    private func submit(group: QuestionGroup, item: QuestionItem) {
        guard !didFinish, !submittedItemIDs.contains(item.id),
              let selected = selections[item.id], let session = model.activeSession else { return }
        let missingAudio = group.part.section == .listening && model.assetURL(for: item.audioAssetID ?? group.audioAssetID) == nil
        let missingImage = group.part == .part1 && model.assetURL(for: item.imageAssetID) == nil
        if audioPlayer.completedFullPlayback { completedAudioGroupIDs.insert(group.id) }
        let incompleteListeningExposure = group.part.section == .listening && !completedAudioGroupIDs.contains(group.id)
        let condition = AnswerCondition(
            playbackRate: playbackRate, replayCount: replayCount, transcriptShown: transcriptUsed,
            sentenceModeUsed: sentenceModeUsed, voiceOverRunning: voiceOverEnabled,
            interrupted: interrupted || missingAudio || missingImage || incompleteListeningExposure,
            appBackgrounded: appBackgrounded,
            audioOutputRoute: audioPlayer.lastPlaybackEnvironment?.route,
            audioSessionSampleRate: audioPlayer.lastPlaybackEnvironment?.sampleRate
        )
        responses.append(.init(
            id: UUID(), sessionID: session.id, groupID: group.id, groupVersion: group.version,
            sourceBatchID: group.sourceBatchID, itemID: item.id, part: group.part,
            difficulty: group.difficulty, familyID: group.familyID, selectedOptionID: selected,
            isCorrect: selected == item.correctOptionID, answeredAt: .now,
            elapsedMilliseconds: max(1, Int(Date.now.timeIntervalSince(startedAt) * 1000)), condition: condition
        ))
        submittedItemIDs.insert(item.id)
        if !revealsImmediately { advance() }
    }

    private func advance() {
        guard !didFinish, let (group, item) = current else { return }
        if !submittedItemIDs.contains(item.id) { submit(group: group, item: item); return }
        if index + 1 < entries.count {
            audioPlayer.stop()
            index += 1
            resetQuestionConditions()
        } else if mode == .diagnostic,
                  let selection = DiagnosticRouter.nextGroup(
                    from: model.package.groups,
                    selectedGroups: sessionGroups,
                    responses: responses,
                    exposedFamilyIDs: model.exposedFamilyIDs
                  ) {
            sessionGroups.append(selection.group)
            model.appendDiagnosticGroup(selection.group, reason: selection.reason)
            audioPlayer.stop()
            index += 1
            resetQuestionConditions()
        } else {
            let finishedAt = Date.now
            submittedAt = finishedAt
            model.finishSession(responses: responses)
            didFinish = true
        }
    }

    private func startSessionIfNeeded() {
        guard !didStartSession else { return }
        didStartSession = true
        do {
            try model.beginSession(groups: sessionGroups, mode: mode)
        } catch {
            sessionStartError = error.localizedDescription
        }
    }

    private func recordCurrentExposureIfNeeded() {
        guard sessionStartError == nil, let (group, item) = current else { return }
        let key = "\(group.id)#\(group.version)#\(item.id)"
        guard recordedExposureKeys.insert(key).inserted else { return }
        model.recordExposure(group: group, itemID: item.id, mode: mode)
    }

    private func resetQuestionConditions() {
        startedAt = .now
        showTranscript = false
        showListeningTools = false
        transcriptUsed = false
        playbackRate = 1
        replayCount = 0
        hasPlayed = false
        sentenceModeUsed = false
        currentSegmentIndex = 0
        lastPlayedSegmentIndex = nil
        interrupted = false
        appBackgrounded = false
        audioPlayer.resetCompletion()
    }

    private var audioStatusIsFailure: Bool {
        if case .failed = audioPlayer.status { true } else { false }
    }

    private var audioStatusText: String {
        switch audioPlayer.status {
        case .idle: "音訊已就緒"
        case .playing: "播放中"
        case .failed(let message): "音訊中斷：\(message)"
        }
    }

    private func segmentLabel(group: QuestionGroup, index: Int) -> String {
        switch group.part {
        case .part1:
            return "選項 \(String(UnicodeScalar(65 + index)!))"
        case .part2:
            return index == 0 ? "問句" : "選項 \(String(UnicodeScalar(64 + index)!))"
        default:
            return "第 \(index + 1) 句"
        }
    }

    private func actionTitle(isSubmitted: Bool) -> String {
        if presentation == .quickTest { return index + 1 == entries.count ? "交卷" : "下一題" }
        if !revealsImmediately { return index + 1 == entries.count ? "交卷" : "儲存並下一題" }
        if !isSubmitted { return "提交答案" }
        return index + 1 == entries.count ? "完成" : "下一題"
    }

    @ViewBuilder
    private var completionView: some View {
        if presentation == .quickTest {
            quickTestCompletionView
        } else {
            standardCompletionView
        }
    }

    private var standardCompletionView: some View {
        let diagnosticSummary = DiagnosticRouter.summary(selectedGroups: sessionGroups, responses: responses)
        return VStack(spacing: 18) {
            Image(systemName: "checkmark.circle.fill").font(.system(size: 58)).foregroundStyle(.green)
            Text("已完成").font(.largeTitle.bold())
            Text("答對 \(responses.filter(\.isCorrect).count) / \(responses.count) 題")
                .font(.title2)
            Text(mode == .diagnostic ? diagnosticSummary.message : "作答與輔助條件已保存在本機，連線後可同步。")
                .foregroundStyle(.secondary).multilineTextAlignment(.center)
            if mode == .diagnostic {
                HStack(spacing: 12) {
                    summaryMetric("\(diagnosticSummary.standardListeningItems)", "標準聽力")
                    summaryMetric("\(diagnosticSummary.standardReadingItems)", "標準閱讀")
                }
                if !diagnosticSummary.uncoveredParts.isEmpty {
                    Text("建議補測：\(diagnosticSummary.uncoveredParts.map(\.shortTitle).joined(separator: "、"))")
                        .font(.caption).foregroundStyle(.orange)
                }
            }
            if let nextPracticeGroup {
                Button("下一組") { startNextPracticeGroup(nextPracticeGroup) }
                    .buttonStyle(.borderedProminent).controlSize(.large)
            }
            Button(mode == .practice ? "返回練習列表" : "返回") { dismiss() }
                .buttonStyle(.bordered)
                .controlSize(.large)
        }
        .padding()
    }

    private var quickTestCompletionView: some View {
        let result = QuickTestScoring.result(
            responses: responses,
            expectedItemCount: entries.count,
            startedAt: sessionStartedAt,
            submittedAt: submittedAt
        )
        return ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                VStack(spacing: 12) {
                    Image(systemName: "checkmark.circle.fill")
                        .font(.system(size: 54))
                        .foregroundStyle(.green)
                    Text("測驗完成")
                        .font(.largeTitle.bold())
                    Text("這是練習短測，不換算多益分數。")
                        .foregroundStyle(.secondary)
                }
                .frame(maxWidth: .infinity)

                if let result {
                    Group {
                        if dynamicTypeSize.isAccessibilitySize {
                            VStack(spacing: 10) {
                                summaryMetric("\(result.correctCount)/\(result.totalCount)", "答對")
                                summaryMetric("\(Int((result.accuracy * 100).rounded()))%", "正確率")
                                summaryMetric(formattedDuration(result.elapsedSeconds), "用時")
                            }
                        } else {
                            HStack(spacing: 10) {
                                summaryMetric("\(result.correctCount)/\(result.totalCount)", "答對")
                                summaryMetric("\(Int((result.accuracy * 100).rounded()))%", "正確率")
                                summaryMetric(formattedDuration(result.elapsedSeconds), "用時")
                            }
                        }
                    }
                }

                Text("逐題回顧")
                    .font(.title2.bold())

                ForEach(Array(entries.enumerated()), id: \.element.1.id) { offset, entry in
                    quickTestReviewCard(number: offset + 1, group: entry.0, item: entry.1)
                }

                Button("完成") { dismiss() }
                    .buttonStyle(.borderedProminent)
                    .controlSize(.large)
                    .frame(maxWidth: .infinity)
            }
            .padding()
        }
    }

    private func quickTestReviewCard(number: Int, group: QuestionGroup, item: QuestionItem) -> some View {
        let selectedID = selections[item.id]
        let isCorrect = selectedID == item.correctOptionID
        return VStack(alignment: .leading, spacing: 12) {
            HStack(alignment: .firstTextBaseline) {
                Text("第 \(number) 題・\(group.part.shortTitle)")
                    .font(.headline)
                Spacer()
                Label(isCorrect ? "答對" : "答錯", systemImage: isCorrect ? "checkmark.circle.fill" : "xmark.circle.fill")
                    .font(.subheadline.weight(.semibold))
                    .foregroundStyle(isCorrect ? .green : .red)
            }
            if let prompt = item.prompt {
                Text(QuestionDisplayText.render(prompt, itemIDs: group.items.map(\.id)))
                    .font(.body.weight(.semibold))
            }
            ForEach(item.options) { option in
                let isAnswer = option.id == item.correctOptionID
                let wasSelected = option.id == selectedID
                HStack(alignment: .top, spacing: 10) {
                    Image(systemName: isAnswer ? "checkmark.circle.fill" : wasSelected ? "xmark.circle.fill" : "circle")
                        .foregroundStyle(isAnswer ? .green : wasSelected ? .red : .secondary)
                    HStack(alignment: .top, spacing: 18) {
                        Text(option.id)
                            .font(.headline)
                            .frame(width: 30, alignment: .center)
                        Text(option.text)
                            .frame(maxWidth: .infinity, alignment: .leading)
                    }
                }
            }
            ExplanationView(item: item, selectedID: selectedID)
        }
        .readableCard()
    }

    private func formattedDuration(_ seconds: Int) -> String {
        if seconds < 60 { return "\(seconds)秒" }
        return "\(seconds / 60):\(String(format: "%02d", seconds % 60))"
    }

    private func startNextPracticeGroup(_ group: QuestionGroup) {
        audioPlayer.stop()
        sessionGroups = [group]
        index = 0
        selections = [:]
        responses = []
        submittedItemIDs = []
        completedAudioGroupIDs = []
        recordedExposureKeys = []
        sessionStartError = nil
        didStartSession = false
        didFinish = false
        resetQuestionConditions()
        startSessionIfNeeded()
        recordCurrentExposureIfNeeded()
    }

    private var modeTitle: String {
        if presentation == .quickTest { return "快速測驗" }
        return switch mode {
        case .practice: "練習"
        case .diagnostic: "診斷"
        case .mockExam: "模考"
        case .review: "複習"
        case .battle: "對戰"
        }
    }

    private func summaryMetric(_ value: String, _ label: String) -> some View {
        VStack(spacing: 4) {
            Text(value).font(.title2.bold()).monospacedDigit()
            Text(label).font(.caption).foregroundStyle(.secondary)
        }
        .frame(maxWidth: .infinity)
        .readableCard()
    }
}

private struct DocumentCard: View {
    let document: StimulusDocument
    let itemIDs: [String]
    @State private var scrollOffset = 0.0
    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            if let title = document.title { Text(title).font(.headline) }
            Text(QuestionDisplayText.render(document.body, itemIDs: itemIDs)).textSelection(.enabled).lineSpacing(5)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .readableCard()
        .accessibilityElement(children: .combine)
        .accessibilityLabel(QuestionDisplayText.render(document.accessibilityLabel ?? document.body, itemIDs: itemIDs))
    }
}

private struct ExplanationView: View {
    let item: QuestionItem
    let selectedID: String?
    @State private var expanded = false
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Label("正解證據", systemImage: "quote.opening").font(.headline).foregroundStyle(.green)
            Text(item.explanation.evidence)
            Text(item.explanation.zhTW).foregroundStyle(.secondary)
            DisclosureGroup("其他解析、翻譯與單字", isExpanded: $expanded) {
                VStack(alignment: .leading, spacing: 10) {
                    if let translation = item.explanation.translation { Text(translation) }
                    ForEach(item.explanation.vocabulary) { word in
                        Text("\(word.term)：\(word.meaning)")
                    }
                    if item.explanation.vocabulary.isEmpty && item.explanation.translation == nil {
                        Text("這題目前沒有額外內容。" ).foregroundStyle(.secondary)
                    }
                }.padding(.top, 8)
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .readableCard()
    }
}
