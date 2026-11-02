# Xcode Full-Build Diagnosis — 2026-10-27

## Executed environment checks

```text
$ xcodebuild -version
Xcode 26.3
Build version 17C529

$ xcode-select -p
/Applications/Xcode.app/Contents/Developer

$ xcodebuild -checkFirstLaunchStatus
exit 0

$ xcodebuild -showsdks
iOS 26.2 -sdk iphoneos26.2
Simulator - iOS 26.2 -sdk iphonesimulator26.2

$ xcrun --sdk iphoneos --show-sdk-path
/Applications/Xcode.app/Contents/Developer/Platforms/iPhoneOS.platform/Developer/SDKs/iPhoneOS26.2.sdk

$ xcrun simctl list runtimes
iOS 18.6 (22G86)
```

The iPhoneOS platform bundle and SDK directory exist. `Info.plist` reports platform/version 26.2. First-launch and license checks succeed. Only the iOS 18.6 Simulator runtime is installed; there is no matching iOS 26.2 component/runtime registered with Xcode.

## Destination resolution evidence

Command:

```text
xcodebuild -project TOEICPath.xcodeproj -scheme TOEICPath -showdestinations
```

Result, exit 0 with no eligible destination:

```text
IDERunDestination: Supported platforms for the buildables in the current scheme is empty.

Ineligible destinations for the "TOEICPath" scheme:
    { platform:iOS, id:dvtdevice-DVTiPhonePlaceholder-iphoneos:placeholder,
      name:Any iOS Device,
      error:iOS 26.2 is not installed. Please download and install the platform
      from Xcode > Settings > Components. }
```

## Full build evidence

Command actually executed:

```text
xcodebuild -project TOEICPath.xcodeproj \
  -scheme TOEICPath \
  -configuration Debug \
  -destination 'generic/platform=iOS' \
  -derivedDataPath .build-device \
  CODE_SIGNING_ALLOWED=NO build
```

Result: exit 70 before build settings or Swift compilation.

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

`-showBuildSettings` independently fails with exit 64 and the same empty-platform condition. This happens before evaluating app source, signing, or target build phases.

## Diagnosis

This failure is in Xcode's destination/platform component registry, not evidence of a successful or failed app compilation. The SDK being readable by `swiftc` does not make the Xcode 26.2 platform component eligible. Xcode 26.3 currently sees only an iOS 18.6 Simulator runtime and explicitly requests installation of the iOS 26.2 component from Settings > Components.

No Antigravity package or project source change can correct this registration. No platform download was initiated automatically because it is a large external Xcode installation change. After installing the matching iOS 26.2 component/runtime, rerun the exact full-build command above and preserve its new result. Direct `swiftc -typecheck` remains useful secondary evidence, but is not a substitute for that build.
