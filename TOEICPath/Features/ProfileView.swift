import SwiftUI
import UniformTypeIdentifiers

struct ProfileView: View {
    @EnvironmentObject private var model: AppModel
    @State private var showImporter = false
    @State private var importMessage: String?

    private var listening: [ItemResponse] { model.standardResponses.filter { $0.part.section == .listening } }
    private var reading: [ItemResponse] { model.standardResponses.filter { $0.part.section == .reading } }

    var body: some View {
        NavigationStack {
            List {
                Section("能力報告") {
                    evidenceRow(title: "聽力", responses: listening, icon: "ear")
                    evidenceRow(title: "閱讀", responses: reading, icon: "book")
                    Text("只顯示首答表現與資料充分度；尚未以獨立資料校準，因此不提供 990 分數預估或信賴區間。")
                        .font(.caption).foregroundStyle(.secondary)
                }

                Section("目標") {
                    LabeledContent("每日", value: "\(model.profile.preferences.dailyMinutes) 分鐘")
                    LabeledContent("方向", value: model.profile.preferences.target)
                    if let date = model.profile.preferences.examDate { LabeledContent("考試日", value: date.formatted(date: .abbreviated, time: .omitted)) }
                }

                Section("題庫與下載") {
                    Button("匯入 Antigravity 批次目錄", systemImage: "square.and.arrow.down") { showImporter = true }
                    NavigationLink("內容審核報告") { ContentReviewView() }
                    LabeledContent("目前版本", value: model.package.manifest.contentVersion)
                    LabeledContent("離線題組", value: "\(model.package.groups.count)")
                }

                Section("隱私與通知") {
                    Toggle("允許通知", isOn: binding(\.notificationsEnabled))
                    Toggle("通知顯示訊息正文", isOn: binding(\.messagePreviewEnabled))
                    Text("正式成績、弱點與詳細作答預設不分享；訊息正文預設不出現在推播。")
                        .font(.caption).foregroundStyle(.secondary)
                }

                Section("資料") {
                    LabeledContent("本機作答紀錄", value: "\(model.completedResponses.count)")
                    LabeledContent("連線狀態", value: model.connectivity == .online ? "可連線" : "離線")
                    if let error = model.lastSaveError { Label(error, systemImage: "exclamationmark.triangle").foregroundStyle(.red) }
                }
            }
            .navigationTitle("我的")
            .fileImporter(isPresented: $showImporter, allowedContentTypes: [.folder]) { result in
                do {
                    let url = try result.get()
                    let access = url.startAccessingSecurityScopedResource()
                    defer { if access { url.stopAccessingSecurityScopedResource() } }
                    try model.importBatchDirectory(url)
                    importMessage = "批次已通過契約、雜湊與內容結構驗證；目前共同啟用 \(model.activeBatchCount) 批、\(model.package.groups.flatMap(\.items).count) 題。"
                }
                catch { importMessage = error.localizedDescription }
            }
            .alert("題庫匯入", isPresented: Binding(get: { importMessage != nil }, set: { if !$0 { importMessage = nil } })) { Button("好") { importMessage = nil } } message: { Text(importMessage ?? "") }
        }
    }

    private func evidenceRow(title: String, responses: [ItemResponse], icon: String) -> some View {
        HStack {
            Image(systemName: icon).foregroundStyle(AppTheme.accent).frame(width: 30)
            VStack(alignment: .leading) {
                Text(title).font(.headline)
                Text(responses.isEmpty ? "尚無標準條件證據" : "首答 \(responses.filter(\.isCorrect).count) / \(responses.count)")
                    .font(.subheadline).foregroundStyle(.secondary)
            }
            Spacer()
            Text(responses.count < 10 ? "證據不足" : "持續觀察").font(.caption.weight(.semibold)).foregroundStyle(responses.count < 10 ? .orange : .green)
        }.frame(minHeight: 48)
    }

    private func binding<T>(_ keyPath: WritableKeyPath<UserPreferences, T>) -> Binding<T> {
        Binding(get: { model.profile.preferences[keyPath: keyPath] }, set: { model.profile.preferences[keyPath: keyPath] = $0; model.persist() })
    }
}

struct ContentReviewView: View {
    @EnvironmentObject private var model: AppModel
    private var report: ContentValidationReport { model.validationReport }
    var body: some View {
        List {
            Section {
                Label(report.isImportable ? "可匯入" : "不可匯入", systemImage: report.isImportable ? "checkmark.seal.fill" : "xmark.octagon.fill")
                    .foregroundStyle(report.isImportable ? .green : .red)
                LabeledContent("錯誤", value: "\(report.errors.count)")
                LabeledContent("警告", value: "\(report.warnings.count)")
            }
            if report.issues.isEmpty {
                Section { Text("沒有發現結構問題。這不代表英文品質、版權或測量效度已完成複核。") }
            } else {
                Section("問題") {
                    ForEach(report.issues) { issue in
                        VStack(alignment: .leading, spacing: 4) {
                            Label(issue.severity == .error ? "錯誤" : "警告", systemImage: issue.severity == .error ? "xmark.circle" : "exclamationmark.triangle")
                                .font(.caption.bold()).foregroundStyle(issue.severity == .error ? .red : .orange)
                            Text(issue.path).font(.caption.monospaced()).foregroundStyle(.secondary)
                            Text(issue.message)
                        }.padding(.vertical, 4)
                    }
                }
            }
        }
        .navigationTitle("內容審核")
        .navigationBarTitleDisplayMode(.inline)
    }
}
