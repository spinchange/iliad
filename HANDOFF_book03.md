# Handoff: Translating Iliad Book 3

This is a working setup for translating Homer's Iliad from Ancient Greek into English, book by book. This handoff covers **Book 3** (461 lines) specifically. All paths are relative to the project root: `H:\My Drive\agent-journal\iliad\`.

## What exists and how it fits together

Four files/directories, all keyed to the **same line numbering** (the standard citation system, e.g. "Iliad 3.1"), all derived from the same base edition (Monro-Allen OCT, 3rd ed., via Perseus's `Perseus:text:1999.01.0133`):

1. **`books/book_03.txt`** — the Greek text itself, one line per numbered line. This is your primary source text.
2. **`morphology/book_03.txt`** — word-by-word grammatical analysis for (nearly) every line: each word's dictionary form (lemma), full morphology (case/number/gender or tense/mood/voice/person), and syntactic role in the sentence. Format:
   ```
   Line 1:
       αὐτὰρ (αὐτάρ) [conj] {AuxY}
       ...
   ```
   Read `morphology/README.md` for the full tag legend (part-of-speech abbreviations, syntactic relation codes like PRED/SBJ/OBJ/ATR/ADV). Source: Perseus's Ancient Greek Dependency Treebank (AGDT) — a multi-annotator scholarly treebank, not one editor's single infallible parse; occasional borderline calls exist, and ~5-15% of lines get folded into an adjacent line's entry rather than listed separately (check the line just before if one seems missing).
3. **`apparatus/book_03.txt`** — the apparatus criticus (manuscript variant record) for Book 3, OCR-extracted from the 1920 Monro-Allen OCT (~91 lines of notes). Tells you where ancient/medieval sources disagree on a reading, and where Alexandrian scholars (Zenodotus, Aristophanes of Byzantium, Aristarchus) marked a line as athetized (`ath.` — suspected spurious). Read `apparatus/README.md` for the abbreviation legend (`ath.`, `Zen.`, `Ar.`, `vulg.`, manuscript sigla, etc.).
   - **Caveat**: this is a mechanical OCR extraction. Greek lemma words inside apparatus notes are sometimes garbled; treat exact wording with some skepticism, but the critical sigla/attributions (who athetized what) are generally reliable. A systematic mis-splitting bug (stray OCR digits creating fake extra line entries) was found and fixed across all 24 books, so entries as they stand should map to real line numbers correctly.
4. **`disputed_lines.md`** (project root) — curated notes on the most significant textual/interpretive disputes across the whole poem. **Book 3 does not have an entry in this curated list** — but the local apparatus for this book does contain genuine athetesis worth knowing about even though it wasn't significant enough to make the project-wide top-15 list:

   - **3.18–20 / 3.19–20** (Paris brandishing his weapons — leopard skin, bow, sword, two spears — and challenging any Achaean champion to single combat): a rare case where **two different ancient editors athetized overlapping but different spans** — Zenodotus flagged 18–20, while Aristarchus separately flagged only 19–20. Confirmed in `apparatus/book_03.txt`: `Line 18-20: ath. Zen` and `Line 19-20: ath. Ar`. Worth knowing if translating Paris's introduction closely, since it shows the description of his gear was unstable across the ancient editorial tradition even though modern editions print it without brackets.
   - **3.108–110** and **3.144**, **3.334–335** (Zenodotus only), **3.428–436**: further individual athetesis by Aristarchus scattered through the book (see `apparatus/book_03.txt` directly — `Line 108-110: ath. Ar`, `Line 144: ath. Ar`, `Line 334-335: ath. Zen`, `Line 428...432-436 ath. Ar`). None of these rise to the significance of the Paris-arming lines above, but check them if your translation of the surrounding passage feels textually uncertain.

## What's NOT provided (know this going in)

- No interlinear or reference English translation — this is a from-scratch translation setup, not a trot/crib.
- No lexicon — for a word whose lemma in `morphology/` isn't enough to pin down precise meaning/nuance, you'll need outside reference (e.g. LSJ, Cunliffe's *Lexicon of the Homeric Dialect*).
- The apparatus is OCR'd from a public-domain 1920 edition, not the modern standard (West's Teubner, still in copyright) — treat it as "a good rough index," not a definitive critical edition.
- No meter/scansion data.

**Data-integrity note (2026-07)**: `books/book_03.txt` was regenerated after a bug was found in the original text-extraction script — it had silently omitted `<l>` (line) elements nested inside `<q>` (quoted-speech) XML wrappers, dropping large chunks of dialogue from every book project-wide (Book 3 alone was previously missing 242 lines out of 461 — more than half). Book 3 is now confirmed complete (461/461 lines, no gaps). This book is unusually speech-heavy (most of it is the teichoscopia — Helen naming the Achaean heroes to Priam from the walls — plus the duel negotiations), so it was especially badly affected by the original bug. If you're working from a copy of `books/book_03.txt` saved/exported before this date, re-fetch it.

## Suggested approach

1. Read `books/book_03.txt` straight through once for overall sense and narrative shape: the armies advance, Paris challenges any Achaean to single combat then flinches at the sight of Menelaus, Hector shames him into agreeing to a formal duel with Menelaus for Helen's sake, the truce is sworn, Priam and Helen watch from the walls (the *teichoscopia* — Helen identifies Agamemnon, Odysseus, and Ajax by name for Priam), the duel itself, and Aphrodite's rescue of Paris at the last moment.
2. Work line-by-line or in short sense-units, using `morphology/book_03.txt` to confirm parsing of anything grammatically ambiguous.
3. Check `apparatus/book_03.txt` at any line where the text seems corrupt, metrically odd, or where you want to know if ancient scholars flagged it — especially around 18–20 (Paris's weapons) per the note above.
4. This book is heavy on formal/ceremonial speech (oaths, challenges, Helen's naming-speeches) — a good place to settle translation conventions for formal diplomatic/ritual language that will recur later (e.g. in the embassy of Book 9, or truce scenes).
5. Carry forward epithet/formula conventions established in Books 1–2 (check `translation/CONVENTIONS.md` if it exists yet).

## First lines for orientation (verified against the corrected, complete text)

```
Line 1:   αὐτὰρ ἐπεὶ κόσμηθεν ἅμʼ ἡγεμόνεσσιν ἕκαστοι,
Line 2:   Τρῶες μὲν κλαγγῇ τʼ ἐνοπῇ τʼ ἴσαν ὄρνιθες ὣς
Line 3:   ἠΰτε περ κλαγγὴ γεράνων πέλει οὐρανόθι πρό·
```
