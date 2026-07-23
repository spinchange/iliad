# Morphological Analysis — Homer's Iliad (Perseus/AGDT Treebank)

This directory contains word-by-word morphological and syntactic analysis for (nearly) every line of the Iliad, extracted from the **Ancient Greek Dependency Treebank (AGDT)**, a project of the Perseus Digital Library / Perseus Digital Library at Tufts, with annotation work by Giuseppe G. A. Celano, Gregory R. Crane, and student annotators at Perseus-affiliated institutions.

- Source: [`gregorycrane/gAGDT`](https://github.com/gregorycrane/gAGDT), file `data/xml/tlg0012.tlg001.perseus-grc1.tb.xml`
- This is the same base edition (`Perseus:text:1999.01.0133`, the Monro-Allen text) as `iliad_greek_full.txt` and `books/` in the parent directory, so line numbers line up directly.
- Coverage: all 24 books, ~112,600 tagged word tokens, matching or very nearly matching the expected line count per book (e.g. Book 1: 611/611 lines, Book 24: 804/804 lines — a handful of other books are short by single-digit lines where a sentence's citation span wasn't cleanly parsed out of the source XML).

## Format

Files `book_01.txt`–`book_24.txt` each look like:

```
Line 1:
    μῆνιν (μῆνις) [noun fem acc sg] {OBJ}
    ἄειδε (ἀείδω) [verb pres imperv act 2 sg] {PRED_CO}
    θεὰ (θεά) [noun fem voc sg] {ExD}
    Πηληϊάδεω (Πηλείδης) [noun masc gen sg] {ATR}
    Ἀχιλῆος (Ἀχιλλεύς) [noun masc gen sg] {ATR}
```

Each word line is: **inflected form** `(lemma / dictionary form)` `[morphology]` `{syntactic relation to the rest of the sentence}`.

Punctuation tokens are omitted from these files (they clutter word-by-word reading and carry no lexical content); the underlying treebank does tag them if ever needed.

## Morphology tags

The treebank encodes each word with a 9-character positional code (`postag`); this project decodes it into readable English abbreviations. For **nouns/adjectives/pronouns/etc.**, you'll see `gender case number [degree]`; for **verbs**, `tense mood voice [person] [number]`.

| Category | Values used here |
|---|---|
| Part of speech | noun, verb, adj, adv, article, particle, conj (conjunction), prep (preposition), pron (pronoun), numeral, interj (interjection) |
| Person | 1, 2, 3 |
| Number | sg (singular), pl (plural), dual |
| Tense | pres, impf (imperfect), perf (perfect), plup (pluperfect), futperf (future perfect), fut (future), aor (aorist) |
| Mood | ind (indicative), subj (subjunctive), opt (optative), inf (infinitive), imperv (imperative), part (participle) |
| Voice | act (active), pass (passive), mid (middle), mp (middle-passive, ambiguous form) |
| Gender | masc, fem, neut |
| Case | nom, gen, dat, acc, voc, loc (locative, rare) |
| Degree | comp (comparative), superl (superlative) — only shown when applicable |

**Note on Homeric forms**: Homeric Greek predates the later Attic standard and has some forms grammarians classify ambiguously (e.g. many middle/passive forms are simply tagged `mp` because the form itself doesn't distinguish voice outside certain tenses) — this is a real feature of the dialect, not an extraction error.

## Syntactic relation tags

The `{...}` tag is the word's **dependency relation** to its syntactic head (per Perseus's Ancient Greek Dependency Treebank annotation guidelines). Common ones you'll encounter:

| Tag | Meaning |
|---|---|
| `PRED` | main predicate of the clause |
| `PRED_CO` | coordinated predicate (joined to another predicate) |
| `SBJ` | subject |
| `OBJ` | direct object |
| `OBJ_CO` | coordinated object |
| `ATR` | attributive modifier (adjective/genitive modifying a noun, etc.) |
| `ATR_CO` | coordinated attributive modifier |
| `ADV` | adverbial modifier |
| `ADV_CO` | coordinated adverbial modifier |
| `AuxV` | auxiliary verb |
| `AuxP` | preposition governing a following noun phrase |
| `AuxX` | punctuation mark (comma, etc.) treated as a syntactic node |
| `AuxK` | sentence-final punctuation |
| `AuxY` | particle with a discourse/connective function (e.g. δέ, γάρ) not otherwise categorized |
| `AuxZ` | emphasizing particle/word |
| `AuxC` | subordinating conjunction |
| `ExD` | "extra dependency" — vocatives, parenthetical elements, and other words not cleanly integrated into the main clause structure |
| `COORD` | coordinating conjunction itself (καί, δέ used to link clauses) |
| `CORR` | correlative (e.g. one half of a μέν...δέ pairing) |
| `PNOM` | predicate nominative (complement of a copula) |
| `ATV` | "attribute verbal" — a secondary predicate (e.g. a participle agreeing with the object) |
| `OCOMP` | object complement |
| `XSEG` | segment of a word split across an annotation boundary (rare) |
| `UNDEFINED` | annotator left the relation unspecified |

A `_CO` suffix marks a coordinated element (joined to a sibling by `COORD`); an `_AP` suffix marks apposition to another element with that base relation (so `ATR_AP` is an appositive functioning attributively, etc.) — these suffixes combine with any of the base tags above rather than being separate categories.

This is not an exhaustive list of every tag in the AGDT guidelines — if you see a tag not listed here, the full annotation guidelines are at [github.com/PerseusDL/treebank_data](https://github.com/PerseusDL/treebank_data) (AGDT2 guidelines document) if you need the complete reference.

## Known limitations

- This is a **student/crowd-annotated treebank**, not a single scholar's definitive parse — the AGDT was built by multiple annotators over time (see the header of the source XML for named contributors) under a shared guideline document, so occasional inconsistencies in judgment calls (e.g. borderline ATR vs. ADV decisions) are possible, same as with any large syntactic annotation project.
- A small number of lines per book (roughly 5-15%, varying by book) are not independently represented as their own `Line N:` entry — most likely because their citation was merged into a multi-line sentence span (`cite="...1.101-1.103"` style) and grouped under a single line number rather than split out. If a specific line you need isn't listed, check the line immediately before it; the missing line's words are often folded in there.
- Word order within each `Line N:` block follows the order words appear in the source treebank's sentence structure (which is often, but not strictly always, the same as reading order in the Greek line, since treebank sentences can span multiple Iliad lines and get grouped by their first-line citation).
- This treebank reflects the **same Monro-Allen edition** as the rest of this project, so any line an editor rejected or altered (see `../disputed_lines.md` and `../apparatus/`) is parsed as printed in that edition, not as a variant reading.
