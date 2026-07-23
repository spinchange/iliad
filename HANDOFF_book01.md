# Handoff: Translating Iliad Book 1

This is a working setup for translating Homer's Iliad from Ancient Greek into English, book by book. This handoff covers **Book 1** (611 lines) specifically. All paths are relative to the project root: `H:\My Drive\agent-journal\iliad\`.

## What exists and how it fits together

Four files/directories, all keyed to the **same line numbering** (the standard citation system, e.g. "Iliad 1.1"), all derived from the same base edition (Monro-Allen OCT, 3rd ed., via Perseus's `Perseus:text:1999.01.0133`):

1. **`books/book_01.txt`** — the Greek text itself, one line per numbered line. This is your primary source text.
2. **`morphology/book_01.txt`** — word-by-word grammatical analysis for (nearly) every line: each word's dictionary form (lemma), full morphology (case/number/gender or tense/mood/voice/person), and syntactic role in the sentence. Format:
   ```
   Line 1:
       μῆνιν (μῆνις) [noun fem acc sg] {OBJ}
       ἄειδε (ἀείδω) [verb pres imperv act 2 sg] {PRED_CO}
       ...
   ```
   Read `morphology/README.md` for the full tag legend (part-of-speech abbreviations, syntactic relation codes like PRED/SBJ/OBJ/ATR/ADV). Source: Perseus's Ancient Greek Dependency Treebank (AGDT) — a multi-annotator scholarly treebank, not one editor's single infallible parse; occasional borderline calls exist, and ~5-15% of lines get folded into an adjacent line's entry rather than listed separately (check the line just before if one seems missing).
3. **`apparatus/book_01.txt`** — the apparatus criticus (manuscript variant record) for Book 1, OCR-extracted from the 1920 Monro-Allen OCT. Tells you where ancient/medieval sources disagree on a reading, and where Alexandrian scholars (Zenodotus, Aristophanes of Byzantium, Aristarchus) marked a line as athetized (`ath.` — suspected spurious). Read `apparatus/README.md` for the abbreviation legend (`ath.`, `Zen.`, `Ar.`, `vulg.`, manuscript sigla, etc.).
   - **Caveat**: this is a mechanical OCR extraction. Greek lemma words inside apparatus notes are sometimes garbled; treat exact wording with some skepticism, but the critical sigla/attributions (who athetized what) are generally reliable. A systematic mis-splitting bug (stray OCR digits creating fake extra line entries) was found and fixed across all 24 books, so entries as they stand should map to real line numbers correctly.
4. **`disputed_lines.md`** (project root) — curated notes on the most significant textual/interpretive disputes in the whole poem, cross-referenced against the local apparatus where applicable. **For Book 1 specifically**, the relevant entry is:
   - **1.4–5** ("...made their bodies a feast for dogs and all birds"): Zenodotus athetized both lines; separately his text is reported to have read *daita* ("banquet") at line 5 instead of the standard reading — debated since antiquity as either grotesquely apt (an ironic "feast" for scavengers) or a corruption. Confirmed in `apparatus/book_01.txt`: `Line 4-5: ath. Zen` and `Line 5: ...δαῖτα Zen. teste Ath.` This is worth a translator's decision (and possibly a footnote) on tone at the very opening of the poem.

No other Book 1 lines are in the curated disputed-lines list, but the local apparatus (`apparatus/book_01.txt`) has ~121 line-entries covering many smaller variants throughout the book — worth checking against as you go, especially at any line where your own read of the Greek feels uncertain or where a published translation surprises you.

**Data-integrity note (2026-07)**: `books/book_01.txt` was regenerated after a bug was found in the original text-extraction script — it had silently omitted `<l>` (line) elements nested inside `<q>` (quoted-speech) XML wrappers, dropping large chunks of dialogue from every book project-wide. Book 1 is now confirmed complete (611/611 lines, no gaps). If you're working from a copy of `books/book_01.txt` saved/exported before this date, re-fetch it — it was likely missing roughly a third of the book's lines (mostly speeches), including parts of Chryses' prayer.

## What's NOT provided (know this going in)

- No interlinear or reference English translation — this is a from-scratch translation setup, not a trot/crib.
- No lexicon — for a word whose lemma in `morphology/` isn't enough to pin down precise meaning/nuance, you'll need outside reference (e.g. LSJ, Cunliffe's *Lexicon of the Homeric Dialect*).
- The apparatus is OCR'd from a public-domain 1920 edition, not the modern standard (West's Teubner, still in copyright) — treat it as "a good rough index," not a definitive critical edition.
- No meter/scansion data.

## Suggested approach

1. Read `books/book_01.txt` straight through once for overall sense and narrative shape (Achilles' wrath, the quarrel with Agamemnon, Chryses' prayer, the plague, the assembly, the seizure of Briseis, Thetis's intervention, the divine assembly on Olympus).
2. Work line-by-line or in short sense-units, using `morphology/book_01.txt` to confirm parsing of anything grammatically ambiguous (this is Homeric Greek — expect dialect forms, unusual verb endings, and formulaic epithets that a modern-Greek-trained eye might parse wrong).
3. Check `apparatus/book_01.txt` at any line where the text seems corrupt, metrically odd, or where you want to know if ancient scholars flagged it.
4. Flag lines 4-5 explicitly per the note above — decide (and note) how you're handling the "feast" image tonally.
5. Keep a running note of translation choices for recurring epithets/formulas (e.g. "swift-footed Achilles," "lord of men Agamemnon") — Book 1 sets the pattern for the whole poem, so consistency decisions made here should be documented for later books.

## First lines for orientation (already verified correct)

```
Line 1:   μῆνιν ἄειδε θεὰ Πηληϊάδεω Ἀχιλῆος
Line 2:   οὐλομένην, ἣ μυρίʼ Ἀχαιοῖς ἄλγεʼ ἔθηκε,
Line 3:   πολλὰς δʼ ἰφθίμους ψυχὰς Ἄϊδι προΐαψεν
```
