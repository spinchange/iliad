# Iliad Fidelity Audit

Scaled-down adaptation of the Odyssey project's production audit
(`..\odyssey\audit-production\`). Same rubric philosophy, lighter process:
this project runs single-reviewer rubric passes per book (or per span for
long books), with a second independent review reserved for books that turn
up CRITICAL/MAJOR findings.

## Process

1. Pick a span (a whole book, or ~300-line ranges for long books).
2. Review against `audit/rubric.md`, Greek (`books/`) beside English
   (`translation/`), aligned by line number.
3. File the report as `audit/findings/book-NN-<span>-r1.md`.
4. Fix accepted findings in the translation; note register changes in
   `translation/CONVENTIONS.md`; commit fixes with the report.
5. Escalate to a second independent reviewer (separate session, no sight of
   the first report) only when r1 finds CRITICAL or MAJOR issues.

Mechanical formula conformance is not audited by humans — run
`python tools/check_formulas.py` instead.

## Status

| Book | Reviewed | Findings filed | Fixes applied |
|---|---|---|---|
| 1 | — | — | — |
| 2 | — | — | — |
| 3 | — | — | — |
| 4 | — | — | — |
