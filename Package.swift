// swift-tools-version: 6.0
import PackageDescription

let package = Package(
    name: "TOEICPathCore",
    platforms: [.macOS(.v14)],
    products: [.library(name: "TOEICPath", targets: ["TOEICPath"])],
    targets: [
        .target(
            name: "TOEICPath",
            path: "TOEICPath",
            exclude: ["Features", "Resources", "App/AppTheme.swift", "App/TOEICPathApp.swift"],
            sources: ["App/AppModel.swift", "Domain", "Data/BundledContentBootstrap.swift", "Data/ContentValidator.swift", "Data/ContentBatchContract.swift", "Data/ContentBatchImporter.swift", "Data/ContentVersionStore.swift", "Data/MockFormContract.swift", "Data/LearningEngines.swift", "Data/LocalBackendService.swift", "Data/LocalProfileStore.swift", "Data/NetworkBackendClient.swift", "Data/SampleContent.swift", "Data/ServiceContracts.swift"]
        ),
        .testTarget(name: "TOEICPathTests", dependencies: ["TOEICPath"], path: "TOEICPathTests")
    ]
)
