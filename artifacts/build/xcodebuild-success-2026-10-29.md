# iPhoneOS build success — 2026-10-29

This supersedes the current-build status in the earlier exit-70 diagnosis files; those files remain unchanged as historical error evidence.

Command executed from `/Users/ziii/Desktop/TOEIC_IOS_App`:

```bash
xcodebuild -project TOEICPath.xcodeproj \
  -scheme TOEICPath \
  -destination 'generic/platform=iOS' \
  -derivedDataPath .build-device \
  CODE_SIGNING_ALLOWED=NO build
```

Result: `** BUILD SUCCEEDED **`.

Built product: `.build-device/Build/Products/Debug-iphoneos/TOEICPath.app`.

Post-build checks:

- Bundle identifier: `com.local.TOEICPath`.
- Project signing values remain `DEVELOPMENT_TEAM = VJ3Y39FF2P`, `CODE_SIGN_STYLE = Automatic`.
- `.app/SeedContent`: 74 files, 7 manifests, 30 media files, 8.9 MB.
- `diff -qr SeedContent .build-device/Build/Products/Debug-iphoneos/TOEICPath.app/SeedContent`: no differences.
- Built-resource bootstrap suite: 4 tests, 0 failures when `TOEICPATH_SEED_ROOT` points at the built `.app` directory.

This is compile/link/package evidence. Physical-device launch and the five-minute interaction checklist remain separate, not-run acceptance work.
