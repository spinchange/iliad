from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "build_audiobook", ROOT / "tools" / "build_audiobook.py"
)
assert SPEC and SPEC.loader
audio = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = audio
SPEC.loader.exec_module(audio)


class AudiobookTests(unittest.TestCase):
    def test_parse_translation_ignores_commentary_and_notes(self) -> None:
        content = """BOOK 1

Commentary 99 not a verse
------------
   1  Sing, goddess, the wrath[1] of Achilles,
   2  ruinous wrath.

   3  Next paragraph.
------------
Notes
[1] a note
"""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "book.txt"
            path.write_text(content, encoding="utf-8")
            units = audio.parse_translation(path)
        self.assertEqual([u.line_start for u in units], [1, 3])
        self.assertEqual(units[0].text, "Sing, goddess, the wrath of Achilles, ruinous wrath.")

    def test_ranges_create_separate_sections(self) -> None:
        verses = [
            audio.Unit((audio.Verse(1, "One.", 0),)),
            audio.Unit((audio.Verse(2, "Two.", 0),)),
            audio.Unit((audio.Verse(5, "Five.", 1),)),
        ]
        selected = audio.select_ranges(verses, [[1, 2], [5, 5]])
        chunks = audio.make_chunks(selected, target_chars=100, max_chars=200)
        self.assertEqual(len(chunks), 2)

    def test_chunking_respects_max_chars(self) -> None:
        units = [
            audio.Unit((audio.Verse(i, ("word " * 20).strip() + ".", 0),))
            for i in range(1, 8)
        ]
        chunks = audio.make_chunks(units, target_chars=150, max_chars=220)
        self.assertTrue(all(len(audio.chunk_text(c)) <= 220 for c in chunks))

    def test_chunking_waits_for_sentence_boundary(self) -> None:
        units = [
            audio.Unit(
                (
                    audio.Verse(1, "This sentence begins", 0),
                    audio.Verse(2, "and reaches its proper end.", 0),
                    audio.Verse(3, "Another sentence begins", 0),
                    audio.Verse(4, "and also ends properly.", 0),
                )
            )
        ]
        chunks = audio.make_chunks(units, target_chars=30, max_chars=80)
        self.assertEqual(
            [(chunk[0].line_start, chunk[-1].line_end) for chunk in chunks],
            [(1, 2), (3, 4)],
        )
        self.assertTrue(
            all(audio.ends_sentence(chunk[-1].verses[-1].text) for chunk in chunks)
        )

    def test_chunk_text_preserves_paragraph_breaks(self) -> None:
        units = [
            audio.Unit((audio.Verse(1, "First sentence.", 0),), paragraph=0),
            audio.Unit((audio.Verse(2, "Second sentence.", 0),), paragraph=1),
        ]
        chunks = audio.make_chunks(units, target_chars=100, max_chars=200)
        self.assertEqual(audio.chunk_text(chunks[0]), "First sentence.\n\nSecond sentence.")

    def test_alignment_detects_omitted_clause(self) -> None:
        expected = "He lifted the spear and called to all the Achaeans."
        observed = "He lifted the spear."
        metrics = audio.alignment_metrics(expected, observed)
        self.assertGreaterEqual(metrics["max_deletion_run"], 5)
        status, _ = audio.suggest_status(
            metrics,
            {
                "max_deletion_ratio": 0.02,
                "max_deletion_run": 3,
                "max_substitution_ratio": 0.06,
                "min_length_ratio": 0.94,
                "max_length_ratio": 1.06,
            },
        )
        self.assertEqual(status, "fail")

    def test_alignment_allows_punctuation_and_case(self) -> None:
        metrics = audio.alignment_metrics(
            "Then Achilles spoke: “Hear me!”", "then achilles spoke hear me"
        )
        self.assertEqual(metrics["deletions"], 0)
        self.assertEqual(metrics["substitutions"], 0)

    def test_alignment_ignores_asr_orthography(self) -> None:
        metrics = audio.alignment_metrics(
            "His honor held, with the wine sack and salt water.",
            "His honour held, with the winesack and saltwater.",
        )
        self.assertEqual(metrics["deletions"], 0)
        self.assertEqual(metrics["substitutions"], 0)

    def test_alignment_treats_unicode_name_as_one_word(self) -> None:
        metrics = audio.alignment_metrics("Eëtion's city.", "Aetion's city.")
        self.assertEqual(metrics["deletions"], 0)
        self.assertEqual(metrics["substitutions"], 1)

    def test_alignment_handles_compound_join_next_to_substitution(self) -> None:
        metrics = audio.alignment_metrics(
            "the god-signs to the Danaans",
            "the godsigns for the Danans",
        )
        self.assertEqual(metrics["deletions"], 0)
        self.assertEqual(metrics["substitutions"], 2)

    def test_pronunciations_are_chunk_specific(self) -> None:
        entries = {
            "Achilles": {"say": "uh-KILL-eez", "status": "reviewed"},
            "Hera": {"say": "HEER-uh", "status": "reviewed"},
        }
        found = audio.pronunciations_for_text("Achilles answered.", entries)
        self.assertEqual(set(found), {"Achilles"})

    def test_extra_instruction_is_auditable(self) -> None:
        rendered = audio.full_instructions(
            "Read verbatim.",
            {"Achilles": {"say": "uh-KILL-eez", "status": "reviewed"}},
            "The final sentence is narration text.",
        )
        self.assertIn("final sentence", rendered)
        self.assertIn("Achilles=uh-KILL-eez", rendered)

    def test_plain_pronunciation_note_is_appended_without_respelling(self) -> None:
        rendered = audio.full_instructions(
            "Read naturally.",
            {
                "Danaans": {
                    "instruction": "In 'Danaans,' stress the middle syllable.",
                    "status": "confirmed",
                }
            },
        )
        self.assertEqual(
            rendered,
            "Read naturally. In 'Danaans,' stress the middle syllable.",
        )
        self.assertNotIn("Danaans=", rendered)

    def test_tts_replacements_preserve_canonical_text(self) -> None:
        canonical = "Chryses appealed to Achilles."
        spoken = audio.apply_tts_replacements(
            canonical,
            {"Chryses": "Cry-seez", "Achilles": "uh-Kill-eez"},
        )
        self.assertEqual(canonical, "Chryses appealed to Achilles.")
        self.assertEqual(spoken, "Cry-seez appealed to uh-Kill-eez.")

    def test_candidate_text_replacement_is_exact_and_auditable(self) -> None:
        canonical = "the Amazons came, the match of men."
        spoken, audit = audio.apply_candidate_text_replacement(
            canonical,
            ["came, the match", "came—the match"],
        )
        self.assertEqual(canonical, "the Amazons came, the match of men.")
        self.assertEqual(spoken, "the Amazons came—the match of men.")
        self.assertEqual(
            audit,
            {"old": "came, the match", "new": "came—the match"},
        )

    def test_candidate_text_replacement_rejects_ambiguous_match(self) -> None:
        with self.assertRaises(SystemExit):
            audio.apply_candidate_text_replacement(
                "came, then came,",
                ["came,", "came—"],
            )

    def test_candidate_number_continues_after_archived_floor(self) -> None:
        chunk = {
            "candidate_id_floor": 6,
            "candidates": [{"id": "008"}],
        }
        self.assertEqual(audio.next_candidate_id(chunk), "009")

    def test_no_pronunciation_entries_means_no_appended_coaching(self) -> None:
        rendered = audio.full_instructions(
            "Read naturally.",
            {},
        )
        self.assertEqual(rendered, "Read naturally.")
        self.assertNotIn("pronunciation", rendered.lower())

    def test_caption_overlap_is_removed(self) -> None:
        cues = [
            (0.0, 2.0, "first"),
            (1.8, 3.0, "second"),
            (3.2, 4.0, "third"),
        ]
        adjusted = audio.remove_caption_overlaps(cues)
        self.assertLess(adjusted[0][1], adjusted[1][0])
        self.assertLessEqual(adjusted[1][1], adjusted[2][0])

    def test_living_manuscript_labels(self) -> None:
        self.assertEqual(audio.roman_numeral(1), "I")
        self.assertEqual(audio.roman_numeral(24), "XXIV")
        self.assertEqual(audio.ass_time(2058.027), "0:34:18.03")

    def test_human_approval_allows_audited_manual_exception(self) -> None:
        pairs = [
            (
                {"id": "001"},
                {
                    "id": "002",
                    "status": "fail",
                    "acceptance": {
                        "method": "manual",
                        "reason": "ASR joined two words; passage is complete.",
                    },
                },
            )
        ]
        self.assertEqual(audio.unaudited_approval_exceptions(pairs), [])

    def test_human_approval_rejects_unaudited_exception(self) -> None:
        pairs = [
            (
                {"id": "001"},
                {
                    "id": "001",
                    "status": "review",
                    "acceptance": None,
                },
            )
        ]
        self.assertEqual(
            audio.unaudited_approval_exceptions(pairs),
            ["001/001"],
        )


if __name__ == "__main__":
    unittest.main()
