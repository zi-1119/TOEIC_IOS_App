import SwiftUI

struct FriendsView: View {
    @EnvironmentObject private var model: AppModel
    @State private var selectedSegment = 0
    @State private var showAccount = false

    var body: some View {
        NavigationStack {
            Group {
                if !model.usesNetworkBackend {
                    EmptyStateView(
                        icon: "network.slash",
                        title: "好友服務尚未部署",
                        message: "離線練習可以直接使用。聊天與跨手機對戰需要受保護的網路服務、正式登入與通知設定；目前不會建立假帳號或假連線。"
                    )
                } else {
                    VStack(spacing: 0) {
                        Picker("好友功能", selection: $selectedSegment) {
                            Text("聊天").tag(0)
                            Text("好友").tag(1)
                            Text("比賽").tag(2)
                        }
                        .pickerStyle(.segmented)
                        .padding()

                        if model.identity == nil {
                            EmptyStateView(icon: "person.crop.circle.badge.checkmark", title: "登入後使用好友功能", message: "練習不需要登入；好友服務會驗證帳號、權限與訊息持久化。")
                        } else {
                            Group {
                                switch selectedSegment {
                                case 0: chatList
                                case 1: friendList
                                default: matchList
                                }
                            }
                        }
                    }
                }
            }
            .navigationTitle("好友")
            .toolbar {
                if model.usesNetworkBackend {
                    ToolbarItem(placement: .topBarTrailing) {
                        Button(model.identity == nil ? "登入" : "邀請", systemImage: model.identity == nil ? "person.crop.circle" : "person.badge.plus") {
                            showAccount = true
                        }
                    }
                }
            }
            .sheet(isPresented: $showAccount) { LocalAccountView() }
            .task {
                guard model.usesNetworkBackend, model.identity != nil else { return }
                do { try await model.refreshFriends(); try await model.refreshMatches() }
                catch { model.socialError = error.localizedDescription }
            }
            .alert("好友服務", isPresented: Binding(get: { model.socialError != nil }, set: { if !$0 { model.socialError = nil } })) {
                Button("好") { model.socialError = nil }
            } message: { Text(model.socialError ?? "") }
        }
    }

    private var chatList: some View {
        Group {
            if model.friends.isEmpty {
                EmptyStateView(icon: "bubble.left.and.bubble.right", title: "還沒有好友", message: "建立邀請碼，讓另一個已登入帳號接受後即可傳送持久訊息。")
            } else {
                List(model.friends) { friend in
                    NavigationLink { ConversationView(friend: friend) } label: {
                        HStack(spacing: 12) {
                            avatar(friend.displayName)
                            VStack(alignment: .leading, spacing: 4) {
                                Text(friend.displayName).font(.headline)
                                Text("持久訊息會在重連後重新查詢").font(.subheadline).foregroundStyle(.secondary).lineLimit(1)
                            }
                            Spacer()
                            if friend.unreadCount > 0 {
                                Text("\(friend.unreadCount)").font(.caption.bold()).foregroundStyle(.white)
                                    .frame(minWidth: 24, minHeight: 24).background(AppTheme.accent, in: Circle())
                                    .accessibilityLabel("\(friend.unreadCount) 則未讀")
                            }
                        }.frame(minHeight: 54)
                    }
                }
            }
        }
    }

    private var friendList: some View {
        Group {
            if model.friends.isEmpty {
                EmptyStateView(icon: "person.2", title: "好友清單是空的", message: "邀請採雙向接受，不讀取手機通訊錄。")
            } else {
                List(model.friends) { friend in
                    HStack {
                        avatar(friend.displayName)
                        VStack(alignment: .leading) { Text(friend.displayName).font(.headline); Text(friend.handle).foregroundStyle(.secondary) }
                        Spacer()
                        Button("邀賽") {
                            Task {
                                await perform { try await model.createLocalBattle(opponentID: friend.id) }
                                selectedSegment = 2
                            }
                        }.buttonStyle(.bordered)
                    }
                    .swipeActions {
                        Button("封鎖", role: .destructive) {
                            Task { await perform { try await model.setBlocked(friendID: friend.id, blocked: true) } }
                        }
                        Button("刪除") {
                            Task { await perform { try await model.removeFriend(friendID: friend.id) } }
                        }.tint(.orange)
                    }
                }
            }
        }
    }

    private var matchList: some View {
        Group {
            if model.matches.isEmpty {
                EmptyStateView(icon: "bolt.horizontal.circle", title: "尚無對戰", message: "從好友清單建立 Part 5 速戰；邀請、時限、收答案與判分都由服務端決定。")
            } else {
                List(model.matches) { match in
                    NavigationLink { BattleDetailView(initialMatch: match) } label: {
                        VStack(alignment: .leading, spacing: 10) {
                            HStack {
                                Text("Part 5 速戰").font(.headline)
                                Spacer()
                                StatusPill(icon: "clock", text: stateLabel(match.state), color: match.state == .invited ? .orange : AppTheme.accent)
                            }
                            Text("\(match.orderedItemIDs.count) 題 · 邀請期限 \(match.invitationExpiresAt.formatted(date: .abbreviated, time: .shortened))")
                                .font(.caption).foregroundStyle(.secondary)
                        }.padding(.vertical, 6)
                    }
                }
            }
        }
    }

    @MainActor
    private func perform(_ operation: () async throws -> Void) async {
        do { try await operation() }
        catch { model.socialError = error.localizedDescription }
    }

    private func avatar(_ name: String) -> some View {
        Text(String(name.prefix(1))).font(.headline).frame(width: 44, height: 44).background(AppTheme.accent.opacity(0.15), in: Circle())
            .accessibilityLabel("\(name) 的頭像")
    }

    private func stateLabel(_ state: MatchState) -> String {
        switch state { case .invited: "待接受"; case .accepted: "已接受"; case .preparing: "準備中"; case .active: "進行中"; case .settling: "結算中"; case .completed: "已完成"; case .expired: "已過期"; case .declined: "已婉拒"; case .cancelled: "已取消"; case .invalid: "無效賽"; case .forfeited: "已棄賽" }
    }
}

private struct BattleDetailView: View {
    @EnvironmentObject private var model: AppModel
    let initialMatch: BattleMatch
    @State private var errorMessage: String?
    @State private var busy = false

    private var match: BattleMatch {
        model.matches.first(where: { $0.id == initialMatch.id }) ?? initialMatch
    }
    private var participant: MatchParticipant? {
        guard let id = model.identity?.userID else { return nil }
        return match.participants.first { $0.id == id }
    }
    private var currentItem: BattleQuestion? {
        guard match.state == .active, let participant, participant.state == .active,
              participant.progress < match.orderedItemIDs.count else { return nil }
        return model.battleItem(match.orderedItemIDs[participant.progress], in: match)
    }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 18) {
                HStack {
                    Text("Part 5 速戰").font(.title2.bold())
                    Spacer()
                    StatusPill(icon: "bolt.fill", text: stateLabel(match.state), color: match.state.isTerminal ? .secondary : AppTheme.accent)
                }
                Text("每題答對 100 分，答錯或未答 0 分；同分平手，速度不作決勝。雙方完成前不揭曉答案。")
                    .foregroundStyle(.secondary)

                if model.battleQuestions(for: match).isEmpty {
                    Label("尚未取得這場對戰的題目，請重新整理後再試。", systemImage: "exclamationmark.triangle")
                        .foregroundStyle(.orange).readableCard()
                } else {
                    phaseContent
                }
            }
            .padding()
        }
        .background(AppTheme.warmBackground)
        .navigationTitle("對戰")
        .navigationBarTitleDisplayMode(.inline)
        .task {
            await refresh()
            while !Task.isCancelled && !match.state.isTerminal {
                try? await Task.sleep(for: .seconds(3))
                await refresh()
            }
        }
        .alert("對戰服務", isPresented: Binding(get: { errorMessage != nil }, set: { if !$0 { errorMessage = nil } })) {
            Button("好") { errorMessage = nil }
        } message: { Text(errorMessage ?? "") }
    }

    @ViewBuilder
    private var phaseContent: some View {
        switch match.state {
        case .invited:
            if participant?.state == .invited {
                Label("邀請將於 \(match.invitationExpiresAt.formatted(date: .abbreviated, time: .shortened)) 到期", systemImage: "clock")
                actionButton("接受挑戰", icon: "checkmark.circle") { try await model.acceptBattle(match.id) }
            } else {
                waiting("等待對方接受邀請")
            }
        case .accepted, .preparing:
            if participant?.state == .ready {
                waiting("素材已確認，等待對方準備")
            } else {
                Text("開始前會確認這份對戰所需素材；雙方都準備後，伺服器同時設定開始與截止時間。")
                actionButton("素材齊全，準備開始", icon: "checkmark.shield") { try await model.markBattleReady(match.id) }
            }
        case .active:
            activeContent
        case .settling:
            waiting("伺服器正在結算")
        case .completed:
            completedContent
        case .expired:
            terminal("邀請已過期", icon: "clock.badge.xmark")
        case .declined:
            terminal("挑戰已婉拒", icon: "hand.raised")
        case .cancelled:
            terminal("挑戰已取消", icon: "xmark.circle")
        case .invalid:
            terminal("服務或素材故障，這場已標為無效賽", icon: "exclamationmark.shield")
        case .forfeited:
            terminal("對局已棄賽", icon: "flag.slash")
        }
    }

    @ViewBuilder
    private var activeContent: some View {
        if participant?.state == .submitted {
            waiting("答案已由伺服器收妥，等待對方完成")
        } else if let item = currentItem, let participant {
            HStack {
                Text("第 \(participant.progress + 1)／\(match.orderedItemIDs.count) 題").font(.headline)
                Spacer()
                if let deadline = match.deadline { Text("截止 \(deadline.formatted(date: .omitted, time: .shortened))").font(.caption).foregroundStyle(.secondary) }
            }
            Text(item.prompt ?? "").font(.title3.bold()).readableCard()
            ForEach(item.options) { option in
                Button {
                    Task { await perform { try await model.submitBattleAnswer(matchID: match.id, itemID: item.id, optionID: option.id, requestID: UUID()) } }
                } label: {
                    HStack(alignment: .top, spacing: 18) {
                        Text(option.id).font(.headline).frame(width: 30, height: 30).background(AppTheme.accent.opacity(0.12), in: Circle())
                        Text(option.text).multilineTextAlignment(.leading)
                        Spacer()
                    }.frame(maxWidth: .infinity, minHeight: 44, alignment: .leading)
                }
                .buttonStyle(.bordered)
                .disabled(busy)
            }
        } else if participant?.progress == match.orderedItemIDs.count {
            actionButton("交卷", icon: "paperplane") { try await model.submitBattle(match.id) }
        } else {
            terminal("找不到對戰題目，請確認題庫版本。", icon: "questionmark.folder")
        }
    }

    private var completedContent: some View {
        VStack(alignment: .leading, spacing: 12) {
            Label(match.winnerID == nil ? "平手" : match.winnerID == model.identity?.userID ? "你贏了" : "對方獲勝",
                  systemImage: match.winnerID == nil ? "equal.circle.fill" : "trophy.fill")
                .font(.title2.bold()).foregroundStyle(AppTheme.accent)
            ForEach(match.participants) { participant in
                HStack {
                    Text(participant.id == model.identity?.userID ? "你" : "對方")
                    Spacer()
                    Text("\(participant.serverScore ?? 0) 分").monospacedDigit().font(.headline)
                }
            }
            Text("這是比賽積分，不是多益分數。")
                .font(.caption).foregroundStyle(.secondary)
        }.readableCard()
    }

    private func actionButton(_ title: String, icon: String, operation: @escaping () async throws -> Void) -> some View {
        Button(title, systemImage: icon) { Task { await perform(operation) } }
            .buttonStyle(.borderedProminent).controlSize(.large).disabled(busy)
            .frame(maxWidth: .infinity, minHeight: 44)
    }

    private func waiting(_ text: String) -> some View {
        Label(text, systemImage: "hourglass").frame(maxWidth: .infinity, minHeight: 80).readableCard()
    }

    private func terminal(_ text: String, icon: String) -> some View {
        Label(text, systemImage: icon).frame(maxWidth: .infinity, minHeight: 80).readableCard()
    }

    @MainActor
    private func perform(_ operation: () async throws -> Void) async {
        busy = true
        defer { busy = false }
        do { try await operation() }
        catch { errorMessage = error.localizedDescription }
    }

    @MainActor
    private func refresh() async {
        do { try await model.refreshBattle(match.id) }
        catch { errorMessage = error.localizedDescription }
    }

    private func stateLabel(_ state: MatchState) -> String {
        switch state { case .invited: "待接受"; case .accepted: "已接受"; case .preparing: "準備中"; case .active: "進行中"; case .settling: "結算中"; case .completed: "已完成"; case .expired: "已過期"; case .declined: "已婉拒"; case .cancelled: "已取消"; case .invalid: "無效賽"; case .forfeited: "已棄賽" }
    }
}

private struct ConversationView: View {
    @EnvironmentObject private var model: AppModel
    let friend: FriendSummary
    @State private var draft = ""
    @State private var messages: [ChatMessage] = []
    @State private var conversationID: UUID?
    @State private var errorMessage: String?

    var body: some View {
        VStack {
            if messages.isEmpty {
                EmptyStateView(icon: "bubble.left.and.bubble.right", title: "還沒有訊息", message: "訊息會持久保存；重新進入時從服務資料補齊。")
            } else {
                List(messages) { message in
                    HStack(alignment: .bottom) {
                        if message.senderID == model.identity?.userID { Spacer(minLength: 44) }
                        VStack(alignment: .leading, spacing: 4) {
                            Text(message.body)
                            Label(deliveryText(message.delivery), systemImage: deliveryIcon(message.delivery))
                                .font(.caption2).foregroundStyle(.secondary)
                            if message.delivery == .failed {
                                Button("重送") { retry(message) }.font(.caption)
                            }
                        }.readableCard()
                        if message.senderID != model.identity?.userID { Spacer(minLength: 44) }
                    }
                }.listStyle(.plain)
            }
            HStack {
                TextField("訊息", text: $draft, axis: .vertical).textFieldStyle(.roundedBorder)
                Button("送出", systemImage: "arrow.up.circle.fill") { sendDraft() }
                    .disabled(draft.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty || conversationID == nil)
                    .labelStyle(.iconOnly).font(.title2).frame(minWidth: 44, minHeight: 44)
            }
            .floatingSurface().padding(.horizontal)
        }
        .navigationTitle(friend.displayName)
        .navigationBarTitleDisplayMode(.inline)
        .task { await loadMessages() }
        .alert("訊息未送出", isPresented: Binding(get: { errorMessage != nil }, set: { if !$0 { errorMessage = nil } })) {
            Button("好") { errorMessage = nil }
        } message: { Text(errorMessage ?? "") }
    }

    @MainActor
    private func loadMessages() async {
        do {
            let id = try await model.conversationID(with: friend.id)
            conversationID = id
            messages = try await model.messages(conversationID: id)
        } catch { errorMessage = error.localizedDescription }
    }

    private func sendDraft() {
        guard let conversationID else { return }
        let body = draft.trimmingCharacters(in: .whitespacesAndNewlines)
        let clientID = UUID()
        let optimistic = ChatMessage(id: UUID(), clientMessageID: clientID, conversationID: conversationID,
                                     senderID: model.identity?.userID ?? UUID(), body: body, createdAt: .now, delivery: .sending)
        messages.append(optimistic)
        draft = ""
        Task {
            do {
                let accepted = try await model.sendMessage(conversationID: conversationID, clientMessageID: clientID, body: body)
                if let index = messages.firstIndex(where: { $0.clientMessageID == clientID }) { messages[index] = accepted }
            } catch {
                if let index = messages.firstIndex(where: { $0.clientMessageID == clientID }) { messages[index].delivery = .failed }
                errorMessage = error.localizedDescription
            }
        }
    }

    private func retry(_ message: ChatMessage) {
        guard let index = messages.firstIndex(where: { $0.clientMessageID == message.clientMessageID }) else { return }
        messages[index].delivery = .sending
        Task {
            do {
                let accepted = try await model.sendMessage(
                    conversationID: message.conversationID, clientMessageID: message.clientMessageID, body: message.body
                )
                if let refreshed = messages.firstIndex(where: { $0.clientMessageID == message.clientMessageID }) { messages[refreshed] = accepted }
            } catch {
                if let refreshed = messages.firstIndex(where: { $0.clientMessageID == message.clientMessageID }) { messages[refreshed].delivery = .failed }
                errorMessage = error.localizedDescription
            }
        }
    }

    private func deliveryText(_ state: DeliveryState) -> String {
        switch state { case .sending: "送出中"; case .sent: "已送出"; case .failed: "失敗" }
    }
    private func deliveryIcon(_ state: DeliveryState) -> String {
        switch state { case .sending: "clock"; case .sent: "checkmark.circle"; case .failed: "exclamationmark.circle" }
    }
}

private struct LocalAccountView: View {
    @EnvironmentObject private var model: AppModel
    @Environment(\.dismiss) private var dismiss
    @State private var email = ""
    @State private var code = ""
    @State private var inviteCode = ""
    @State private var generatedInvite: String?
    @State private var status: String?
    @State private var busy = false

    var body: some View {
        NavigationStack {
            Form {
                if let identity = model.identity {
                    Section("目前帳號") {
                        LabeledContent("Email", value: identity.email)
                        LabeledContent("身分 ID", value: identity.userID.uuidString)
                    }
                    Section("邀請好友") {
                        Button("建立 24 小時邀請碼") { createInvite() }.disabled(busy)
                        if let generatedInvite { Text(generatedInvite).font(.footnote.monospaced()).textSelection(.enabled) }
                        TextField("貼上邀請碼或完整連結", text: $inviteCode).textInputAutocapitalization(.never)
                        Button("接受邀請") { acceptInvite() }.disabled(inviteCode.isEmpty || busy)
                    }
                    Section {
                        Button("切換帳號", role: .destructive) {
                            Task { await model.signOutLocalAccount(); dismiss() }
                        }
                    } footer: {
                        Text("只清除目前 App 的登入工作階段，不刪除服務端的帳號、好友、訊息或對戰資料。")
                    }
                } else {
                    Section("Email OTP") {
                        TextField("name@example.com", text: $email).textContentType(.emailAddress).textInputAutocapitalization(.never)
                        Button("要求驗證碼") { requestCode() }.disabled(email.isEmpty || busy)
                        TextField("六位驗證碼", text: $code).keyboardType(.numberPad).textContentType(.oneTimeCode)
                        Button("驗證並合併本機紀錄") { verify() }.disabled(code.isEmpty || busy)
                        if model.usesNetworkBackend {
                            Text("驗證碼由已設定的後端寄送；App 不內建正式驗證碼。")
                                .font(.caption).foregroundStyle(.secondary)
                        } else {
                            Text("本機開發服務驗證碼固定為 \(LocalBackendHub.verificationCode)；正式部署不可沿用此碼。")
                                .font(.caption).foregroundStyle(.secondary)
                        }
                    }
                }
                if let status { Section { Text(status).foregroundStyle(.secondary) } }
            }
            .navigationTitle("帳號與邀請")
            .toolbar { ToolbarItem(placement: .confirmationAction) { Button("完成") { dismiss() } } }
        }
    }

    private func requestCode() {
        busy = true
        Task { @MainActor in
            defer { busy = false }
            do {
                try await model.requestLocalSignInCode(email: email)
                status = model.usesNetworkBackend ? "驗證碼要求已送出，請查看 Email。" : "驗證碼已由本機開發服務建立。"
            }
            catch { status = error.localizedDescription }
        }
    }

    private func verify() {
        busy = true
        Task { @MainActor in
            defer { busy = false }
            do { try await model.verifyLocalSignIn(email: email, code: code); status = "登入完成，本機練習紀錄已冪等合併。" }
            catch { status = error.localizedDescription }
        }
    }

    private func createInvite() {
        busy = true
        Task { @MainActor in
            defer { busy = false }
            do { generatedInvite = try await model.createFriendInvite().absoluteString }
            catch { status = error.localizedDescription }
        }
    }

    private func acceptInvite() {
        busy = true
        Task { @MainActor in
            defer { busy = false }
            let code = URL(string: inviteCode)?.pathComponents.last ?? inviteCode
            do { try await model.acceptFriendInvite(code: code); status = "已互相成為好友。" }
            catch { status = error.localizedDescription }
        }
    }
}
