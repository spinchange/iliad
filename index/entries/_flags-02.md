# Slice 02 — citation flags, reviewed

`tools/merge_index.py` flags any `book.line` an entry cites that is not an
occurrence of that headword. The check is advisory by design: an entry may
legitimately cite a scene line where the figure is present but named by
patronymic, epithet, periphrasis, or across an enjambment. Every flag raised
against `entries-02.md` was checked against the text on 2026-07-27 and is listed
here with its justification, so a later reviewer need not re-derive them.

Four flags were **real errors and have been fixed**: Apollo cited 1.14 for the
ἑκηβόλος first-ref (that line is "holding in his hands, on a golden staff, the
wreaths"; the epithet falls on 1.15); Atreus cited 9.341 (the patronymic is at
9.340, "the sons of Atreus"); Argos cited 4.51 (the three cities are named at
4.52); Boeotians cited 15.329 (the ethnonym is at 15.330).

The twenty-four below are correct as written.

| Entry | Cited | Why it is not an occurrence |
|---|---|---|
| Apollo | 1.37 | epithet-register first-ref for ἀργυρότοξος; the line is Chryses' vocative "god of the silver bow," no name |
| Apollo | 1.147 | epithet-register first-ref for ἑκάεργος; "the worker-from-afar," substantive, no name |
| Apollo | 1.385 | epithet-register first-ref for ἕκατος; "the god-word of the far-striker," substantive, no name |
| Areithous | 7.142 | his death in Nestor's tale — the line names Lycurgus, the killer; Areithous is "him" |
| Ares | 5.831 | Athena's "that raving thing, that made evil, that turncoat" — the ἀλλοπρόσαλλος register ref, all epithet |
| Ares | 13.518 | the death of his son Ascalaphus, cited under Ares for the 15.110–118 consequence; the line names Ascalaphus |
| Argives | 9.22 | Agamemnon "orders me back to Argos in disgrace" — the host is "me" and "my people," place-name only |
| Artemis | 21.479 | Hera turning on her: "the honored wife of Zeus, in anger, reviled the shooter of arrows" — periphrasis both ways |
| Ascalaphus | 15.110 | opening of Hera's report of his death; he is "his son," named at 15.112 |
| Asclepius | 4.219 | Chiron's drugs "which Chiron once gave his father" — Asclepius is "his father" |
| Asius | 13.387 | his death-blow; the line names Idomeneus, the killer, and Asius is "him" |
| Asteropaeus | 21.179 | his death-blow; Achilles "took his life with the sword," no name |
| Astyanax | 6.402 | first half of the name-gloss couplet: "Hector called him Scamandrius, but the others / Astyanax" — the name lands on 6.403 |
| Athena | 2.157 | epithet-register first-ref for Ἀτρυτώνη; Hera's vocative "Unwearied one, child of aegis-bearing Zeus" |
| Athena | 4.128 | epithet-register first-ref for ἀγελείη; "Zeus's daughter, the driver of the spoil" |
| Athena | 5.747 | epithet-register first-ref for ὀβριμοπάτρη; "she of the mighty father," substantive |
| Athena | 8.373 | epithet-register ref for standalone γλαυκῶπις; Zeus's familiar "his dear grey-eyes" |
| Athena | 21.406 | the boundary-stone blow in the theomachy; the line names Ares, and Athena is "she" (named at 21.408) |
| Athenians | 15.332 | Aeneas kills Iasus, set a captain of the Athenians at 15.337; the line names the victims only |
| Atreus | 2.101 | first line of the sceptre's descent, which reaches Atreus at 2.105 |
| Automedon | 16.146 | the honor-formula "the man he honored most after Achilles breaker of men"; Automedon is named at 16.145 and is "the man" here |
| Briseis | 1.184 | epithet-register ref for καλλιπάρῃος; enjambed "fair-cheeked / Briseis," the name on 1.185 |
| Capaneus | 4.404 | opening of Sthenelus' retort quoted in the entry; the speaker is "the son of glorious Capaneus" at 4.403 |
| Cebriones | 16.737 | the stone-cast that kills him: "he struck Hector's charioteer —" with the name enjambed to 16.738 |
| Cebriones | 16.776 | "lay mighty in his mightiness, his horsemanship all forgotten" — the corpse is the subject, unnamed |
