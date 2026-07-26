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
| 1 | 2026-07-26 (full, r1) | book-01-full-r1.md — 0 firm, 1 parked | none required |
| 2 | 2026-07-26 (full, r1) | book-02-full-r1.md — 0 firm, 2 parked | none required |
| 3 | 2026-07-26 (full, r1) | book-03-full-r1.md — 0 firm, 0 parked | none required |
| 4 | 2026-07-26 (full, r1) | book-04-full-r1.md — 0 firm, 1 parked (fixed) | 4.48-49 = 24.69-70 harmonized |
| 5 | 2026-07-26 (full, r1) | book-05-full-r1.md — 0 firm, 0 parked | none required |
| 6 | 2026-07-26 (full, r1) | book-06-full-r1.md — 0 firm at review, 1 upgraded + fixed, 1 parked | μήστωρ φόβοιο harmonized (6.97/278, with 8.108, 23.16) |
| 7 | 2026-07-26 (full, r1) | book-07-full-r1.md — 1 firm (fixed), 1 parked | 7.117 ἀκόρητος inversion fixed |
| 8 | 2026-07-26 (full, r1) | book-08-full-r1.md — 2 firm (fixed), 1 parked | 8.105 = 5.221 harmonized; μήστωρ φόβοιο register fix |
| 9 | 2026-07-26 (full, r1) | book-09-full-r1.md — 0 firm, 0 parked | none required |
| 10 | — | — | — |
| 11 | — | — | — |
| 12 | — | — | — |
| 13 | — | — | — |
| 14 | — | — | — |
| 15 | — | — | — |
| 16 | — | — | — |
| 17 | — | — | — |
| 18 | — | — | — |
| 19 | — | — | — |
| 20 | — | — | — |
| 21 | — | — | — |
| 22 | 2026-07-26 (full, r1) | book-22-full-r1.md — 0 firm, 1 parked | none required |
| 23 | 2026-07-26 (full, r1) | book-23-full-r1.md — 0 firm, 1 parked | none required |
| 24 | 2026-07-26 (full, r1) | book-24-full-r1.md — 0 firm, 2 parked | none required |

No CRITICAL or MAJOR findings in any reviewed book; no r2 escalation
triggered. Fixes applied so far: 4.48-49 = 24.69-70 harmonized
(Book 4 tranche); 7.117 "glutted" → "never sated" (ἀκόρητος
inversion — the audit's first firm mistranslation); the μήστωρ
φόβοιο formula harmonized to the registered "machine(s) of rout" at
6.97, 6.278, 8.108, 23.16; and 8.105 harmonized to the 5.221
wording. Remaining scope: Books 9-21, to be reviewed in subsequent
sessions (fresh-context sessions are preferable for the r1 pass on
books translated long before, and mandatory for any r2).
