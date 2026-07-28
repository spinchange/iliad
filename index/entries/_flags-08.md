# Slice 08 — citation flags, reviewed

`tools/merge_index.py` flags any `book.line` an entry cites that is not an
occurrence of that headword. The check is advisory by design: an entry may
legitimately cite a scene line where the figure is present but named by
patronymic, epithet, periphrasis, or across an enjambment. Every flag raised
against `entries-08.md` was checked against the text on 2026-07-27 and is listed
here with its justification, so a later reviewer need not re-derive them.

Three flags were **real errors and have been fixed**: Zeus cited 1.397 for the
Κρονίδης / Κρονίων first-ref (that line is "declare it proudly: that you alone
among the immortals"; the patronymic falls on 1.398); Trojans cited 22.408 (the
collective there is "the people", and the Trojans are named at 22.1); Stichius
and Simoeisios each had a flagged ref resolved by moving to the naming line.

The eighteen below are correct as written.

| Entry | Cited | Why it is not an occurrence |
|---|---|---|
| Simois | 20.53 | the river under the alternate printed spelling *Simoïs* — "now running by Simoïs over Callicolone"; the entry cites it to record the spelling variant |
| Simois | 21.307 | likewise *Simoïs* — Scamander's call to his "dear brother" against Achilles; same variant |
| Sleep | 14.259 | Night's rescue of Sleep from Zeus's fury — "had Night not saved me — Night, subduer of gods and men"; Sleep is the speaking "me" |
| Sun | 14.344 | the register ref for the god's other name in this translation: "Not even Helios could spy us through it" |
| Sun | 19.398 | the "Hyperion the shining sun" formula; the token is Hyperion, the referent the Sun |
| Telamon | 12.371 | the half-brother line — "and with him went Teucer, his brother by one father"; Telamon is "one father", unnamed |
| Theano | 6.299 | her patronymic and marriage in the line after the name: "Cisseus' daughter, wife of Antenor, breaker of horses" |
| Theano | 11.223 | the alternate spelling of her father — "Cisses raised him in his house"; Theano is named at 11.224 |
| Thebes | 4.370 | opening line of the Agamemnon shaming-speech cited as a range (4.370–400); Thebes is named inside it at 4.378 |
| Thetis | 1.538 | epithet-register support for ἀργυρόπεζα; the name and epithet fall on 1.537, the patronymic "daughter of the old man of the sea" on 1.538 |
| Thetis | 18.35 | "his lady mother heard him / where she sat in the depths of the sea beside her aged father" — periphrasis; she is named at 18.51 |
| Thetis | 24.126 | "And she, his lady mother, sat down close beside him" — same periphrasis, named at 24.120 |
| Zephyrus | 16.150 | the sire of Xanthus and Balius given as "the West Wind", not by name; cited to show the poem uses both |
| Zephyrus | 19.415 | "the very breath of the West Wind" in Xanthus's speech; same untransliterated form |
| Zeus | 1.498 | epithet-register first-ref for εὐρύοπα; "the wide-seeing son of Cronos", substantive |
| Zeus | 1.398, 1.528 | epithet-register refs for Κρονίδης / Κρονίων; "the son of Cronos, lord of the dark cloud" (1.398, the corrected first-ref) and "The son of Cronos spoke, and nodded with his dark brows" (1.528), both the patronymic standing for the name |
| Zeus | 1.544 | epithet-register first-ref for πατὴρ ἀνδρῶν τε θεῶν τε; "the father of men and gods answered her", substantive |
| Zeus | 1.580, 7.411, 8.250, 13.625 | epithet-register first-refs quoted from `CONVENTIONS.md`: "the Olympian, lord of lightning" (substantive); "Zeus the loud-thunderer, Hera's lord" and "Zeus of All Voices" (the flagged line carries the epithet, the name adjacent); "Zeus / of Guest-right" (enjambed from 13.624) |
| Zeus | 8.5, 15.56, 15.187, 16.431, 22.209, 24.103 | scene-opening lines cited as ranges or turning-points where Zeus is the speaker or subject unnamed: the Olympus ban ("Hear me, all you gods"), the plan-speech 15.56–77, the three-brothers lot (Poseidon speaking of "Zeus, and I, and Hades"), "the son of crooked-counseled Cronos saw them, and pitied", "the father stretched out his golden scales", "the father of men and gods began speaking" |
