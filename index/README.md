# Index of names and places — build pipeline

A four-phase pipeline that turns the finished translation into an index of every
named person, god, people, and place in the poem, each with an anglicized
pronunciation, its fixed epithets, its aliases, its kin, and real line citations.
It is a port of the companion Odyssey project's pipeline (`..\odyssey\index`),
kept deliberately parallel so the two indexes read as one work and shared names
are pronounced the same way in both.

**Status: complete for the 301 classified headwords.** `index.md` is built —
301 entries with pronunciations injected. What remains is the 735-name tail in
`tail-unclassified.md`, which is a separate scoping decision (see below).

Phase 3 was written by eight parallel writers, one per slice, each required to
read the cited lines before making any claim rather than writing from knowledge
of Homer. That rule earned its cost: it caught roughly forty factual errors at
write time, and it exposed four defects in files that were supposed to be
authoritative — see "What the entry-writing found upstream" below.

## The phases

| Phase | Tool | Produces |
|---|---|---|
| 1. Extraction | `tools/build_index.py` | `occurrences.{json,md}` — every capitalized token in the verse body with every citation |
| 2. Canon | *(hand-written)* | `canon.md` — categories, alias resolution, genealogy, homonyms |
| 2b. Registry | `tools/build_registry.py` | `registry.{json,md}` — the classified headword list + coverage audit |
| — Pronunciation | `tools/seed_pronunciations.py` | `pronunciations.tsv` — inherits shared rows from the Odyssey, reports gaps |
| 3. Slicing | `tools/make_slices.py` | `entries/_worklist-NN.md` — balanced, self-contained work packets |
| 3. Writing | *(writers)* | `entries/entries-NN.md` — per the `entries/WRITER-BRIEF.md` contract |
| 4. Merge | `tools/merge_index.py` | `index.md` — alphabetized, with `*Say:*` injected |

Run in order:

```powershell
python tools\build_index.py           # refresh occurrences
python tools\seed_pronunciations.py   # report pronunciation gaps (--write to inherit)
python tools\build_registry.py        # refresh registry + coverage audit
python tools\make_slices.py --slices 8
#   ... writers produce index/entries/entries-NN.md ...
python tools\merge_index.py           # validate + assemble index.md
```

## Where the numbers stand

- **15,687 verse lines** scanned across 24 books; the extractor self-checks every
  book's last line number and line count against the canonical Monro-Allen
  numbering, accounting for the three documented gaps (9.458–461, 11.543, 14.269)
  where the printed Greek is genuinely short. A boundary regression fails loudly
  rather than silently producing a wrong index.
- **1,064 candidate tokens** after the function-word stoplist.
- **301 classified headwords, all written** — Mortals 174, Gods 41, Peoples 27,
  Places 51, Animals/objects/sky 8. Nothing above 4 hits is unclassified.
- **275 of 301 entries carry a pronunciation.** The 26 without are correctly
  row-less: transparent English (Troy, Crete, Sparta, Hector, Paris) and the
  personifications (Dawn, Sleep, Strife, Panic, Fate, the Muses).
- **161 citation flags**, every one reviewed against the text and recorded with a
  justification in `entries/_flags-NN.md`. They are advisory by design: most are
  epithet-register first-refs where the line carries the epithet substantively and
  never the name, or death-blows that name the killer rather than the victim.
- **735 real names still unclassified**, listed in `tail-unclassified.md`. Every
  token in the tail was reviewed by hand (2026-07-26): 167 were non-names and are
  now stoplisted, recorded in `noise-stoplist.md`. Of the 735, **535 occur exactly
  once** in the poem and **211 occur only in Book 2**, the Catalogue of Ships —
  those are list-entries (towns, contingent leaders) that likely want one
  gazetteer table rather than 211 separate entries.
- **403 pronunciation rows**, of which 191 are inherited verbatim from the Odyssey
  project. Names correctly carrying no row: transparent English (Troy, Crete,
  Thebes) and the personifications (Dawn, Sleep, Strife, the Muses).

## What the entry-writing found upstream

Writing an index entry forces a line-by-line reconciliation of the registers
against the text, which is why this phase found bugs that the audit passes did
not. All four were confirmed against the poem before being fixed:

- **`CONVENTIONS.md` attributed χρυσόθρονος "of the golden throne" to Dawn.** It
  is Hera's — all four occurrences are hers or Zeus's. The row sat directly below
  two Dawn epithets, which is what misled. Now tagged `(Hera)`.
- **`CONVENTIONS.md` filed the patronymic Κρονίδης/Κρονίων at 1.397.** It falls on
  1.398.
- **The registry folded the token `Xanthus` into Scamander.** That one spelling is
  four things: Troy's river, the Lycian river, Achilles' immortal horse, and a man
  Diomedes kills. The fold made Scamander's hit-count and ref-list wrong.
- **Three registry notes asserted what the poem does not say** — that Hebe is
  "Ares' nurse", that Ilus is glossed as Ilion's eponym, and that Hector killed
  Protesilaus. The text withholds Protesilaus' killer ("a Dardanian man had
  killed him", 2.701); the other two are simply absent from it.

The writers also found homonyms `canon.md` had not registered (Eurypylus of Cos;
a third Thoas; three Echius, Epistrophus and Enops each) and, where the poem
declines to say whether two bearers of a name are one man, left them unmerged and
said so.

## Design notes worth knowing

**The verse body is found by the horizontal rules, not by line shape.** Each
translation file is commentary, then a rule, then the verse, then a rule, then the
footnote apparatus. The commentary cites line numbers in prose ("318 (did the god
…)") that look exactly like verse lines, and footnote continuations are indented
the same way. Keying on the rules is what makes the scan exact.

**Patronymics are headwords, not aliases.** Atreus (181 hits), Peleus (146),
Tydeus (109), Menoetius (38), Aeacus (25) rank among the poem's most frequent
tokens, and in most of those hits the father is not the referent — "Tydeus' son"
means Diomedes. Folding them into the son would inflate his count with a hundred
refs that never name him, so each father keeps his own entry and `canon.md`'s
alias table carries the resolution. This is the single biggest structural
difference from the Odyssey index.

**Epithet-only tokens are folded.** "Argus" occurs only inside Hermes' fixed
epithet "the slayer of Argus," and "Gerenian" only inside Nestor's — both verified
against every occurrence, both folded into the god or man rather than given a
spurious entry.

**The stoplist is cumulative and documented in place.** It grew in labeled blocks
— function words, battle-narrative openers, compass winds, and finally the
2026-07-26 tail sweep of 167 non-names. Each block says why its words are there.
Personifications that look like common nouns (Dawn, Sleep, Strife, Panic, Fate,
Death, Blindness, the Muses) are deliberately *not* stoplisted: they are gods in
this poem and are classified as such in the registry.

**A stoplisted registry token is a fatal build error.** `build_registry.py` asserts
that no classified token appears in `build_index.py`'s `STOP`, before it writes
anything. The failure it prevents is silent: a token that is both classified and
stoplisted never reaches `occurrences.json`, so its headword quietly loses those
hits, or vanishes from the index entirely while still looking present in
`REGISTRY`. This is not theoretical — the guard caught **Bear** on its first run
(the constellation at 18.487, stoplisted by an earlier pass because "Bear up" also
opens three imperatives). The stoplist is per-token and all-or-nothing, so when a
word is both a name and an opener, the name wins.

**The merge gate is strict about coverage and advisory about citations.** Missing
or extra entries block the build, because positional misalignment would silently
attach every later entry to the wrong headword. Citations that aren't in a
headword's occurrence set are only flagged: a writer may legitimately cite a scene
line where the figure is present under an epithet. Both behaviors were confirmed
on a live six-entry run before the pipeline was handed off.

## Authority

Two upstream files outrank anything written here:

- `translation/CONVENTIONS.md` — name spellings and the fixed English of every
  epithet, built book by book across the whole translation.
- `index/occurrences.json` — every citation. Refs are real or they are wrong.
