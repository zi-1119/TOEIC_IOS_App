#!/bin/zsh
# Producer-side reference run of scripts/swift_importer_probe.swift against the current TOEICPathCore sources.
# Builds in a throwaway package + scratch path under $TMPDIR; does not touch the repo's .swiftpm-build or sources.
# Not a receiver acceptance result — Codex owns the authoritative importer verification.
set -euo pipefail
REPO=/Users/ziii/Desktop/TOEIC_IOS_App
PKG=${TMPDIR:-/tmp}/ag-importer-probe-pkg
rm -rf "$PKG"; mkdir -p "$PKG/Sources/AGProbe"
cp "$REPO/scripts/swift_importer_probe.swift" "$PKG/Sources/AGProbe/main.swift"
cat > "$PKG/Package.swift" <<EOF
// swift-tools-version: 6.0
import PackageDescription
let package = Package(
    name: "AGProbe",
    platforms: [.macOS(.v14)],
    dependencies: [.package(path: "$REPO")],
    targets: [.executableTarget(name: "AGProbe", dependencies: [.product(name: "TOEICPath", package: "TOEIC_IOS_App")],
        swiftSettings: [.swiftLanguageMode(.v5), .unsafeFlags(["-enable-testing"])])]
)
EOF
cd "$PKG"
swift build --scratch-path "${TMPDIR:-/tmp}/ag-importer-probe-build" -Xswiftc -enable-testing 2>&1 | tail -15
"${TMPDIR:-/tmp}/ag-importer-probe-build/debug/AGProbe" "$@"
