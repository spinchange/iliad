# Slice 04 — citation flags, reviewed

`tools/merge_index.py` flags any `book.line` an entry cites that is not an
occurrence of that headword. The check is advisory by design: an entry may
legitimately cite a scene line where the figure is present but named by
patronymic, epithet, periphrasis, or across an enjambment — and a cited
scene-range (`14.489–500`) is checked on its opening line, which is often the
line before the name lands. Every flag raised against `entries-04.md` was
checked against the text on 2026-07-27 and is listed here with its
justification, so a later reviewer need not re-derive them.

Two flags were **real errors and have been fixed**: Hector was credited with
killing Protesilaus and cited 2.701, but the poem says only "a Dardanian man had
killed him" and never names the killer — the claim was struck and the *Kills:*
field rebuilt from named victims (Amphimachus 13.185, Schedius 17.306, Asaeus and
Autonous 11.301); and Ida cited 15.152 for the arrival on the mountain, where the
mountain is named at 15.151 (15.152 is Gargaron, correctly cited under that
headword).

The thirty below, spread across twenty entries, are correct as written.

| Entry | Cited | Why it is not an occurrence |
|---|---|---|
| Eumelus | 2.715 | the epithet quoted for his mother Alcestis, "brilliant among women, loveliest of the daughters of Pelias"; the names are on 2.714 |
| Eumelus | 2.761 | opening of the Muse-question on the best horses, answered with his mares at 2.763–764 |
| Euphorbus | 16.806 | opening of the wounding of Patroclus: "from behind, at close range, a Dardanian / struck him" — the name is enjambed to 16.808 |
| Euphorbus | 17.45 | opening of his death-blow: "And second, with the bronze, / rose Atreus' son Menelaus"; Euphorbus is named at 17.47 |
| Euryalus | 23.679 | his father Mecisteus' Theban games for fallen Oedipus, quoted in the *Kin* field; Euryalus is named at 23.677 and is "him" here |
| Eurypylus | 11.578 | the spear-cast that kills Apisaon, cited as his kill; the line names the victim, and Eurypylus is the subject from 11.575 |
| Eurypylus | 15.390 | opening of the Patroclus-in-the-hut continuity scene; Eurypylus is named at 15.392 |
| Eurystheus | 8.362 | opening of Athena's complaint, "all the times I saved his son"; Eurystheus is named at 8.363 |
| Eurystheus | 15.639 | Copreus, "who used to carry the messages / of king Eurystheus"; the name lands on 15.640 |
| Eëtion | 6.414 | Andromache's "My father — brilliant Achilles killed him"; Eëtion is "my father," named at 6.416 |
| Hades | 5.190 | epithet-register ref for Ἀϊδωνεύς; the alias "Aïdoneus," no "Hades" in the line |
| Hades | 15.187 | opening of Poseidon's division-of-lots speech, "Three brothers are we, whom Rhea bore to Cronos"; Hades named at 15.188 |
| Hades | 20.61 | his terror in the theomachy, rendered with the alias: "the lord of those below, Aïdoneus" |
| Hector | 22.326 | his death-blow; the line names Achilles, and Hector is the implied target ("as he charged") |
| Hecuba | 6.251 | epithet-register first-ref for ἠπιόδωρος; "his gentle-giving mother," no name |
| Hecuba | 22.79 | opening of her plea from the wall: "And his mother in her turn wailed" — periphrasis throughout the speech |
| Helen | 3.175 | the daughter she left at Sparta, inside her own speech; the speaker is "Helen" at 3.171 |
| Hephaestus | 1.572 | the *Kin* ref for his mother: "bringing comfort to his dear mother, white-armed Hera"; Hephaestus is named at 1.571 |
| Hephaestus | 1.607 | epithet-register first-ref for ἀμφιγυήεις and περικλυτός; "the famed crook-footed god," with the name enjambed to 1.608 |
| Hephaestus | 18.382 | the *Kin* ref for Charis his wife; the line names her, and he is "her" husband in the scene |
| Hephaestus | 18.478 | opening of the shield-making, "And he made first of all a shield"; the maker is unnamed pronoun through the ecphrasis |
| Hera | 4.51 | opening of her three-cities speech; she is named in the speech-introduction at 4.50 |
| Hermes | 20.34 | epithet-register ref for the "courier" rendering of διάκτορος; the name is enjambed to 20.35 |
| Hippolochus | 6.207 | his charge to Glaucus, quoted in the entry; he is "Hippolochus" at 6.206 and the subject here |
| Hippothous | 17.293 | his death-blow: "the son of Telamon, springing at him through the crowd" — the line names the killer, Hippothous is "him" |
| Idaeus | 7.384 | epithet-register ref for ἠπύτα κῆρυξ; "the far-calling herald," substantive, no name |
| Idomeneus | 13.451 | the *Kin* ref for his father: "and Minos got a son, blameless Deucalion"; Idomeneus is Deucalion's son, named at 13.452 |
| Ilus | 20.231 | opening of the Trojan genealogy, "and from Tros in turn three blameless sons were born"; Ilus is named at 20.232 |
| Iphiclus | 2.703 | opening of the Phylacean succession passage; Iphiclus is named at 2.705 as Podarces' father |
| Iphidamas | 11.238 | his death-blow; the line names Agamemnon, and Iphidamas is "his grip" / "his neck" |
