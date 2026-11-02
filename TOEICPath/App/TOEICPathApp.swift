import SwiftUI

@main
struct TOEICPathApp: App {
    @StateObject private var model: AppModel

    init() {
        _model = StateObject(wrappedValue: AppModel(backend: BackendComposition.make()))
    }

    var body: some Scene {
        WindowGroup {
            Group {
                if model.profile.preferences.hasCompletedOnboarding {
                    RootTabView()
                } else {
                    OnboardingView()
                }
            }
            .environmentObject(model)
            .tint(AppTheme.accent)
            .task { await model.bootstrapBundledContent() }
        }
    }
}
