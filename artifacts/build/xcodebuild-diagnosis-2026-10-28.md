# Xcode Full-Build Recheck — 2026-10-28

The generic-device destination was checked again because `-showdestinations` once more printed the iOS placeholders. This did not make the destination eligible.

## Destination command

```text
xcodebuild -project TOEICPath.xcodeproj -scheme TOEICPath -showdestinations
```

Observed output includes:

```text
IDERunDestination: Supported platforms for the buildables in the current scheme is empty.
Available destinations:
    Any iOS Device
    Any iOS Simulator Device
```

## Full unsigned build command

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

The placeholder being listed is not proof of eligibility. The blocking condition is unchanged: Xcode's component registry still rejects the iOS 26.2 generic destination. A full build has therefore not passed. The separate iPhoneOS whole-source type check and SwiftPM suite remain secondary evidence only.
