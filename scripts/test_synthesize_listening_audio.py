#!/usr/bin/env python3
"""Deterministic tests for option-label parsing; never invoke macOS TTS."""

import subprocess
import tempfile
import unittest
import wave
from pathlib import Path
from unittest import mock

from scripts import synthesize_listening_audio as audio


class OptionGapSpokenTextTests(unittest.TestCase):
    def test_bare_article_a_is_not_an_option_label(self) -> None:
        text = "A customer is waiting near the reception desk."
        self.assertEqual(
            audio.option_gap_spoken_text(
                part=1, segment_index=0, text_en=text, option_label_gap_ms=400
            ),
            text,
        )

    def test_part_two_question_segment_is_never_rewritten(self) -> None:
        text = "(A) customer called about the invoice."
        self.assertEqual(
            audio.option_gap_spoken_text(
                part=2, segment_index=0, text_en=text, option_label_gap_ms=400
            ),
            text,
        )

    def test_explicit_label_formats_are_rewritten_for_part_one(self) -> None:
        cases = {
            "(A) She is opening a cabinet.": "A [[slnc 400]] She is opening a cabinet.",
            "A) She is opening a cabinet.": "A [[slnc 400]] She is opening a cabinet.",
            "B. The shelves are empty.": "B [[slnc 400]] The shelves are empty.",
            "C: A ladder is beside the wall.": "C [[slnc 400]] A ladder is beside the wall.",
            "D - Several boxes are stacked.": "D [[slnc 400]] Several boxes are stacked.",
        }
        for source, expected in cases.items():
            with self.subTest(source=source):
                self.assertEqual(
                    audio.option_gap_spoken_text(
                        part=1,
                        segment_index=1,
                        text_en=source,
                        option_label_gap_ms=400,
                    ),
                    expected,
                )

    def test_part_two_rejects_option_d(self) -> None:
        self.assertEqual(
            audio.option_gap_spoken_text(
                part=2,
                segment_index=3,
                text_en="(C) This is the third valid response.",
                option_label_gap_ms=400,
            ),
            "C [[slnc 400]] This is the third valid response.",
        )
        text = "(D) This response must not be relabelled."
        self.assertEqual(
            audio.option_gap_spoken_text(
                part=2, segment_index=3, text_en=text, option_label_gap_ms=400
            ),
            text,
        )

    def test_other_parts_and_zero_gap_preserve_exact_text(self) -> None:
        text = "(A) Keep this exact text."
        self.assertEqual(
            audio.option_gap_spoken_text(
                part=3, segment_index=1, text_en=text, option_label_gap_ms=400
            ),
            text,
        )
        self.assertEqual(
            audio.option_gap_spoken_text(
                part=1, segment_index=0, text_en=text, option_label_gap_ms=0
            ),
            text,
        )


class SynthesisPathTests(unittest.TestCase):
    def test_actual_synthesis_path_uses_safe_part_two_parsing(self) -> None:
        group = {
            "part": 2,
            "stimulus": {
                "speakers": [
                    {"speaker_id": "q", "accent": "us", "role": "male questioner"},
                    {"speaker_id": "r", "accent": "au", "role": "female responder"},
                ],
                "audio_script": [
                    {"segment_id": "q1", "speaker_id": "q", "text_en": "A customer is waiting outside."},
                    {"segment_id": "a1", "speaker_id": "r", "text_en": "(A) In the main lobby."},
                    {"segment_id": "b1", "speaker_id": "r", "text_en": "B. At three o'clock."},
                    {"segment_id": "d1", "speaker_id": "r", "text_en": "(D) This label is invalid for Part 2."},
                ],
            },
        }
        spoken_texts = []

        def fake_run(command, **kwargs):
            if command[0] == "/usr/bin/say":
                output = Path(command[command.index("-o") + 1])
                spoken_texts.append(command[-1])
                with wave.open(str(output), "wb") as wav:
                    wav.setnchannels(1)
                    wav.setsampwidth(2)
                    wav.setframerate(audio.SAMPLE_RATE)
                    wav.writeframes(b"\x00\x00" * 32)
            elif command[0] == "/usr/bin/afconvert":
                Path(command[-1]).write_bytes(b"deterministic-test-m4a")
            else:
                self.fail(f"unexpected command: {command}")
            return subprocess.CompletedProcess(command, 0)

        with tempfile.TemporaryDirectory() as directory, mock.patch.object(
            audio.subprocess, "run", side_effect=fake_run
        ):
            result = audio.synthesize_group_audio(
                group,
                Path(directory) / "out.m4a",
                option_label_gap_ms=400,
            )

        self.assertEqual(
            spoken_texts,
            [
                "A customer is waiting outside.",
                "A [[slnc 400]] In the main lobby.",
                "B [[slnc 400]] At three o'clock.",
                "(D) This label is invalid for Part 2.",
            ],
        )
        self.assertEqual(result["option_label_gap_ms"], 400)
        self.assertEqual(len(result["segment_times"]), 4)


if __name__ == "__main__":
    unittest.main()
