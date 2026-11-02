import SwiftUI

struct TodayView: View {
    @EnvironmentObject private var model: AppModel
    @Environment(\.dynamicTypeSize) private var dynamicTypeSize
    @State private var quickTestLaunch: QuickTestLaunch?

    private var focus: QuickTestFocus { model.profile.preferences.quickTestFocus }
    private var level: QuickTestLevel { model.profile.preferences.quickTestLevel }
    private var assembly: QuickTestAssembly { model.quickTestAssembly() }

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 18) {
                    VStack(alignment: .leading, spacing: 7) {
                        Text("今天想測哪一種？")
                            .font(.largeTitle.bold())
                        Text("約 10 題，交卷後一次看成績與解析。")
                            .font(.title3)
                            .foregroundStyle(.secondary)
                    }

                    VStack(alignment: .leading, spacing: 14) {
                        testConfigurationControls

                        HStack(spacing: 8) {
                            Label("\(assembly.actualItemCount) 題", systemImage: "list.number")
                            Text("・")
                            Text(assembly.containsReview ? "含複習題" : "優先新情境")
                        }
                        .font(.subheadline.weight(.semibold))

                        if !assembly.isExactTarget, assembly.actualItemCount > 0 {
                            Text("為了保留完整題組，本次是 \(assembly.actualItemCount) 題，不拆題組也不重複補滿。")
                                .font(.caption)
                                .foregroundStyle(.secondary)
                        } else if assembly.actualItemCount == 0 {
                            Label("目前沒有符合條件且素材完整的訓練題組。", systemImage: "exclamationmark.triangle")
                                .font(.caption)
                                .foregroundStyle(.orange)
                        }

                        Button {
                            quickTestLaunch = QuickTestLaunch(groups: assembly.groups)
                        } label: {
                            Label("開始測驗", systemImage: "play.fill")
                                .frame(maxWidth: .infinity, minHeight: 52)
                        }
                        .buttonStyle(.borderedProminent)
                        .controlSize(.large)
                        .disabled(assembly.groups.isEmpty)
                    }
                    .readableCard()

                    Group {
                        if dynamicTypeSize.isAccessibilitySize {
                            VStack(spacing: 12) {
                                metric(title: "待複習", value: "\(model.dueReviewCount)", icon: "clock.arrow.circlepath")
                                metric(title: "已完成", value: "\(model.profile.sessions.count)", icon: "checkmark.circle")
                            }
                        } else {
                            HStack(spacing: 12) {
                                metric(title: "待複習", value: "\(model.dueReviewCount)", icon: "clock.arrow.circlepath")
                                metric(title: "已完成", value: "\(model.profile.sessions.count)", icon: "checkmark.circle")
                            }
                        }
                    }

                    VStack(alignment: .leading, spacing: 10) {
                        Text("更多練習")
                            .font(.headline)
                        Text("可依 Part 練習並逐題查看解析；診斷與完整模考會在題庫符合正式條件後開放。")
                            .font(.subheadline)
                            .foregroundStyle(.secondary)
                        Button("前往分項練習") { model.selectedTab = 1 }
                            .buttonStyle(.bordered)
                    }
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .readableCard()

                    if let last = model.profile.sessions.last {
                        VStack(alignment: .leading, spacing: 8) {
                            Text("上次進度")
                                .font(.headline)
                            Text(last.completedAt?.formatted(date: .abbreviated, time: .shortened) ?? "未完成")
                            Text("\(last.responses.filter(\.isCorrect).count) / \(last.responses.count) 題答對")
                                .foregroundStyle(.secondary)
                        }
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .readableCard()
                    }
                }
                .padding()
            }
            .background(AppTheme.warmBackground)
            .navigationTitle("今天")
            .fullScreenCover(item: $quickTestLaunch) { launch in
                SessionView(groups: launch.groups, mode: .practice, presentation: .quickTest)
            }
        }
    }

    @ViewBuilder
    private var testConfigurationControls: some View {
        if dynamicTypeSize.isAccessibilitySize {
            VStack(alignment: .leading, spacing: 14) {
                Text("測驗範圍")
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
                Picker("測驗範圍", selection: focusBinding) {
                    ForEach(QuickTestFocus.allCases) { option in
                        Text(option.title).tag(option)
                    }
                }
                .pickerStyle(.menu)

                Text("難度（編輯估計）")
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
                Picker("難度（編輯估計）", selection: levelBinding) {
                    ForEach(QuickTestLevel.allCases) { option in
                        Text(option.title).tag(option)
                    }
                }
                .pickerStyle(.menu)
            }
        } else {
            Picker("範圍", selection: focusBinding) {
                ForEach(QuickTestFocus.allCases) { option in
                    Text(option.title).tag(option)
                }
            }
            .pickerStyle(.segmented)

            HStack {
                Text("難度（編輯估計）")
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
                Spacer()
                Picker("難度（編輯估計）", selection: levelBinding) {
                    ForEach(QuickTestLevel.allCases) { option in
                        Text(option.title).tag(option)
                    }
                }
                .pickerStyle(.segmented)
                .frame(maxWidth: 180)
            }
        }
    }

    private var focusBinding: Binding<QuickTestFocus> {
        Binding(
            get: { focus },
            set: { model.updateQuickTestPreferences(focus: $0, level: level) }
        )
    }

    private var levelBinding: Binding<QuickTestLevel> {
        Binding(
            get: { level },
            set: { model.updateQuickTestPreferences(focus: focus, level: $0) }
        )
    }

    private func metric(title: String, value: String, icon: String) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            Image(systemName: icon).foregroundStyle(AppTheme.accent)
            Text(value).font(.title.bold())
            Text(title).font(.subheadline).foregroundStyle(.secondary)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .readableCard()
    }
}

private struct QuickTestLaunch: Identifiable {
    let id = UUID()
    let groups: [QuestionGroup]
}
