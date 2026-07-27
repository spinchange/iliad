# Pronunciation key — house style

The index gives each non-obvious name a pronunciation in the `*Say:*` field.
This is the house style those respellings follow. It is the same scheme used by
the companion Odyssey project (`..\odyssey\index\pron-key.md`), deliberately, so
that a reader of both books meets one convention and the shared names — Achilles,
Agamemnon, Nestor, Odysseus, and some two hundred more — are respelled
identically in each.

## Convention

**Traditional anglicized pronunciation** — the established English/Latinate
reading — *not* reconstructed ancient Greek. This is the only choice consistent
with the translation's Latinate spellings: you cannot print "Achilles" and say
"a-khil-LEUS." Where the anglicized tradition is itself split (and for these
names it often is), the field gives one respelling and notes the variant with
"*or*".

## Notation

Plain respelling; syllables hyphenated; **primary stress in CAPS**; unstressed
vowels reduced to the schwa `uh`.

### Vowel key (anchor words)

| respell | as in | respell | as in |
|---|---|---|---|
| `a` | c**a**t | `oh` | g**o** |
| `ah` | f**a**ther | `aw` | s**aw** |
| `ay` | d**ay** | `oo` | f**oo**d |
| `air` | c**are** | `yoo` | (eu-) f**ew** |
| `e` | b**e**d | `u` | c**u**p |
| `ee` | s**ee** | `ur` | f**ur** |
| `i` | s**i**t | `uh` | schwa, **a**bout |
| `eye` / `y` | sk**y** | `ow` | n**ow** |

**Consonants:** `g` is hard ("get") unless written `j`; `th` is voiceless
("thin"); Greek χ and Latin `ch` become `k`; `s`, `k`, `z` are always written as
the sound, never the letter.

## The two rules

1. **Sound shifts.** `c` before e/i/y/ae → `s` (Cebriones → seb-); `g` before
   e/i/y → often `j` (Agenor → uh-JEE-nor); `ae`/`oe` → `ee`; `eu` → `yoo`;
   `ei` → `eye`; `ou` → `oo`; final `-es` → `-eez`; `Ps-`/`Cn-`/`Ct-` drop
   the first letter; `ch`/`chi` → `k`.
2. **Stress (the Latin Penult Rule).** Stress the **penult** if it is heavy (long
   vowel, diphthong, or vowel + two consonants); otherwise the **antepenult**.
   Penult weight follows the **Greek vowel quantity**, which `tools/scan.py`
   already computes — so stress placement is checkable against the Greek, not
   guessed.

## Iliad-specific points

- **Diaeresis is kept in the spelling and honored in the respelling.** The
  translation prints Eëtion, Oïleus, Leïtus, Alpheius; the vowels are separate
  syllables (Eëtion = ay-EE-tee-on, not "EE-shun"). See the named-entity register
  in `translation/CONVENTIONS.md`.
- **Two names for one figure get one row each.** Paris and Alexandros are both
  headwords (the translation uses both per the Book 3 policy); so are Ilion and
  Troy, Phoebus and Apollo, Cypris and Aphrodite, Enyalius and Ares.
- **Patronymic adjectives that function as names are respelled** — Telamonian,
  Gerenian, Atreides-type forms — because a reader meets them as the surface
  form and needs them said aloud. Purely descriptive epithets are not.
- **Homonyms are disambiguated in the entry, not the respelling.** The Iliad has
  several men to a name (three Amphidamas, two Adrastus/Adrestus, two
  Hippothous, two Polydorus, two Podargus, two Thoas, two Noëmon, two
  Echepolus). They share one pronunciation row keyed to the spelling; the
  *entries* keep them apart.

## Data & regeneration

- The respellings live in **`index/pronunciations.tsv`** — one row per headword
  (`headword` ⇥ `say` ⇥ optional `variant`). It is meant to be scanned and
  corrected by hand; it is the single source of truth.
- Rows for names shared with the Odyssey are **inherited verbatim** from
  `..\odyssey\index\pronunciations.tsv` by `tools/seed_pronunciations.py`, which
  also reports which Iliad headwords still need a hand-written row. Re-running it
  never overwrites a row already present here.
- `tools/merge_index.py` reads the TSV and injects the `*Say:*` field into each
  entry when it builds `index/index.md`. Editing a pronunciation means editing
  one row and re-running the merge.
- Transparent English names (Troy, Crete, Sparta, Athens, Egypt, and the like)
  and the descriptive/collective headwords (Dawn, Sleep, Strife, the Muses)
  carry no row and get no `*Say:*` field.
