import AVFoundation
import Combine
import SwiftUI
import UIKit

@MainActor
private final class MockExamAudioPlayer: ObservableObject {
    enum Status: Equatable { case idle, playing, failed(String) }
    @Published private(set) var status: Status = .idle
    private var player: AVPlayer?

    func play(url: URL, elapsedSeconds: TimeInterval) {
        do {
            let session = AVAudioSession.sharedInstance()
            try session.setCategory(.playback, mode: .spokenAudio)
            try session.setActive(true)
            let player = AVPlayer(url: url)
            self.player = player
            player.seek(to: CMTime(seconds: max(0, elapsedSeconds), preferredTimescale: 1_000), toleranceBefore: .zero, toleranceAfter: .zero)
            player.play()
            status = .playing
        } catch {
            status = .failed(error.localizedDescription)
        }
    }

    func stop() {
        player?.pause()
        player = nil
        status = .idle
    }
}

struct MockExamRunnerView: View {
    @EnvironmentObject private var model: AppModel
    @Environment(\.dismiss) private var dismiss
    @Environment(\.scenePhase) private var scenePhase
    @Environment(\.accessibilityVoiceOverEnabled) private var voiceOverEnabled

    let groups: [QuestionGroup]
    let audioURL: URL?
    @State private var runtime: MockExamRuntime
    @StateObject private var audioPlayer = MockExamAudioPlayer()
    @State private var showGrid = false
    @State private var showSubmitConfirmation = false
    @State private var errorMessage: String?
    @State private var finalized = false
    private let timer = Timer.publish(every: 1, on: .main, in: .common).autoconnect()

    init(runtime: MockExamRuntime, groups: [QuestionGroup], audioURL: URL?) {
        self.groups = groups
        self.audioURL = audioURL
        _runtime = State(initialValue: runtime)
    }

    private var entries: [(QuestionGroup, QuestionItem)] {
        groups.flatMap { group in group.items.map { (group, $0) } }
    }

    private var currentEntry: (QuestionGroup, QuestionItem)? {
        guard let id = runtime.currentItemID else { return nil }
        return entries.first { $0.1.id == id }
    }

    var body: some View {
        NavigationStack {
            Group {
                switch runtime.phase {
                case .listening, .reading: activeSection
                case .sectionBreak: sectionBreak
                case .expired: expiredView
                case .submitted: submittedView
                case .notStarted: EmptyStateView(icon: "exclamationmark.triangle", title: "模考尚未開始", message: "請返回並重新開始。")
                }
            }
            .background(AppTheme.warmBackground.ignoresSafeArea())
            .navigationTitle(runtime.phase == .listening ? "聽力測驗" : runtime.phase == .reading ? "閱讀測驗" : "完整模考")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                if runtime.phase == .listening || runtime.phase == .reading {
                    ToolbarItem(placement: .topBarLeading) {
                        Button("題目導覽", systemImage: "square.grid.3x3") { showGrid = true }
                    }
                    ToolbarItem(placement: .topBarTrailing) {
                        Text(remainingText).font(.subheadline.monospacedDigit()).accessibilityLabel("剩餘時間 \(remainingText)")
                    }
                }
            }
            .sheet(isPresented: $showGrid) { answerGrid }
            .confirmationDialog("確定交卷？", isPresented: $showSubmitConfirmation) {
                Button("交卷", role: .destructive) { submit() }
                Button("繼續作答", role: .cancel) { }
            } message: {
                Text("未作答題目會以錯誤計算；交卷後不能修改。")
            }
            .alert("模考狀態", isPresented: Binding(get: { errorMessage != nil }, set: { if !$0 { errorMessage = nil } })) {
                Button("好") { errorMessage = nil }
            } message: { Text(errorMessage ?? "") }
        }
        .interactiveDismissDisabled(runtime.phase != .submitted)
        .onAppear { resumeTimelineIfNeeded() }
        .onDisappear {
            audioPlayer.stop()
            if !finalized { model.saveMockExam(runtime) }
        }
        .onReceive(timer) { tick($0) }
        .onChange(of: scenePhase) { _, phase in handleScenePhase(phase) }
    }

    private var activeSection: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 18) {
                HStack {
                    StatusPill(
                        icon: runtime.phase == .listening ? "waveform" : "book",
                        text: runtime.phase == .listening ? "固定播放時間線" : "75 分鐘",
                        color: AppTheme.accent
                    )
                    Spacer()
                    Text(progressText).font(.caption).foregroundStyle(.secondary)
                }

                if runtime.phase == .listening {
                    HStack(spacing: 10) {
                        Image(systemName: audioStatusIcon)
                        Text(audioStatusText).font(.subheadline)
                    }
                    .foregroundStyle(audioStatusIsFailure ? .red : .secondary)
                    .floatingSurface()
                }

                if let (group, item) = currentEntry {
                    ForEach(group.documents) { document in
                        VStack(alignment: .leading, spacing: 8) {
                            if let title = document.title { Text(title).font(.headline) }
                            Text(document.body).textSelection(.enabled).lineSpacing(5)
                        }
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .readableCard()
                    }
                    if let prompt = item.prompt, group.part.rawValue > 2 {
                        Text(prompt).font(.title3.bold()).frame(maxWidth: .infinity, alignment: .leading).readableCard()
                    } else if group.part == .part1 {
                        mockPhoto(item: item)
                    }
                    VStack(spacing: 10) {
                        ForEach(item.options) { option in
                            mockOption(option, item: item, hidesText: group.part.rawValue <= 2)
                        }
                    }
                    navigationControls
                } else {
                    ProgressView("等待聽力時間線進入下一題…")
                        .frame(maxWidth: .infinity, minHeight: 220)
                }
            }
            .padding()
        }
    }

    private func mockOption(_ option: AnswerOption, item: QuestionItem, hidesText: Bool) -> some View {
        let selected = runtime.selectedOptionIDs[item.id] == option.id
        return Button {
            do {
                try runtime.select(
                    optionID: option.id, for: item.id,
                    condition: AnswerCondition(voiceOverRunning: voiceOverEnabled), now: .now
                )
                model.saveMockExam(runtime)
            } catch { errorMessage = error.localizedDescription }
        } label: {
            HStack(spacing: 18) {
                Text(option.id).font(.headline).frame(width: 30, height: 30)
                    .background((selected ? AppTheme.accent : Color.secondary).opacity(0.14), in: Circle())
                if !hidesText { Text(option.text).frame(maxWidth: .infinity, alignment: .leading) }
                else { Text("選項 \(option.id)").frame(maxWidth: .infinity, alignment: .leading) }
                if selected { Image(systemName: "checkmark.circle.fill").foregroundStyle(AppTheme.accent) }
            }
            .padding(14).frame(minHeight: 52)
            .background(AppTheme.card, in: RoundedRectangle(cornerRadius: 14))
            .overlay { RoundedRectangle(cornerRadius: 14).stroke(selected ? AppTheme.accent : .clear, lineWidth: 2) }
        }
        .buttonStyle(.plain)
        .accessibilityAddTraits(selected ? .isSelected : [])
    }

    @ViewBuilder
    private func mockPhoto(item: QuestionItem) -> some View {
        if let url = model.assetURL(for: item.imageAssetID), let image = UIImage(contentsOfFile: url.path) {
            Image(uiImage: image).resizable().scaledToFit()
                .accessibilityLabel("Part 1 作答照片")
                .frame(maxWidth: .infinity).readableCard()
        } else {
            Label("照片素材中斷；這份模考應標記為無效", systemImage: "photo.badge.exclamationmark")
                .foregroundStyle(.red).frame(maxWidth: .infinity).readableCard()
        }
    }

    private var navigationControls: some View {
        HStack(spacing: 12) {
            Button("上一題", systemImage: "chevron.left") { move(by: -1) }
                .buttonStyle(.bordered).disabled(!canMove(by: -1))
            Button("下一題", systemImage: "chevron.right") { move(by: 1) }
                .buttonStyle(.borderedProminent).disabled(!canMove(by: 1))
            if runtime.phase == .reading {
                Button("交卷") { showSubmitConfirmation = true }.buttonStyle(.bordered)
            }
        }
        .frame(maxWidth: .infinity)
    }

    private var sectionBreak: some View {
        VStack(spacing: 18) {
            Image(systemName: "checkmark.circle.fill").font(.system(size: 54)).foregroundStyle(.green)
            Text("聽力區段已結束").font(.largeTitle.bold())
            Text("已接受的答案都保留。閱讀開始後有完整 75 分鐘，截止時間不因離開 App 而重設。")
                .foregroundStyle(.secondary).multilineTextAlignment(.center)
            Button("開始閱讀") {
                do { try runtime.beginReading(); model.saveMockExam(runtime) }
                catch { errorMessage = error.localizedDescription }
            }
            .buttonStyle(.borderedProminent).controlSize(.large)
        }.padding()
    }

    private var expiredView: some View {
        VStack(spacing: 18) {
            Image(systemName: "timer").font(.system(size: 52)).foregroundStyle(.orange)
            Text("閱讀時間結束").font(.largeTitle.bold())
            Text("本機答案已保留，請完成交卷。")
            Button("完成交卷") { submit() }.buttonStyle(.borderedProminent).controlSize(.large)
        }.padding()
    }

    private var submittedView: some View {
        VStack(spacing: 18) {
            Image(systemName: "checkmark.seal.fill").font(.system(size: 56)).foregroundStyle(.green)
            Text("交卷完成").font(.largeTitle.bold())
            Text("本機已保存 \(runtime.selectedOptionIDs.count) 題作答；上線同步後仍由伺服器確認接收。")
                .foregroundStyle(.secondary).multilineTextAlignment(.center)
            Button("返回") { dismiss() }.buttonStyle(.borderedProminent)
        }.padding()
    }

    private var answerGrid: some View {
        NavigationStack {
            ScrollView {
                LazyVGrid(columns: [GridItem(.adaptive(minimum: 48), spacing: 10)], spacing: 10) {
                    ForEach(currentSectionIDs, id: \.self) { id in
                        let number = (runtime.form.orderedItemIDs.firstIndex(of: id) ?? 0) + 1
                        Button {
                            do { try runtime.navigate(to: id); showGrid = false; model.saveMockExam(runtime) }
                            catch { errorMessage = error.localizedDescription }
                        } label: {
                            Text("\(number)").monospacedDigit().frame(width: 44, height: 44)
                                .background(runtime.selectedOptionIDs[id] == nil ? Color.secondary.opacity(0.12) : AppTheme.accent.opacity(0.18), in: Circle())
                                .overlay { if id == runtime.currentItemID { Circle().stroke(AppTheme.accent, lineWidth: 2) } }
                        }
                        .buttonStyle(.plain)
                        .accessibilityLabel("第 \(number) 題，\(runtime.selectedOptionIDs[id] == nil ? "未作答" : "已作答")")
                        .accessibilityAddTraits(id == runtime.currentItemID ? .isSelected : [])
                    }
                }.padding()
            }
            .navigationTitle("題目導覽")
            .toolbar { ToolbarItem(placement: .confirmationAction) { Button("完成") { showGrid = false } } }
        }
    }

    private var currentSectionIDs: [String] {
        runtime.phase == .listening ? runtime.availableItemIDs() : runtime.phase == .reading ? runtime.form.readingItemIDs : []
    }
    private var progressText: String {
        guard let id = runtime.currentItemID, let index = runtime.form.orderedItemIDs.firstIndex(of: id) else { return "" }
        return "第 \(index + 1) / 200 題"
    }
    private var remainingText: String {
        let seconds = runtime.remainingSeconds() ?? 0
        return String(format: "%02d:%02d", seconds / 60, seconds % 60)
    }
    private var audioStatusIsFailure: Bool { if case .failed = audioPlayer.status { true } else { false } }
    private var audioStatusIcon: String { audioStatusIsFailure ? "exclamationmark.triangle" : "waveform.circle.fill" }
    private var audioStatusText: String {
        switch audioPlayer.status { case .idle: "準備固定播放時間線"; case .playing: "播放中；不可暫停或變速"; case .failed(let message): "音訊中斷：\(message)" }
    }

    private func canMove(by offset: Int) -> Bool {
        guard let id = runtime.currentItemID, let index = currentSectionIDs.firstIndex(of: id) else { return false }
        return currentSectionIDs.indices.contains(index + offset)
    }
    private func move(by offset: Int) {
        guard let id = runtime.currentItemID, let index = currentSectionIDs.firstIndex(of: id), currentSectionIDs.indices.contains(index + offset) else { return }
        do { try runtime.navigate(to: currentSectionIDs[index + offset]); model.saveMockExam(runtime) }
        catch { errorMessage = error.localizedDescription }
    }
    private func tick(_ now: Date) {
        let oldPhase = runtime.phase
        runtime.updateForTime(now)
        if oldPhase != runtime.phase { audioPlayer.stop(); model.saveMockExam(runtime) }
    }
    private func resumeTimelineIfNeeded() {
        guard runtime.phase == .listening, let audioURL, let start = runtime.sectionStartedAt else { return }
        audioPlayer.play(url: audioURL, elapsedSeconds: Date.now.timeIntervalSince(start))
    }
    private func handleScenePhase(_ phase: ScenePhase) {
        switch phase {
        case .active:
            runtime.endInterruption(.background)
            runtime.updateForTime()
            resumeTimelineIfNeeded()
        case .inactive, .background:
            runtime.beginInterruption(.background)
            model.saveMockExam(runtime)
        @unknown default: break
        }
    }
    private func submit() {
        do {
            try runtime.submit()
            model.saveMockExam(runtime)
            if !finalized { model.finalizeMockExam(runtime, groups: groups); finalized = true }
        } catch { errorMessage = error.localizedDescription }
    }
}
