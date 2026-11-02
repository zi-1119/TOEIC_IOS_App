import Foundation

enum SampleContent {
    static let package = ContentPackage(
        manifest: .init(
            schemaVersion: 1,
            packageID: "bundled-preview",
            contentVersion: "preview-2026.10.1",
            locale: "en",
            createdAt: Date(timeIntervalSince1970: 1_782_509_400),
            generator: "Hand-reviewed preview fixtures",
            generatorVersion: "1",
            license: "Internal evaluation only"
        ),
        assets: [],
        groups: groups
    )

    static let groups: [QuestionGroup] = [
        group("p1-station", family: "station-platform", part: .part1, scenario: "Train station", items: [
            item("p1-q1", nil, ["A person is checking a departure board.", "Several suitcases are being loaded onto a cart.", "The platform is completely empty.", "A ticket is being printed."], 0,
                 evidence: "The person is looking up at the departure information display.", zh: "照片中的人正在查看出發資訊看板；選項 A 最符合可見動作。", transcript: "A. A person is checking a departure board. B. Several suitcases are being loaded onto a cart. C. The platform is completely empty. D. A ticket is being printed.")
        ]),
        group("p2-office", family: "office-supply", part: .part2, scenario: "Office", items: [
            item("p2-q1", nil, ["By the supply cabinet.", "Yes, it arrived yesterday.", "About twenty pages."], 0,
                 evidence: "A where-question requires a location; only choice A gives one.", zh: "問句詢問地點，只有 A 回答影印紙放在哪裡。", transcript: "Where did you put the extra copy paper? A. By the supply cabinet. B. Yes, it arrived yesterday. C. About twenty pages.")
        ]),
        group("p3-catering", family: "event-catering", part: .part3, scenario: "Event planning", items: [
            item("p3-q1", "What are the speakers mainly discussing?", ["A room reservation", "A catering order", "A travel schedule", "A hiring decision"], 1, evidence: "They discuss guest count, meals, and confirming an order.", zh: "對話重點是活動餐飲訂單。"),
            item("p3-q2", "What change does the woman mention?", ["The event will start earlier", "More guests will attend", "A speaker has canceled", "The venue has changed"], 1, evidence: "She says the guest count increased to sixty.", zh: "女士提到來賓人數增加到六十人。"),
            item("p3-q3", "What will the man probably do next?", ["Send a revised estimate", "Visit the venue", "Call the keynote speaker", "Print name tags"], 0, evidence: "He promises to email an updated estimate.", zh: "男士接下來會寄送更新後的估價。")
        ], transcript: "W: Our guest count has increased to sixty. Can you update the lunch order? M: Certainly. I will email a revised estimate this afternoon. W: Great, please include vegetarian meals for eight people."),
        group("p4-museum", family: "museum-announcement", part: .part4, scenario: "Public announcement", items: [
            item("p4-q1", "Where most likely is the announcement being made?", ["At a museum", "At a bank", "At a factory", "At a stadium"], 0, evidence: "The announcement refers to galleries and an exhibition.", zh: "提到展廳與展覽，因此場景是博物館。"),
            item("p4-q2", "What will happen at 2 p.m.?", ["A café will close", "A guided tour will begin", "Tickets will go on sale", "A film will be shown"], 1, evidence: "The speaker states that the guided tour begins at two.", zh: "下午兩點將開始導覽。"),
            item("p4-q3", "What are listeners asked to do?", ["Silence their phones", "Return a form", "Move their vehicles", "Purchase a map"], 0, evidence: "Visitors are asked to silence mobile phones.", zh: "廣播請訪客將手機調成靜音。")
        ], transcript: "Welcome to the Harbor City Museum. A guided tour of the new design exhibition will begin at two in the main lobby. Please silence your mobile phones before entering the galleries."),
        group("p5-report", family: "quarterly-report", part: .part5, scenario: "Business report", items: [
            item("p5-q1", "The quarterly report must be reviewed _____ it is sent to the client.", ["before", "despite", "during", "unless"], 0, evidence: "The review must happen earlier than sending, so ‘before’ expresses the required time sequence.", zh: "審閱發生在寄送之前，因此使用時間連接詞 before。", translation: "季度報告在寄給客戶之前必須先經過審閱。")
        ]),
        group("p6-email", family: "maintenance-email", part: .part6, scenario: "Building maintenance", documents: [
            .init(id: "p6-doc", kind: .email, title: "Elevator Maintenance", body: "To all tenants:\nThe west elevator will be unavailable on Friday while technicians (1) _____ a routine inspection. Please use the east elevator instead. The work is expected to finish by noon. (2) _____. We apologize for any inconvenience this may (3) _____. Questions should be directed (4) _____ the building office.", accessibilityLabel: nil)
        ], items: [
            item("p6-q1", "(1)", ["conduct", "conducted", "will conduct", "have conducted"], 0, evidence: "‘While technicians conduct’ uses the simple present for the scheduled action.", zh: "while 子句描述排定作業，使用現在簡單式 conduct。"),
            item("p6-q2", "(2)", ["Parking permits are available online.", "Signs will direct visitors to the other elevator.", "The rent is due next Monday.", "A new tenant moved in yesterday."], 1, evidence: "Only the sentence about directional signs supports the elevator-maintenance context.", zh: "只有指示牌的句子能連貫承接電梯停用資訊。"),
            item("p6-q3", "(3)", ["cause", "causes", "caused", "causing"], 0, evidence: "After modal ‘may’, use the base verb ‘cause’.", zh: "情態助動詞 may 後接原形動詞 cause。"),
            item("p6-q4", "(4)", ["at", "by", "to", "from"], 2, evidence: "The fixed expression is ‘direct questions to’ a person or office.", zh: "固定搭配為 direct questions to…。")
        ]),
        group("p7-library", family: "library-renovation", part: .part7, scenario: "Library notice", documents: [
            .init(id: "p7-doc", kind: .notice, title: "Temporary Entrance Change", body: "Beginning November 3, the north entrance of Brookfield Library will be closed for renovation. Visitors should enter through the doors beside the café on Pine Street. Book returns will remain available at the outdoor slot. The project is scheduled to finish on November 21.", accessibilityLabel: nil)
        ], items: [
            item("p7-q1", "Why was the notice written?", ["To announce a temporary access change", "To advertise a new café", "To request overdue books", "To recruit library staff"], 0, evidence: "The notice announces that one entrance will close and identifies another entrance.", zh: "公告目的是通知整修期間的臨時入口變更。"),
            item("p7-q2", "What is indicated about book returns?", ["They must be made inside", "They are suspended until November 21", "An outdoor return slot can still be used", "They have moved to Pine Street"], 2, evidence: "The notice explicitly says the outdoor book-return slot remains available.", zh: "公告明確指出戶外還書口仍可使用。")
        ])
    ]

    private static func group(
        _ id: String,
        family: String,
        part: TOEICPart,
        difficulty: Difficulty = .d2,
        scenario: String,
        documents: [StimulusDocument] = [],
        items: [QuestionItem],
        transcript: String? = nil
    ) -> QuestionGroup {
        var adjustedItems = items
        if let transcript {
            adjustedItems = items.map {
                .init(id: $0.id, prompt: $0.prompt, options: $0.options, correctOptionID: $0.correctOptionID, explanation: $0.explanation, skills: $0.skills, transcript: transcript, imageAssetID: $0.imageAssetID, audioAssetID: $0.audioAssetID)
            }
        }
        return .init(id: id, familyID: family, part: part, difficulty: difficulty, scenario: scenario, documents: documents, items: adjustedItems, audioAssetID: nil, audioSegments: [], timeLimitSeconds: nil, tags: [scenario.lowercased()])
    }

    private static func item(
        _ id: String,
        _ prompt: String?,
        _ optionTexts: [String],
        _ correct: Int,
        evidence: String,
        zh: String,
        transcript: String? = nil,
        translation: String? = nil
    ) -> QuestionItem {
        let letters = ["A", "B", "C", "D"]
        let options = optionTexts.enumerated().map { AnswerOption(id: letters[$0.offset], text: $0.element) }
        return .init(
            id: id,
            prompt: prompt,
            options: options,
            correctOptionID: letters[correct],
            explanation: .init(evidence: evidence, zhTW: zh, optionNotes: [:], translation: translation, vocabulary: [], takeaway: nil),
            skills: [], transcript: transcript, imageAssetID: nil, audioAssetID: nil
        )
    }
}
