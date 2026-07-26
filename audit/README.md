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
| 10 | 2026-07-26 (full, r1) | book-10-full-r1.md — 1 firm (fixed), 0 parked | 10.90 = 9.610 harmonized |
| 11 | 2026-07-26 (full, r1) | book-11-full-r1.md — 2 firm (fixed), 0 parked | 11.407 "argue" harmonized; 11.435-436 = 3.357-358 harmonized |
| 12 | 2026-07-26 (full, r1) | book-12-full-r1.md — 3 firm (fixed), 0 parked | 12.231-234 = 7.357-360; 12.194 = 8.277; 12.84 = 11.47 |
| 13 | 2026-07-26 (full, r1) | book-13-full-r1.md — 5 firm (fixed), 0 parked | five single-echo harmonizations (vs 8.43-44, 8.331-333, 12.368-369, 8.541, 8.380) |
| 14 | 2026-07-26 (full, r1) | book-14-full-r1.md — 3 firm (fixed), 0 parked | rally-formula split harmonized ×5 (12.75, 14.74, 14.370, 15.294, 18.297); 14.69 = 2.116; 14.148-149 = 5.860-861 |
| 15 | 2026-07-26 (full, r1) | book-15-full-r1.md — 1 firm (fixed), 0 parked | 15.368-369 = 8.346-347 harmonized (15.294 fixed in Book 14 tranche) |
| 16 | 2026-07-26 (full, r1) | book-16-full-r1.md — 6 firm (fixed), 1 parked | six single-echo harmonizations (16.59 = 9.648 etc.; γέρας θανόντων fixed at 23.9) |
| 17 | 2026-07-26 (full, r1) | book-17-full-r1.md — 6 firm (fixed), 2 parked | heart-soliloquy line is five-fold (17.97 fixed); 17.82, 147-148, 259, 315, 617 harmonized |
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
