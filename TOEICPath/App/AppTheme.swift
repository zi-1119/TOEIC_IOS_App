import SwiftUI

enum AppTheme {
    static let accent = Color(red: 0.06, green: 0.39, blue: 0.90)
    static let warmBackground = Color(uiColor: UIColor { traits in
        traits.userInterfaceStyle == .dark
            ? UIColor(red: 0.055, green: 0.055, blue: 0.06, alpha: 1)
            : UIColor(red: 0.975, green: 0.97, blue: 0.955, alpha: 1)
    })
    static let card = Color(uiColor: .secondarySystemBackground)
}

struct ReadableCardModifier: ViewModifier {
    func body(content: Content) -> some View {
        content
            .padding(18)
            .background(AppTheme.card, in: RoundedRectangle(cornerRadius: 20, style: .continuous))
    }
}

struct FloatingSurfaceModifier: ViewModifier {
    @Environment(\.accessibilityReduceTransparency) private var reduceTransparency

    @ViewBuilder
    func body(content: Content) -> some View {
        if reduceTransparency {
            content
                .padding(12)
                .background(Color(uiColor: .systemBackground), in: RoundedRectangle(cornerRadius: 20, style: .continuous))
        } else if #available(iOS 26.0, *) {
            content
                .padding(12)
                .glassEffect(.regular.interactive(), in: .rect(cornerRadius: 20))
        } else {
            content
                .padding(12)
                .background(.regularMaterial, in: RoundedRectangle(cornerRadius: 20, style: .continuous))
        }
    }
}

extension View {
    func readableCard() -> some View { modifier(ReadableCardModifier()) }
    func floatingSurface() -> some View { modifier(FloatingSurfaceModifier()) }
}

struct StatusPill: View {
    let icon: String
    let text: String
    let color: Color

    var body: some View {
        Label(text, systemImage: icon)
            .font(.caption.weight(.semibold))
            .foregroundStyle(color)
            .padding(.horizontal, 10)
            .padding(.vertical, 6)
            .background(color.opacity(0.12), in: Capsule())
    }
}

struct EmptyStateView: View {
    let icon: String
    let title: String
    let message: String

    var body: some View {
        ContentUnavailableView(title, systemImage: icon, description: Text(message))
    }
}
