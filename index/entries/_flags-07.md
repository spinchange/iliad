# Slice 07 — citation flags, reviewed

`tools/merge_index.py` flags any `book.line` an entry cites that is not an
occurrence of that headword. The check is advisory by design: an entry may
legitimately cite a scene line where the figure is present but named by
patronymic, epithet, periphrasis, or across an enjambment. Every flag raised
against `entries-07.md` was checked against the text on 2026-07-27 and is listed
here with its justification, so a later reviewer need not re-derive them.

Three drafted citations were **corrected before submission** and no longer flag:
Pergamos cited 6.512 (the name is enjambed onto 6.513, "of Pergamos, blazing in
his armor"); Periphas cited 17.323 (the herald's name lands on 17.324); Sarpedon
cited 16.463 for the horse Pedasus, which the line does not support — 16.463 is
Patroclus killing Thrasymelus, and Sarpedon's errant cast hits Pedasus at 16.466.

The seven below are correct as written (`merge_index.py` groups them into six
flag lines, since the two Sarpedon refs are reported together).

| Entry | Cited | Why it is not an occurrence |
|---|---|---|
| Polydamas | 14.450 | his killing of Prothoenor; the line names Prothoenor and Areïlycus, and Polydamas is "Panthous's son" — he is named at 14.449 |
| Poseidon | 7.455 | epithet-register first-ref for εὐρυσθενής; Zeus's "Shame, wide-ruling earth-shaker" — all epithet, no name |
| Poseidon | 9.183 | epithet-register first-ref for γαιήοχος; the envoys pray to "the holder and shaker of the earth," substantive |
| Poseidon | 21.435 | opening of his challenge to Apollo in the theomachy: "And the lord earth-shaker addressed Apollo" — epithet only |
| Promachus | 14.476 | the death-blow; the line names Acamas the killer and "his brother," with Promachus enjambed to 14.477 |
| Sarpedon | 12.394 | his killing of Alcmaon; the line names Alcmaon and Thestor, and Sarpedon is the unnamed subject carried over from 12.392–393 |
| Sarpedon | 16.480 | the spear-cast that kills him: "But Patroclus in his turn / rose with the bronze" — Sarpedon is the unnamed target, named at 16.477 |

## Addendum (2026-07-27): Scamander refs after the registry token split

`Xanthus` was originally folded into the **Scamander** headword, which conflated
four referents and made its hit-count and ref-list wrong. The token now sits with
the horse (see `tools/build_registry.py`), so the river's own occurrences under
the *Xanthus* spelling no longer resolve against its occurrence set and are
flagged. All are correct as cited:

| Entry | Cited | Why it is not an occurrence |
|---|---|---|
| Scamander | 21.2 | "eddying Xanthus, whom immortal Zeus begot" — the river under its divine name |
| Scamander | 21.15 | "the sounding stream of Xanthus" — same river, same spelling |
| Scamander | 2.877, 6.172, 12.313 | cited in the entry's NB precisely to warn that these are the **Lycian** Xanthus, not this river |
