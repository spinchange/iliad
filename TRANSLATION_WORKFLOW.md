# Translation Workflow: Text, Footnotes, and Commentary (v2)

This document specifies *how* to run a translation-plus-annotation pass on a
book of the Iliad in this project, so the output is consistent across books
and across sessions. Read it alongside the relevant `HANDOFF_bookNN.md` where
one exists (source-material orientation for that book) and
`translation/CONVENTIONS.md` (the binding formula register and policy file —
its Principles section is part of this workflow).

v2 (2026-07-22) incorporates the production practices of the sibling Odyssey
project (`..\odyssey`): numbered lines, a FORMULAS-style register with
first-use references, echo notes, verification tooling, git, and a fidelity
audit. v1 was written before any book had been translated; this version
supersedes it.

## Two passes, not one

Translate first. Annotate second. Do not interleave them in a single pass.

**Why**: translating and judging "is this footnote-worthy" are different
cognitive tasks. Doing both at once produces either a choppy, second-guessed
translation or thin annotation. Splitting avoids both.

**Pass 0 — Preflight.**
1. Read `translation/CONVENTIONS.md` in full; the register is binding.
2. Run `python tools/scan.py books/book_NN.txt` — expect ~95% of lines to
   scan. A rate far below that means the Greek source is damaged; stop and
   investigate before translating.
3. Read the book's apparatus (`apparatus/book_NN.txt`) and the relevant rows
   of `disputed_lines.md` before translating, so known cruxes are met with
   open eyes rather than discovered in Pass 2.

**Pass 1 — Translation.** Work through `books/book_NN.txt` and produce a
clean English translation, one English line per Greek line, aiming at a
loose five-to-six-beat line. Use `morphology/book_NN.txt` to resolve
grammatical ambiguity. Do not stop to write commentary — drop a lightweight
`{{NOTE: reason}}` placeholder where something clearly needs a note. Keep
the draft (with line numbers) in the session scratchpad; it is the alignment
record for Pass 2.

**Pass 2 — Annotation.** Re-read the completed translation against the
Greek, the apparatus, and `disputed_lines.md`. Convert placeholders into
numbered footnotes; add others found on this dedicated re-read; write the
translator's commentary. Update `translation/CONVENTIONS.md` (with first-use
references) for every newly fixed formula, refrain, or policy.

**Pass 3 — Verify and commit.**
1. Run `python tools/check_formulas.py NN` — must pass clean. If a
   violation reflects a *better* convention than the register (it happens),
   fix the register and the checker, not the translation, and say so in the
   commit message.
2. Confirm the line count matches the Greek (the numbering script or a
   quick count).
3. Commit the book, the register update, and any tooling changes together;
   the commit message names the book and any convention changes.

## What triggers a footnote

Not every line needs one. A footnote is warranted when at least one applies:

1. **Known textual disputes.** The line is flagged in `disputed_lines.md`
   or has a notable apparatus entry (athetesis, substantive variant,
   omission) that could plausibly affect translation. State the dispute,
   cite the source, and say what choice was made and why.
2. **Translator's judgment calls.** Genuinely competing renderings —
   ambiguous syntax, a word with no clean English equivalent, a deliberate
   departure from the usual rendering. State the alternatives and the
   choice.
3. **Realia and cultural context.** A reference a modern reader likely
   won't catch — ritual, epithet's mythological weight, geography, social
   custom. Genuinely explanatory, not textual-critical.
4. **Formulaic/repeated language.** Note a formula the first time it
   appears anywhere in the whole translation, explain the rendering
   convention, log it in the register, and then go silent on recurrences.
5. **Meaningful reuse (echo notes).** A formula, line, or scene whose
   *recurrence or placement* carries the point: a line reused in a changed
   context, a payoff of something planted books earlier, an arc landing
   (e.g. Diomedes' silence at 4.401 answered at 9.32). Adopted from the
   Odyssey project's practice, where such notes are the annotation's best
   feature. Use sparingly: the echo must do real work in the scene, not
   merely exist.

If none apply, don't force a note. Err toward restraint on categories 2, 3,
and 5; categories 1 and 4 are objectively bounded.

## Output format

Each translated book is a single file, `translation/book_NN.txt`:

```
BOOK 1

[One-sentence epigraph naming the book's action.]

TRANSLATOR'S COMMENTARY

[A few paragraphs. See below.]

------------------------------------------------------------

   1  Sing, goddess, the wrath[1] of Peleus' son Achilles,
   2  ruinous wrath, that laid griefs beyond counting on the Achaeans
   ...

------------------------------------------------------------

Notes

[1] (1.1) "wrath" (μῆνιν) — ...
```

- **Every translation line carries its Greek line number** (right-aligned,
  width 4, two spaces, text). The 1:1 lineation makes the number both a
  citation and an alignment record; the audit and the formula checker
  depend on it.
- Note markers are bracketed integers `[1]`, `[2]`… restarting at 1 per
  book; each note opens with its `(book.line)` reference so it can be found
  from either direction.
- Blank lines may separate verse paragraphs; they carry no numbers.
- The translation line stays otherwise free of clutter — no inline
  citations, no parenthetical Greek. All of that lives in the notes.
- Notes are concise — a sentence or two of context, a sentence on the
  choice. Topics needing paragraphs belong in the commentary.

## Translator's commentary

A short prose section (roughly 200-500 words; more only if the book
warrants it) at the top of the book's file, in the translator's own voice:
book-wide interpretive stances, register/tone aims, how live decisions from
the handoff or apparatus were resolved, and any arcs worth flagging forward.

## Cross-book consistency

`translation/CONVENTIONS.md` is the register: principles, fixed renderings
with first-use references, speech-introduction and vocative formulas,
whole-line refrains, and policy sections (ritual language, combat
conventions, names). Its rules:

- The committed text is the source of truth; grep the books when in doubt.
- Update the register in the same session as the book that changes it.
- Add a `tools/check_formulas.py` entry for any frequently recurring
  formula you fix.
- Verbatim Greek repetition = verbatim English repetition, always.

## Verification and audit

- `tools/scan.py` — hexameter verifier for the Greek source (ported from
  the Odyssey project). Baseline ~95%; a drop signals corrupt source, not
  Homer.
- `tools/check_formulas.py` — mechanical formula-conformance check;
  run per book in Pass 3 and over all books occasionally.
- `audit/` — the fidelity audit (rubric adapted from the Odyssey
  project's). After every few books, run a rubric-based review pass over a
  sample or a whole book; findings are filed in `audit/findings/`. The
  rubric, not other translations, is the standard.

## Summary checklist for a session translating book NN

1. Read `HANDOFF_bookNN.md` (if it exists), `translation/CONVENTIONS.md`,
   `apparatus/book_NN.txt`, and the book's rows in `disputed_lines.md`.
2. Pass 0: `python tools/scan.py books/book_NN.txt` — source sanity.
3. Pass 1: translate the whole book, 1:1 lines, `{{NOTE}}` placeholders,
   numbered draft in the scratchpad.
4. Pass 2: notes (categories 1-5), commentary, epigraph; update the
   register with first-use refs.
5. Pass 3: `python tools/check_formulas.py NN`; verify line count; commit.
