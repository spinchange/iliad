# Fidelity Review Rubric (Iliad)

Adapted from the Odyssey project's production rubric
(`..\odyssey\audit-production\rubric.md`), which was written for the same
translation contract this project uses.

## Scope

Evaluate semantic fidelity of the supplied Greek passage against its English
translation. Read in syntactic units spanning line boundaries. The
translation deliberately uses one English verse per Greek verse and a loose
five-to-six-beat line (all books, measured, hold a median-13-syllable,
92-95% 9-16-syllable distribution); do not flag defensible poetic recasting
merely because it is not literal.

The translator's notes explain choices but do not establish that those
choices are correct. Other English translations are not a gold standard —
the Greek is.

Explanatory notes are within audit scope when they assert the Greek's
meaning, the translation's logic, or factual context used to justify a
rendering — including apparatus claims (who athetized what, variant
readings). A materially false note may be reported even when the verse
itself is correct. Apparatus claims should be checked against
`apparatus/book_NN.txt`, remembering that file is itself OCR-derived and
rough.

## Finding categories

- `MISTRANSLATION`: source meaning materially changed or reversed.
- `OMISSION`: meaningful source content absent without nearby compensation.
- `ADDITION`: the English asserts material content unsupported by the Greek.
- `GRAMMAR`: agency, relationship, negation, tense, aspect, mood, or scope
  changed.
- `AMBIGUITY`: the English resolves a consequential Greek ambiguity too
  narrowly (and no note flags the choice).
- `LEXICAL`: significant denotation or connotation weakened or displaced.
- `FORMULA`: a registered or repeated formula materially mishandled in
  meaning or rhetorical function. (Mechanical fixed-rendering conformance
  is `tools/check_formulas.py`'s job and is outside the reviewer count.)
- `REGISTER`: consequential change in social, rhetorical, or character
  voice (e.g. softening an insult, formalizing camp speech).
- `LINEATION`: the 1:1 lineation causes a meaning or attachment distortion
  (wrong clause attachment across a line break).
- `NOTE`: a materially false or misleading claim in a footnote or
  commentary.

## Severity

- `CRITICAL`: reverses the action, agency, negation, or central proposition.
- `MAJOR`: loses or adds an important proposition, relationship, or poetic
  effect.
- `MODERATE`: meaningful local distortion that should probably be revised.
- `MINOR`: real but limited deviation; revision may still be required by an
  explicit register rule.

Report `confidence` from 0.00 to 1.00 — the probability the difference is a
*material fidelity problem*, not merely that the Greek and English differ in
construction. Firm findings need >= 0.75; park 0.50-0.74 concerns in a
secondary table; omit weaker possibilities. Do not report mere alternative
possibilities as errors.

## Decision rules

- **Generic plurals/quantifiers**: a Greek bare plural may be generic; an
  added "all/every/always" is a firm ADDITION only when the exhaustive
  reading is materially stronger than the likely Greek scope.
- **Particles**: untranslated δέ/ἄρα/τε are not findings; untranslated ἦ
  μήν, περ, γε *may* be when emphasis carries meaning.
- **Formulaic epithets**: the register's fixed renderings are given; do not
  re-litigate them per line. A FORMULA finding requires the *function* in
  context to be mishandled.
- **Athetized lines**: the project translates the printed text including
  atheteses; their presence is never a finding.
- **Duals**: loss of dual number is a GRAMMAR finding only where the
  two-ness is dramatically operative (e.g. embassy scenes).

## Output format

One report per reviewed span: a findings table
(`line | category | severity | confidence | Greek | English | note`),
a secondary (0.50-0.74) table, and a two-paragraph summary. File under
`audit/findings/book-NN-<span>-r<reviewer>.md`.
