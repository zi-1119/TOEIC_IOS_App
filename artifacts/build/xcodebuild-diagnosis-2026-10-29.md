# Xcode Full-Build Recheck — 2026-10-29

## Required command executed

```text
xcodebuild -project TOEICPath.xcodeproj \
  -scheme TOEICPath \
  -destination 'generic/platform=iOS' \
  -derivedDataPath .build-device \
  CODE_SIGNING_ALLOWED=NO build
```

Result: **exit 70**, before build settings, source compilation, linking, or signing.

```text
IDERunDestination: Supported platforms for the buildables in the current scheme is empty.
xcodebuild: error: Unable to find a destination matching the provided destination specifier:
    { generic:1, platform:iOS }

Ineligible destinations for the "TOEICPath" scheme:
    { platform:iOS, id:dvtdevice-DVTiPhonePlaceholder-iphoneos:placeholder,
      name:Any iOS Device,
      error:iOS 26.2 is not installed. Please download and install the platform
      from Xcode > Settings > Components. }
```

The same command was rerun with output suppressed only to capture its shell status; it again returned `XCODEBUILD_EXIT_CODE=70`. The failure is unchanged from the prior diagnosis and is not evidence that the App compiled.

## Supplemental check

All App and SwiftUI sources were separately passed to `swiftc -typecheck` using the iPhoneOS 26.2 SDK and iOS 18 deployment target. This is useful source-level evidence but does not replace the failed full build. The first run exposed two warnings; both were corrected. The final rerun exited 0 with no output or warnings:

```text
sdk_path=$(xcrun --sdk iphoneos --show-sdk-path) && \
xcrun --sdk iphoneos swiftc -typecheck -parse-as-library \
  -target arm64-apple-ios18.0 -sdk "$sdk_path" \
  -module-name TOEICPath -module-cache-path .swift-module-cache \
  $(find TOEICPath -type f -name '*.swift' | sort)
```

Required user action: install the iOS 26.2 platform component in Xcode Settings → Components, then rerun the exact command above.
