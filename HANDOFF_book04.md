# Handoff: Translating Iliad Book 4

This is a working setup for translating Homer's Iliad from Ancient Greek into English, book by book. This handoff covers **Book 4** (544 lines) specifically. All paths are relative to the project root: `H:\My Drive\agent-journal\iliad\`.

## What exists and how it fits together

Four files/directories, all keyed to the **same line numbering** (the standard citation system, e.g. "Iliad 4.1"), all derived from the same base edition (Monro-Allen OCT, 3rd ed., via Perseus's `Perseus:text:1999.01.0133`):

1. **`books/book_04.txt`** — the Greek text itself, one line per numbered line. This is your primary source text.
2. **`morphology/book_04.txt`** — word-by-word grammatical analysis for (nearly) every line: each word's dictionary form (lemma), full morphology (case/number/gender or tense/mood/voice/person), and syntactic role in the sentence. Read `morphology/README.md` for the full tag legend (part-of-speech abbreviations, syntactic relation codes like PRED/SBJ/OBJ/ATR/ADV). Source: Perseus's Ancient Greek Dependency Treebank (AGDT) — a multi-annotator scholarly treebank, not one editor's single infallible parse; occasional borderline calls exist, and ~5-15% of lines get folded into an adjacent line's entry rather than listed separately (check the line just before if one seems missing).
3. **`apparatus/book_04.txt`** — the apparatus criticus (manuscript variant record) for Book 4, OCR-extracted from the 1920 Monro-Allen OCT (~98 lines of notes). Tells you where ancient/medieval sources disagree on a reading, and where Alexandrian scholars (Zenodotus, Aristophanes of Byzantium, Aristarchus) marked a line as athetized (`ath.` — suspected spurious). Read `apparatus/README.md` for the abbreviation legend (`ath.`, `Zen.`, `Ar.`, `vulg.`, manuscript sigla, etc.).
   - **Caveat**: this is a mechanical OCR extraction. Greek lemma words inside apparatus notes are sometimes garbled; treat exact wording with some skepticism, but the critical sigla/attributions (who athetized what) are generally reliable. A systematic mis-splitting bug (stray OCR digits creating fake extra line entries) was found and fixed across all 24 books, so entries as they stand should map to real line numbers correctly.
4. **`disputed_lines.md`** (project root) — curated notes on the most significant textual/interpretive disputes across the whole poem. **Book 4 does not have an entry in this curated list** — but the local apparatus for this book has a genuinely notable cluster of athetesis worth knowing about even though it didn't make the project-wide top-15:

   - **4.55–56** (Zeus and Hera's bargain — Hera offers Zeus her three favorite cities, Argos, Sparta, and Mycenae, to destroy in exchange for letting the sack of Troy proceed): athetized by Aristarchus. Confirmed in `apparatus/book_04.txt`: `Line 55-56: ath. Ar`. This is a thematically striking passage to find athetized — Hera essentially offering up her own cult centers — so worth a translator's note if you cover it, regardless of whether you follow the athetesis in your rendering.
   - **4.195–197** (part of the scene where Machaon is summoned to treat Menelaus's wound after Pandarus breaks the truce): athetized by Aristarchus, who separately marked the nearly-identical lines 205–207 elsewhere in the book — Aristarchus considered one of the two repeated passages spurious. Confirmed: `Line 195-197: ath. hic Ar. (= 205-207)`.
   - **4.407–409**: athetized by Aristarchus (see `apparatus/book_04.txt`, `Line 407-409: ath. Ar`) — part of Sthenelus's retort to Agamemnon's rebuke of Diomedes, claiming the sons of the Seven Against Thebes surpassed their fathers. Worth checking if translating that exchange.
   - Smaller individual athetesis at **4.117, 4.140, 4.149, 4.320** — see `apparatus/book_04.txt` directly for details on each.

## What's NOT provided (know this going in)

- No interlinear or reference English translation — this is a from-scratch translation setup, not a trot/crib.
- No lexicon — for a word whose lemma in `morphology/` isn't enough to pin down precise meaning/nuance, you'll need outside reference (e.g. LSJ, Cunliffe's *Lexicon of the Homeric Dialect*).
- The apparatus is OCR'd from a public-domain 1920 edition, not the modern standard (West's Teubner, still in copyright) — treat it as "a good rough index," not a definitive critical edition.
- No meter/scansion data.

**Data-integrity note (2026-07)**: `books/book_04.txt` was regenerated after a bug was found in the original text-extraction script — it had silently omitted `<l>` (line) elements nested inside `<q>` (quoted-speech) XML wrappers, dropping large chunks of dialogue from every book project-wide (Book 4 alone was previously missing 242 lines out of 544 — nearly half, including the entirety of the Zeus/Hera bargain dialogue and much of the divine council). Book 4 is now confirmed complete (544/544 lines, no gaps). If you're working from a copy of `books/book_04.txt` saved/exported before this date, re-fetch it.

## Suggested approach

1. Read `books/book_04.txt` straight through once for overall sense and narrative shape: the divine council on Olympus and Zeus/Hera's bargain over Troy's fate, Athena's descent to incite Pandarus to break the truce by shooting Menelaus, the wounding of Menelaus and Machaon's treatment of it, and Agamemnon's inspection/rousing of the Achaean troops leading into the first full battle of the poem.
2. Work line-by-line or in short sense-units, using `morphology/book_04.txt` to confirm parsing of anything grammatically ambiguous.
3. Check `apparatus/book_04.txt` at any line where the text seems corrupt, metrically odd, or where you want to know if ancient scholars flagged it — especially the Zeus/Hera bargain (55–56) and the repeated Machaon-summons lines (195–197 / 205–207) per the notes above.
4. Book 4 opens the poem's battle narrative — if you haven't yet settled conventions for combat vocabulary (weapon names, wound descriptions, formulaic "and so-and-so fell" death-lines), this is the first book where you'll need them; decisions made here will recur constantly through the rest of the poem.
5. Carry forward epithet/formula conventions established in Books 1–3 (check `translation/CONVENTIONS.md` if it exists yet).

## First lines for orientation (verified against the corrected, complete text)

```
Line 1:   οἳ δὲ θεοὶ πὰρ Ζηνὶ καθήμενοι ἠγορόωντο
Line 2:   χρυσέῳ ἐν δαπέδῳ, μετὰ δέ σφισι πότνια Ἥβη
Line 3:   νέκταρ ἐοινοχόει· τοὶ δὲ χρυσέοις δεπάεσσι
```
