import SwiftUI

struct OnboardingView: View {
    @EnvironmentObject private var model: AppModel
    @State private var step = 0
    @State private var dailyMinutes = 20
    @State private var target = "穩定提升聽讀能力"
    @State private var hasExamDate = false
    @State private var examDate = Calendar.current.date(byAdding: .month, value: 2, to: .now) ?? .now

    var body: some View {
        NavigationStack {
            VStack(spacing: 28) {
                Spacer()
                Image(systemName: step == 0 ? "chart.line.uptrend.xyaxis" : "calendar.badge.clock")
                    .font(.system(size: 48, weight: .medium))
                    .foregroundStyle(AppTheme.accent)
                    .accessibilityHidden(true)

                VStack(spacing: 10) {
                    Text(step == 0 ? "練得更準，不猜分數" : "安排一條走得久的路")
                        .font(.largeTitle.bold())
                        .multilineTextAlignment(.center)
                    Text(step == 0
                         ? "先試練也可以。聽力與閱讀分開記錄，用足夠證據找出下一步。"
                         : "每日時間可以隨時更改；考試日也可以之後再填。")
                        .foregroundStyle(.secondary)
                        .multilineTextAlignment(.center)
                }

                if step == 0 {
                    Picker("每日練習時間", selection: $dailyMinutes) {
                        Text("10 分鐘").tag(10)
                        Text("20 分鐘").tag(20)
                        Text("40 分鐘").tag(40)
                    }
                    .pickerStyle(.segmented)
                    .accessibilityHint("設定每日建議的練習長度")
                } else {
                    VStack(alignment: .leading, spacing: 16) {
                        TextField("目標", text: $target)
                            .textFieldStyle(.roundedBorder)
                        Toggle("設定考試日", isOn: $hasExamDate)
                        if hasExamDate {
                            DatePicker("考試日", selection: $examDate, in: Date.now..., displayedComponents: .date)
                        }
                    }
                    .readableCard()
                }

                Spacer()
                Button {
                    if step == 0 { step = 1 }
                    else { model.completeOnboarding(minutes: dailyMinutes, target: target, examDate: hasExamDate ? examDate : nil) }
                } label: {
                    Text(step == 0 ? "繼續" : "開始試練")
                        .frame(maxWidth: .infinity, minHeight: 50)
                }
                .buttonStyle(.borderedProminent)
                .controlSize(.large)
            }
            .padding(24)
            .background(AppTheme.warmBackground.ignoresSafeArea())
            .toolbar {
                if step == 1 {
                    ToolbarItem(placement: .topBarLeading) {
                        Button("返回", systemImage: "chevron.left") { step = 0 }
                    }
                }
            }
        }
    }
}
