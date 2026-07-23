# Apparatus Criticus — Homer's Iliad (Monro & Allen, OCT 3rd ed., 1920)

This directory contains a mechanically extracted apparatus criticus (critical
apparatus) for all 24 books of the Iliad, derived from OCR'd scans of the
Oxford Classical Text edition edited by David B. Monro and Thomas W. Allen
("Homeri Opera," 3rd ed., Oxford, 1920):

- Volume I (Iliad Books 1–12): archive.org item `homerioperarecog01homeuoft`
- Volume II (Iliad Books 13–24): archive.org item `homerioperarecog02homeuoft`

Files `book_01.txt` through `book_24.txt` each contain the apparatus entries
for one book of the Iliad, extracted from the material printed below the rule
on each page (the main Greek poetic text at the top of each page is *not*
included here — it has already been digitized separately as
`iliad_greek_full.txt` in the parent directory).

## How this was produced

The two source volumes are raw OCR text (djvu text layer) of the printed
book. On each page, the apparatus criticus is a dense block of compact notes
keyed by Iliad line number, e.g.:

```
46-47 ath. Zen. 47 éèouds) eAvodels Zen. 56 dpîro Zen.
59 raAiurAayx0évras Ar. vulg.: mdAiw rAayx0évras L8 L!° Le!
```

A script identified the apparatus block on each page (as distinct from the
Greek verse text above it) using the density of recognizable critical-Latin
vocabulary (`Zen.`, `Ar.`, `ath.`, `vulg.`, etc.) and citation-number patterns,
then joined and re-split the OCR'd lines into per-line-number entries. Running
page headers ("N. IAIAAOZ X") were used to track which Iliad book each page
belonged to, tolerating the many different ways the header itself got
garbled by OCR.

## Known limitations (read before relying on this for scholarship)

- **The Greek is frequently garbled.** Polytonic Greek diacritics and some
  letterforms did not survive OCR reliably, especially in Volume I (Books
  1–12), where Greek often comes out as a transliteration-like jumble of
  Latin lookalike characters. Volume II (Books 13–24) fared better and
  usually keeps real Greek Unicode. Critical sigla and Latin abbreviations
  (the actual scholarly apparatus) survive much better than the Greek lemma
  text in both volumes, since they are mostly plain Latin characters.
- **Line numbers are best-effort.** Iliad line numbers were recovered from
  citation-like digit patterns in the OCR'd apparatus text. Most are correct,
  but a small number of entries are mis-split or mislabeled: e.g. a
  cross-reference to a *different* book's line (the apparatus sometimes cites
  another book with a single Greek letter, like "cf. E 793" for Book 5 line
  793) can be misread as a same-book line number; a footnote/page number in a
  cited secondary source (e.g. "cit. Ammian. xxiii. 6. 62") can occasionally
  be mistaken for a line-number citation. Entries are kept in the original
  page order (itself ascending by line number) rather than re-sorted
  numerically, precisely to avoid scattering these mislabeled numbers out of
  context.
- **Entries with no recoverable line number** are collected at the end of
  each book's file under "Unplaced fragments."
- **A handful of pages (roughly half a dozen out of ~200) were too
  OCR-corrupted to extract at all** and were skipped rather than guessed at;
  affected books carry a note near the top of their file naming the
  approximate gap. This affects small portions of Books 6, 16, 19, 20, and 21.
- **Quoted variant readings.** Occasionally the apparatus itself quotes a full
  alternate line of Greek verse under discussion (e.g. Zenodotus's rejected
  opening lines to the Iliad, or the disputed "Catalogue of Ships" verses
  about Ajax's contingent) — these appear as apparatus content, not leaked
  primary text, and are retained.
- This is a **mechanical extraction, not a critical edition**. Treat it as a
  rough-and-ready index into where variants/athetesis/manuscript notes exist,
  and consult the original OCT (or a proper digital edition) for anything
  that matters for actual scholarship.

## Legend of common abbreviations and sigla

| Abbreviation | Meaning |
|---|---|
| `ath.` | *athetized* — marked as spurious/rejected by an ancient editor (the line is kept in the text but flagged as probably not genuine) |
| `Zen.` | **Zenodotus** of Ephesus, earliest Alexandrian editor of Homer (3rd c. BC) |
| `Ar.` | **Aristarchus** of Samothrace, the most authoritative ancient Homeric critic (2nd c. BC) |
| `Aristoph.` | **Aristophanes of Byzantium**, Alexandrian scholar (3rd–2nd c. BC), predecessor of Aristarchus |
| `vulg.` | *vulgate* — the common/majority reading found in most manuscripts |
| `om.` | *omittit/omittunt* — omitted by (the manuscript(s)/editor named) |
| `codd.` | *codices* — (all/the majority of) the manuscripts |
| `cf.` | *confer* — compare (with the line/work cited) |
| `Hdn.` | **Herodian**, 2nd-century AD grammarian, son of Apollonius Dyscolus, wrote on Homeric accentuation/prosody |
| `Did.` | **Didymus**, 1st-century BC Alexandrian scholar who compiled earlier critical work |
| `Eust.` | **Eustathius**, 12th-century AD Archbishop of Thessalonica, author of extensive Homeric commentaries |
| `v.l.` / `v. l.` | *varia lectio* — variant reading |
| `v.l. ant.` | *varia lectio antiqua* — an ancient variant reading (pre-dating the medieval MSS) |
| `teste` | *on the testimony of* (the source named attests to this reading) |
| `fort.` | *fortasse* — perhaps/possibly |
| `quidam` | *some (manuscripts/scholars)* — an unspecified subset |
| `ss.` | *supra scriptum/scripta* — written above (a marginal/interlinear correction) |
| `uv.` | *ut videtur* — as it seems/apparently |
| `yp.` (γράφεται) | *it is written/read as* — introduces a variant noted in a manuscript margin |
| `s` | *scholium, scholia* — ancient/Byzantine marginal commentary |
| `qu.` | *quidam* — some manuscripts/authorities |
| `post` | *after* (line N) — used when a note concerns material following that line |
| `pro` | *instead of* (line(s) N) — introduces a quoted variant/rejected reading substituted for the standard text |
| Single/double letters, sometimes with superscript numbers (e.g. `L¹⁹`, `V¹²`, `Bm⁵`, `P²`) | **Manuscript sigla** — abbreviations for individual medieval manuscripts or papyri in Monro & Allen's apparatus |
| `P` + number (e.g. `P⁹`, `P¹²`) | A papyrus witness |
| Roman numerals after a citation (e.g. `Strab. 296`, `Plut. Sol. 10`) | Page/chapter references into the ancient secondary source being cited, not Iliad line numbers |

Names of other ancient scholars/grammarians that appear occasionally:
**Rhianus**, **Sosigenes**, **Aristoxenus**, **Apollonius (Rhodius/Dyscolus)**,
**Herodorus**, **Strabo**, **Plato**, **Porphyry**, **Plutarch**, **Nicanor**,
**Demetrius (Ixion)**, **Crates**, **Pindar**, **Hesiod**, **Antimachus**,
**Heraclides**, **Dionysius (of Sidon/Thrax)**, **Posidonius**, **Longinus**,
**Ammonius**, **Callistratus**, **Tyrannio**.

## Directory contents

- `book_01.txt` – `book_24.txt`: apparatus entries for each Iliad book, in
  page (≈ line-number ascending) order.
- `README.md`: this file.
