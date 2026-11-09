import AVFoundation
import Combine
import SwiftUI

@MainActor
private final class AudioQualityPreviewPlayer: ObservableObject {
    @Published private(set) var playingID: String?
    @Published private(set) var errorMessage: String?

    private var player: AVAudioPlayer?
    private var finishTask: Task<Void, Never>?

    func toggle(_ variant: AudioPreviewVariant) {
        if playingID == variant.id {
            stop()
            return
        }
        play(variant)
    }

    func stop() {
        finishTask?.cancel()
        finishTask = nil
        player?.stop()
        player = nil
        playingID = nil
    }

    private func play(_ variant: AudioPreviewVariant) {
        stop()
        errorMessage = nil

        guard let url = AudioPreviewCatalog.url(for: variant) else {
            errorMessage = "找不到試聽檔案：\(variant.fileName)"
            return
        }

        do {
            let session = AVAudioSession.sharedInstance()
            try session.setCategory(.playback, mode: .spokenAudio)
            try session.setActive(true)

            let player = try AVAudioPlayer(contentsOf: url)
            player.prepareToPlay()
            guard player.play() else { throw PlaybackError.cannotStart }
            self.player = player
            playingID = variant.id

            let duration = max(player.duration, 0.1)
            finishTask = Task { @MainActor [weak self] in
                try? await Task.sleep(for: .seconds(duration))
                guard !Task.isCancelled else { return }
                self?.stop()
            }
        } catch {
            stop()
            errorMessage = "音訊無法播放：\(error.localizedDescription)"
        }
    }

    private enum PlaybackError: LocalizedError {
        case cannotStart

        var errorDescription: String? { "播放器無法開始。" }
    }
}

struct AudioQualityPreviewView: View {
    @Environment(\.scenePhase) private var scenePhase
    @StateObject private var player = AudioQualityPreviewPlayer()

    var body: some View {
        List {
            Section {
                Label("離線 A／B 音質試聽", systemImage: "waveform.badge.magnifyingglass")
                    .font(.headline)
                Text("請使用同一部 iPhone、相同音量，先聽 A 再聽 B。B 是比較候選，尚未取代正式題庫音訊，也不會計入練習或能力紀錄。")
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
            }

            if let errorMessage = player.errorMessage {
                Section {
                    Label(errorMessage, systemImage: "exclamationmark.triangle.fill")
                        .foregroundStyle(.red)
                        .accessibilityLabel("播放失敗，\(errorMessage)")
                }
            }

            ForEach(AudioPreviewCatalog.samples) { sample in
                Section {
                    VStack(alignment: .leading, spacing: 6) {
                        Text(sample.title).font(.headline)
                        Text(sample.note).font(.subheadline).foregroundStyle(.secondary)
                    }
                    .padding(.vertical, 4)

                    ForEach(sample.variants) { variant in
                        previewButton(variant)
                    }
                } header: {
                    Text("範例 \(sample.number) · Part \(sample.part)")
                }
            }
        }
        .navigationTitle("音質試聽")
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .topBarTrailing) {
                Button("停止", systemImage: "stop.fill") { player.stop() }
                    .disabled(player.playingID == nil)
            }
        }
        .onDisappear { player.stop() }
        .onChange(of: scenePhase) { _, phase in
            if phase != .active { player.stop() }
        }
    }

    private func previewButton(_ variant: AudioPreviewVariant) -> some View {
        let isPlaying = player.playingID == variant.id
        return Button { player.toggle(variant) } label: {
            HStack(alignment: .top, spacing: 18) {
                Text(variant.marker)
                    .font(.headline)
                    .frame(width: 34, height: 34)
                    .background(
                        (isPlaying ? AppTheme.accent : Color.secondary).opacity(0.14),
                        in: Circle()
                    )

                VStack(alignment: .leading, spacing: 5) {
                    HStack(spacing: 8) {
                        Text(variant.title).font(.headline)
                        if variant.kind == .candidate {
                            Text("尚未採用")
                                .font(.caption2.weight(.semibold))
                                .foregroundStyle(.orange)
                                .padding(.horizontal, 7)
                                .padding(.vertical, 3)
                                .background(.orange.opacity(0.12), in: Capsule())
                        }
                    }
                    Text(variant.detail)
                        .font(.subheadline)
                        .foregroundStyle(.secondary)
                        .multilineTextAlignment(.leading)
                }
                .frame(maxWidth: .infinity, alignment: .leading)

                Image(systemName: isPlaying ? "stop.circle.fill" : "play.circle.fill")
                    .font(.title2)
                    .foregroundStyle(isPlaying ? AppTheme.accent : .secondary)
            }
            .padding(.vertical, 8)
            .frame(maxWidth: .infinity, minHeight: 56, alignment: .leading)
            .contentShape(Rectangle())
        }
        .buttonStyle(.plain)
        .accessibilityLabel("\(variant.marker)，\(variant.title)，\(variant.detail)，\(isPlaying ? "正在播放，點兩下停止" : "點兩下播放")")
        .accessibilityAddTraits(isPlaying ? .isSelected : [])
    }
}
