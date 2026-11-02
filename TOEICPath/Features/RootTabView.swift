import SwiftUI

struct RootTabView: View {
    @EnvironmentObject private var model: AppModel

    var body: some View {
        TabView(selection: $model.selectedTab) {
            Tab("今天", systemImage: "sun.max", value: 0) { TodayView() }
            Tab("練習", systemImage: "book.pages", value: 1) { PracticeHomeView() }
            Tab("好友", systemImage: "person.2", value: 2) { FriendsView() }
            Tab("我的", systemImage: "person.crop.circle", value: 3) { ProfileView() }
        }
        .safeAreaInset(edge: .top, spacing: 0) {
            switch model.contentBootstrapState {
            case .idle, .loading:
                HStack(spacing: 10) {
                    ProgressView()
                    Text("正在驗證離線題庫…").font(.subheadline)
                }
                .frame(maxWidth: .infinity, minHeight: 44)
                .background(.regularMaterial)
                .accessibilityElement(children: .combine)
            case .failed(let message):
                VStack(alignment: .leading, spacing: 8) {
                    Label("離線題庫尚未啟用", systemImage: "exclamationmark.triangle.fill")
                        .font(.headline).foregroundStyle(.orange)
                    Text(message).font(.caption).foregroundStyle(.secondary)
                    Button("重新驗證") { Task { await model.bootstrapBundledContent() } }
                        .buttonStyle(.bordered)
                }
                .padding(12)
                .frame(maxWidth: .infinity, alignment: .leading)
                .background(.regularMaterial)
            case .ready:
                EmptyView()
            }
        }
    }
}
