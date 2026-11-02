# Part 1 research laboratory audio comparison

Status: comparison evidence only. This directory is not an App seed package and does not replace or modify any Antigravity export.

## A — currently bundled source

- Path: `SeedContent/batch-ag-0006/assets/ag-ast-p1-000001-audio.m4a`
- SHA-256: `684cd4b76474d8dc727975321314eac90c070a2b720a0274f908a82453ebbef9`
- CoreAudio: AAC mono, 22,050 Hz, measured bitrate about 37.6 kbps, 15.016 seconds of valid frames.
- Content: four statements in A→D order, but the recording does not speak the option letters.
- Device acceptance: `not_passed`; the user reported muddy audio on iPhone.

## B — local comparison sample

- Path: `alternative-samantha-44k-labels.m4a`
- SHA-256: `75ecd6c2a7f35f6f4722c78c5ec4858185207faaae7c20160935c9de72eee1fc`
- CoreAudio: AAC mono, 44,100 Hz, measured bitrate about 124.7 kbps, 9.389 seconds.
- Voice/source: installed macOS Samantha voice at 160 WPM; the recording explicitly speaks A, B, C, and D.
- Purpose: lets the user compare voice and option-label clarity. A higher sample rate/bitrate alone is not accepted as proof of better perceptual quality.

## Physical-device shortlist result

On 2026-10-30 the user compared the three bundled Part 1 groups through the same iPhone built-in speaker and reported that the third sample, `ag-g-p1-000003` (`Karen en_AU`, `public_waterfront`), was the clearest. This is direct device evidence for preferring Karen as the first small-revision voice direction. It does not isolate bitrate, loudness, or sample rate as the cause because those properties and the spoken content differ between the three files.

## C — Karen, original pipeline and wording

- Path: `candidate-karen-original-pipeline.m4a`
- SHA-256: `8b0b691f5878e62e0f523a7e55d8225db11004aacc3e9a4b0a1dfa1244cb87b3`
- CoreAudio: AAC mono, 22,050 Hz, measured bitrate about 56.4 kbps, 12.777 seconds.
- Voice/source: installed macOS Karen voice (`en_AU`) at the existing 172 WPM, existing 1,200 ms inter-statement pause and existing AAC pipeline.
- Content: the original `ag-g-p1-000001` four statements without spoken option letters.
- Measured segment windows in milliseconds: A `300–2304`, B `3504–5636`, C `6836–9049`, D `10249–12327`.
- Purpose: keeps the original content and encoding pipeline while changing the voice direction to the user-preferred Karen voice.

## D — Karen with spoken A–D labels

- Path: `candidate-karen-with-labels.m4a`
- SHA-256: `a7e996696e32e3b24e705cab9630b8f9a0a2d393194aaaaad9e24c6d4ab90f4b`
- CoreAudio: AAC mono, 22,050 Hz, measured bitrate about 54.7 kbps, 13.508 seconds.
- Voice/source: the same Karen voice, rate, pauses and encoding pipeline as sample C.
- Content: the original four statements with audible A, B, C and D labels.
- Measured segment windows in milliseconds: A `300–2430`, B `3630–5928`, C `7128–9593`, D `10793–13058`.
- Purpose: tests whether spoken labels remove the answer-to-audio mapping ambiguity without reducing clarity or naturalness.

Samples C and D are comparison artifacts only. They have not been installed into `SeedContent`, and neither is an Antigravity immutable replacement package. The next acceptance step is an A/B comparison through the same iPhone speaker at the same system volume.

## E — Karen with spoken labels and a requested 400 ms label gap

- Path: `candidate-karen-labels-400ms-gap.m4a`
- SHA-256: `1eae239a6c1dbb7937e4f71754bc64269c2369968f8948e7c60abb471cc857be`
- CoreAudio: AAC mono, 22,050 Hz, measured bitrate about 57.0 kbps, 15.556 seconds.
- Voice/source: the same Karen voice, 172 WPM, 1,200 ms option-to-option pauses and current AAC pipeline.
- Content: each option speaks its A–D label, uses the macOS speech engine's requested 400 ms silence control, and then speaks the statement in the same utterance. This avoids the unnatural elongation observed when a letter was synthesized as a standalone utterance.
- Encoded-audio silence detection (`-45 dB`, minimum 250 ms) measured the four label-to-statement gaps as approximately 359, 359, 357 and 357 ms. The requested control value and measured encoded result are both recorded rather than described as sample-exact equivalents.
- Measured logical segment windows in milliseconds: A `300–2735`, B `3935–6810`, C `8010–11059`, D `12259–15106`.
- Reproduction: `python3 scripts/build_part1_audio_comparison.py`. The builder reads the immutable seed group and writes only this comparison artifact.

On 2026-10-30 the user accepted sample D's Karen-plus-label direction but requested more separation between the label and statement. Sample E is the resulting device-acceptance candidate and still does not modify `SeedContent` or an Antigravity export.

## Required before a production replacement

Antigravity must publish an immutable new batch/version rather than overwrite batches 0006/0007. Karen with spoken labels and an audible label-to-statement gap is the preferred direction; bulk replacement remains blocked until sample E is accepted on the iPhone speaker. The replacement needs remeasured segment timing, duration and SHA-256, audio-only blind solving, plus iPhone-speaker and headphone human review. Paid or external TTS requires the user's approval and deployment credentials first.
