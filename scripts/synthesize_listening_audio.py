#!/usr/bin/env python3
"""
Synthesize playable TOEIC Part 1-4 audio assets using macOS `/usr/bin/say` and `/usr/bin/afconvert`,
measuring exact sample-accurate segment_times (start_ms, end_ms) and duration_ms.
"""

import hashlib
import json
import re
import subprocess
import tempfile
import wave
from pathlib import Path
from typing import Any, Dict, List, Tuple

SAMPLE_RATE = 22050
SPEECH_RATE_WPM = 172

# A bare leading article such as "A customer is waiting" is ordinary English,
# not an option label. Only punctuation-delimited labels are explicit enough to
# receive a spoken pause.
EXPLICIT_OPTION_LABEL = re.compile(
    r"^\s*(?:\(([A-D])\)|([A-D])(?:[).:]|\s+-))\s+(.+?)\s*$"
)

# Distinct voice pools mapped to installed macOS voices
FEMALE_ROLE_HINTS = {
    "clara", "ms.", "mrs.", "female", "woman", "receptionist", "specialist",
    "assistant", "coordinator", "clerk", "planner", "nurse", "instructor",
    "administrator", "merchandiser", "lead", "director",
}
MALE_ROLE_HINTS = {
    "devon", "mr.", "male", "man", "supervisor", "manager", "technician",
    "officer", "representative", "head", "concierge", "architect", "designer",
    "dispatcher", "announcer", "president", "guest", "client", "patient",
}


def infer_gender(role: str, first_text: str, index: int) -> str:
    r_low = role.lower()
    if "female" in r_low:
        return "F"
    if "male" in r_low:
        return "M"
    # Check greetings in dialogue text if any
    if re.search(r"\b(Hi|Hello),?\s+(Devon|Marcus|Daniel|Kenji|David|Tom| Lucas|Leo)\b", first_text):
        # Greeting a male means this speaker might be opposite, handled by alternation
        pass
    # Alternate by speaker index so 2-speaker dialogues always contrast F vs M
    return "F" if index % 2 == 0 else "M"


def select_macos_voice(accent: str, role: str, speaker_idx: int, used_voices: List[str]) -> Tuple[str, str, bool]:
    """
    Returns (voice_name, actual_locale, is_ca_fallback).
    Never fabricates accent verification: if accent == 'ca', uses North American en_US voice
    and flags is_ca_fallback = True so source_note_zh and reviews.jsonl disclose it transparently.
    """
    r_low = role.lower()
    is_narrator = "narrator" in r_low
    gender = "F" if "female" in r_low else ("M" if "male" in r_low else ("F" if speaker_idx % 2 == 0 else "M"))

    if accent == "us":
        if is_narrator:
            candidates = ["Flo (英文（美國）)", "Samantha", "Reed (英文（美國）)"]
        elif gender == "F":
            candidates = ["Samantha", "Shelley (英文（美國）)", "Sandy (英文（美國）)", "Flo (英文（美國）)"]
        else:
            candidates = ["Reed (英文（美國）)", "Eddy (英文（美國）)", "Rocko (英文（美國）)"]
        for c in candidates:
            if c not in used_voices:
                return c, "en_US", False
        return candidates[0], "en_US", False

    if accent == "uk":
        if is_narrator:
            candidates = ["Flo (英文（英國）)", "Daniel", "Reed (英文（英國）)"]
        elif gender == "F":
            candidates = ["Shelley (英文（英國）)", "Flo (英文（英國）)", "Sandy (英文（英國）)"]
        else:
            candidates = ["Daniel", "Reed (英文（英國）)", "Eddy (英文（英國）)", "Rocko (英文（英國）)"]
        for c in candidates:
            if c not in used_voices:
                return c, "en_GB", False
        return candidates[0], "en_GB", False

    if accent == "au":
        # macOS built-in Australian English voice
        return "Karen", "en_AU", False

    if accent == "ca":
        # macOS built-in voices on this host do not include an en_CA voice pack;
        # use a distinct North American en_US voice and explicitly flag fallback.
        if gender == "F":
            candidates = ["Shelley (英文（美國）)", "Sandy (英文（美國）)", "Samantha"]
        else:
            candidates = ["Eddy (英文（美國）)", "Rocko (英文（美國）)", "Reed (英文（美國）)"]
        for c in candidates:
            if c not in used_voices:
                return c, "en_US (North American fallback for ca)", True
        return candidates[0], "en_US (North American fallback for ca)", True

    return "Samantha", "en_US", False


def option_gap_spoken_text(
    *,
    part: int,
    segment_index: int,
    text_en: str,
    option_label_gap_ms: int,
) -> str:
    """Return the exact text sent to ``say`` for one audio-script segment.

    Part 1 permits explicit A-D option labels. Part 2 keeps segment zero as the
    question and only permits A-C on its response segments. Other Parts, a
    non-positive gap, a bare English article, and an invalid label are returned
    byte-for-byte unchanged.
    """
    if option_label_gap_ms <= 0:
        return text_en
    if part == 1:
        allowed_labels = set("ABCD")
    elif part == 2 and segment_index > 0:
        allowed_labels = set("ABC")
    else:
        return text_en

    match = EXPLICIT_OPTION_LABEL.match(text_en)
    if not match:
        return text_en
    label = match.group(1) or match.group(2)
    if label not in allowed_labels:
        return text_en
    return f"{label} [[slnc {option_label_gap_ms}]] {match.group(3)}"


def synthesize_group_audio(
    group: Dict[str, Any],
    out_m4a_path: Path,
    *,
    option_label_gap_ms: int = 0,
) -> Dict[str, Any]:
    """
    Synthesizes all segments in group['stimulus']['audio_script'] into out_m4a_path (.m4a),
    returns metadata dict with:
      - sha256
      - duration_ms
      - segment_times: [{segment_id, start_ms, end_ms}]
      - voice_cast: [{speaker_id, role, planned_accent, voice_name, locale, ca_fallback}]
      - has_ca_fallback: bool

    When option_label_gap_ms is positive, a leading Part 1/2 option label such as
    ``(A)`` is followed by the macOS speech engine's millisecond silence command
    within the same utterance. Keeping one utterance avoids stretching an isolated
    letter. The default preserves existing output.
    """
    part = group["part"]
    speakers = group["stimulus"]["speakers"]
    script = group["stimulus"]["audio_script"]

    speaker_voice_map: Dict[str, Tuple[str, str, bool]] = {}
    used_voices: List[str] = []
    voice_cast: List[Dict[str, Any]] = []

    for idx, spk in enumerate(speakers):
        sid = spk["speaker_id"]
        acc = spk["accent"]
        role = spk["role"]
        v_name, v_loc, ca_fb = select_macos_voice(acc, role, idx, used_voices)
        used_voices.append(v_name)
        speaker_voice_map[sid] = (v_name, v_loc, ca_fb)
        voice_cast.append({
            "speaker_id": sid,
            "role": role,
            "planned_accent": acc,
            "voice_name": v_name,
            "locale": v_loc,
            "ca_fallback": ca_fb,
        })

    out_m4a_path.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        master_wav_path = tmp_path / "master.wav"

        pcm_chunks: List[bytes] = []
        total_frames = 0

        def append_silence(ms: int) -> None:
            nonlocal total_frames
            n_frames = int(round(ms * SAMPLE_RATE / 1000.0))
            pcm_chunks.append(b"\x00\x00" * n_frames)
            total_frames += n_frames

        # Initial lead-in silence: 300 ms
        append_silence(300)

        segment_times: List[Dict[str, Any]] = []
        for s_idx, seg in enumerate(script):
            seg_id = seg["segment_id"]
            spk_id = seg["speaker_id"]
            text_en = seg["text_en"]
            voice_name, _, _ = speaker_voice_map[spk_id]

            start_ms = int(round(total_frames * 1000.0 / SAMPLE_RATE))

            spoken_pieces = [option_gap_spoken_text(
                part=part,
                segment_index=s_idx,
                text_en=text_en,
                option_label_gap_ms=option_label_gap_ms,
            )]

            for piece_idx, spoken_text in enumerate(spoken_pieces):
                piece_wav = tmp_path / f"seg_{s_idx:02d}_piece_{piece_idx:02d}.wav"
                subprocess.run(
                    [
                        "/usr/bin/say",
                        "-v", voice_name,
                        "-r", str(SPEECH_RATE_WPM),
                        f"--data-format=LEI16@{SAMPLE_RATE}",
                        "-o", str(piece_wav),
                        spoken_text,
                    ],
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=30,
                    check=True,
                )

                with wave.open(str(piece_wav), "rb") as wf:
                    assert wf.getnchannels() == 1
                    assert wf.getsampwidth() == 2
                    assert wf.getframerate() == SAMPLE_RATE
                    n_frames = wf.getnframes()
                    raw_pcm = wf.readframes(n_frames)

                pcm_chunks.append(raw_pcm)
                total_frames += n_frames

            end_ms = int(round(total_frames * 1000.0 / SAMPLE_RATE))
            if end_ms <= start_ms:
                end_ms = start_ms + 50

            segment_times.append({
                "segment_id": seg_id,
                "start_ms": start_ms,
                "end_ms": end_ms,
            })

            # Determine inter-segment pause
            if s_idx < len(script) - 1:
                next_seg = script[s_idx + 1]
                if part == 1:
                    append_silence(1200)
                elif part == 2:
                    append_silence(1200 if s_idx == 0 else 1000)
                else:
                    # Part 3 or Part 4: longer pause before narrator questions
                    if "-seg-q" in next_seg["segment_id"] or "narrator" in next_seg["speaker_id"]:
                        append_silence(1200)
                    else:
                        append_silence(550)

        # Trailing silence: 450 ms
        append_silence(450)

        with wave.open(str(master_wav_path), "wb") as mf:
            mf.setnchannels(1)
            mf.setsampwidth(2)
            mf.setframerate(SAMPLE_RATE)
            mf.writeframes(b"".join(pcm_chunks))

        # Encode to AAC .m4a
        if out_m4a_path.exists():
            out_m4a_path.unlink()
        subprocess.run(
            [
                "/usr/bin/afconvert",
                "-f", "m4af",
                "-d", "aac",
                "-b", "64000",
                str(master_wav_path),
                str(out_m4a_path),
            ],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=30,
            check=True,
        )

    total_pcm_ms = int(round(total_frames * 1000.0 / SAMPLE_RATE))
    last_end_ms = segment_times[-1]["end_ms"] if segment_times else 0
    duration_ms = max(total_pcm_ms, last_end_ms + 200)

    h = hashlib.sha256()
    with out_m4a_path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)

    return {
        "sha256": h.hexdigest(),
        "duration_ms": duration_ms,
        "segment_times": segment_times,
        "voice_cast": voice_cast,
        "has_ca_fallback": any(v["ca_fallback"] for v in voice_cast),
        "option_label_gap_ms": option_label_gap_ms,
    }


if __name__ == "__main__":
    print("synthesize_listening_audio module ready.")
