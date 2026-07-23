# Handoff: Translating Iliad Book 2

This is a working setup for translating Homer's Iliad from Ancient Greek into English, book by book. This handoff covers **Book 2** (877 lines) specifically. All paths are relative to the project root: `H:\My Drive\agent-journal\iliad\`.

## What exists and how it fits together

Four files/directories, all keyed to the **same line numbering** (the standard citation system, e.g. "Iliad 2.1"), all derived from the same base edition (Monro-Allen OCT, 3rd ed., via Perseus's `Perseus:text:1999.01.0133`):

1. **`books/book_02.txt`** — the Greek text itself, one line per numbered line. This is your primary source text.
2. **`morphology/book_02.txt`** — word-by-word grammatical analysis for (nearly) every line: each word's dictionary form (lemma), full morphology (case/number/gender or tense/mood/voice/person), and syntactic role in the sentence. Format:
   ```
   Line 1:
       μῆνιν (μῆνις) [noun fem acc sg] {OBJ}
       ...
   ```
   Read `morphology/README.md` for the full tag legend (part-of-speech abbreviations, syntactic relation codes like PRED/SBJ/OBJ/ATR/ADV). Source: Perseus's Ancient Greek Dependency Treebank (AGDT) — a multi-annotator scholarly treebank, not one editor's single infallible parse; occasional borderline calls exist, and ~5-15% of lines get folded into an adjacent line's entry rather than listed separately (check the line just before if one seems missing). Book 2 is long (877 lines) and includes the Catalogue of Ships, which is dense with proper names (place names, tribal/contingent leaders) — expect the treebank's parsing of these to be more mechanical/formulaic than the narrative sections.
3. **`apparatus/book_02.txt`** — the apparatus criticus (manuscript variant record) for Book 2, OCR-extracted from the 1920 Monro-Allen OCT (~189 lines of notes). Tells you where ancient/medieval sources disagree on a reading, and where Alexandrian scholars (Zenodotus, Aristophanes of Byzantium, Aristarchus) marked a line as athetized (`ath.` — suspected spurious). Read `apparatus/README.md` for the abbreviation legend (`ath.`, `Zen.`, `Ar.`, `vulg.`, manuscript sigla, etc.).
   - **Caveat**: this is a mechanical OCR extraction. Greek lemma words inside apparatus notes are sometimes garbled; treat exact wording with some skepticism, but the critical sigla/attributions (who athetized what) are generally reliable. A systematic mis-splitting bug (stray OCR digits creating fake extra line entries) was found and fixed across all 24 books, so entries as they stand should map to real line numbers correctly.
4. **`disputed_lines.md`** (project root) — curated notes on the most significant textual/interpretive disputes in the whole poem. **Book 2 has more entries here than most books** — this is one of the most textually contested books in the Iliad:

   - **2.193–197** (Odysseus rebuking the common soldiers): obelized/athetized by Aristarchus as tonally/logically inconsistent with the surrounding scene, and independently missing from a quotation of the passage in Xenophon's *Memorabilia* (1.2.56) — two independent lines of evidence the passage may not be original. Confirmed in `apparatus/book_02.txt`: `Line 193-197: ath. Ar. (om. Xen. mem. i. 2. 56)`. Affects how imperious/violent Odysseus's crowd-control rhetoric reads — worth a translator's decision on tone.
   - **Catalogue of Ships, 2.494–759**: long suspected (on modern "Analyst" grounds — distinct meter/diction, encyclopedic content) as an originally independent composition (possibly Boeotian/Hesiodic) later inserted into the poem. Scholarly opinion is split on whether to treat it as integral or as an inserted "document"; this is a matter of ongoing modern debate, not primarily a manuscript-variant question, though the apparatus does show `Line 494-877: om.` in several manuscripts (i.e., real ancient/medieval textual instability around the whole span, consistent with the suspicion). This is a pacing/register decision for you as translator: how "epic-formulaic" vs. "list-like" should the Catalogue read compared to the narrative sections around it?
   - **2.557–558** (Ajax's contingent — the Salamis lines): athetized by Aristarchus, and ancient tradition (Strabo, Diogenes Laertius) reports an accusation that **Solon or Pisistratus forged this line** to bolster Athens's territorial claim to Salamis against Megara. This is one of the most famous individual "forged line" stories in the whole poem — genuinely worth a footnote if you're translating the Catalogue in full. Confirmed in `apparatus/book_02.txt`: `Line 558: ath. Ar. ... inseruisse seu Pisistratum seu Solonem refert Strab. ... D.L. i[.48]`.

**Data-integrity note (2026-07)**: `books/book_02.txt` was regenerated after a bug was found in the original text-extraction script — it had silently omitted `<l>` (line) elements nested inside `<q>` (quoted-speech) XML wrappers, dropping large chunks of dialogue from every book project-wide (Book 2 alone was previously missing 283 lines out of 877). Book 2 is now confirmed complete (877/877 lines, no gaps). If you're working from a copy of `books/book_02.txt` saved/exported before this date, re-fetch it.

## What's NOT provided (know this going in)

- No interlinear or reference English translation — this is a from-scratch translation setup, not a trot/crib.
- No lexicon — for a word whose lemma in `morphology/` isn't enough to pin down precise meaning/nuance, you'll need outside reference (e.g. LSJ, Cunliffe's *Lexicon of the Homeric Dialect*). This matters especially for the Catalogue's place names and dialectal forms.
- The apparatus is OCR'd from a public-domain 1920 edition, not the modern standard (West's Teubner, still in copyright) — treat it as "a good rough index," not a definitive critical edition.
- No meter/scansion data.
- No gazetteer/map for the Catalogue of Ships place names — if you want to identify real-world locations for the ~29 contingents listed, that's outside this project's current scope.

## Suggested approach

1. Read `books/book_02.txt` straight through once for overall sense and narrative shape: Zeus's deceptive dream to Agamemnon, the assembly and the (failed) test of the troops' resolve, Odysseus rallying the army and rebuking Thersites, the omen at Aulis recalled, and then the Catalogue of Ships (a long structural set-piece listing every Greek contingent, followed by a shorter Trojan catalogue at the end of the book).
2. Consider treating the Catalogue (roughly 494–877) as a distinct translation pass from the narrative portions (1–493) — many translators shift register here (more list-like, incantatory), and it may be easier to work through once you've found your voice in the narrative sections first.
3. Work line-by-line or in short sense-units, using `morphology/book_02.txt` to confirm parsing of anything grammatically ambiguous.
4. Check `apparatus/book_02.txt` at any line where the text seems corrupt, metrically odd, or where you want to know if ancient scholars flagged it — this book has an unusually high density of flagged material for a non-"contested whole book" (compare Book 10 or Book 20), so it's worth checking more liberally here than in a typical book.
5. Flag 2.193–197 and 2.557–558 explicitly per the notes above; decide how (or whether) to footnote the Catalogue's contested status as a whole.
6. Carry forward any epithet/formula translation choices you made in Book 1 for consistency (e.g. "swift-footed Achilles," "lord of men Agamemnon") — Book 2 reuses many of the same formulas.

## First lines for orientation (already verified correct)

```
Line 1:   ἄλλοι μέν ῥα θεοί τε καὶ ἀνέρες ἱπποκορυσταὶ
Line 2:   εὗδον παννύχιοι, Δία δ᾽ οὐκ ἔχε νήδυμος ὕπνος,
Line 3:   ἀλλ᾽ ὅ γε μερμήριζε κατὰ φρένα ὡς Ἀχιλῆα
```
