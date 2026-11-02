# iPhone speaker audio diagnosis — 2026-10-29

## Reproduction boundary

- Reported output: iPhone built-in speaker.
- Same App contains both clear and muddy audio according to the user.
- Known muddy sample: `ag-g-p1-000001` (`Flo en_US`).
- The user identified `ag-g-p1-000003` (`Karen en_AU`) as the clearest of the three controlled bundled Part 1 samples on 2026-10-30. This establishes a preferred voice direction, but does not isolate one encoding or loudness property as the cause.

## Source inventory

All 27 bundled listening files are AAC mono at 22,050 Hz and came from the same local `say` + `afconvert` pipeline. Their measured encoded bitrate varies from about 37.6 to 61.8 kbps and mean volume from about -21.5 to -16.3 dB. The reported muddy sample is the lowest-bitrate file and has mean volume about -20.4 dB, but this alone cannot establish cause: voice synthesis, phoneme content, encoding complexity, speaker response, playback state, and route must be compared under the same device conditions.

Controlled Part 1 shortlist:

| Group | Voice | Bitrate | Mean / peak | Acceptance |
|---|---|---:|---:|---|
| `ag-g-p1-000001` | Flo en_US | 37.6 kbps | -20.4 / -3.7 dB | muddy, user-reported |
| `ag-g-p1-000002` | Flo en_GB | 38.9 kbps | -20.0 / -4.0 dB | unknown |
| `ag-g-p1-000003` | Karen en_AU | 54.0 kbps | -17.5 / -2.8 dB | clearest of shortlist, user-reported |
| local comparison | Samantha en_US, explicit A–D | 124.7 kbps, 44.1 kHz | not normalized to originals | comparison only |

The shortlist is intentionally small. Its result supports Karen for the next controlled revision; it does not justify a bulk replacement by itself.

Two follow-up files reuse the original `ag-g-p1-000001` statements and current encoding pipeline so the next device comparison can focus on Karen and spoken labels:

| Candidate | Spoken labels | Format / bitrate | Duration | SHA-256 |
|---|---|---|---:|---|
| `candidate-karen-original-pipeline.m4a` | no | AAC mono 22,050 Hz / ~56.4 kbps | 12.777 s | `8b0b691f5878e62e0f523a7e55d8225db11004aacc3e9a4b0a1dfa1244cb87b3` |
| `candidate-karen-with-labels.m4a` | A–D | AAC mono 22,050 Hz / ~54.7 kbps | 13.508 s | `a7e996696e32e3b24e705cab9630b8f9a0a2d393194aaaaad9e24c6d4ab90f4b` |

Both are local comparison artifacts under `artifacts/audio-comparison/part1-research-laboratory/`; neither changes exports, `SeedContent`, or the currently installed App.

The user preferred the labeled version but requested a short gap between each letter and its statement. `candidate-karen-labels-400ms-gap.m4a` implements that direction with a requested 400 ms speech-engine silence control. The encoded AAC file is 15.556 seconds with SHA-256 `1eae239a6c1dbb7937e4f71754bc64269c2369968f8948e7c60abb471cc857be`; silence detection measured the four audible gaps at approximately 357–359 ms. It remains a comparison-only artifact pending the same-device acceptance listen.

## App-side evidence added

Practice playback now captures the active `AVAudioSession` output port and sample rate at playback start in `AnswerCondition`, and shows a simple `輸出：iPhone 喇叭` (or the actual route) caption. These fields are diagnostic metadata only and do not change correctness or standard-evidence classification.

Normal 1× playback does not enable AVAudioPlayer rate processing; 0.8× explicitly does. Every new playback stops the existing player first. A mid-play route-change observer is not yet implemented, so any route switch during a clip remains a separate device test.

## Pending acceptance

1. Listen to `candidate-karen-labels-400ms-gap.m4a` on the same iPhone speaker and volume and accept or adjust the gap.
2. Ask Antigravity for an immutable small v3 candidate using the accepted Karen-plus-label rhythm; do not overwrite batches 0006/0007.
3. Require audio-only blind solving plus iPhone-speaker and headphone human review before bulk replacement.
