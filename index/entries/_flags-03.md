# Slice 03 — citation flags, reviewed

`tools/merge_index.py` flags any `book.line` an entry cites that is not an
occurrence of that headword. The check is advisory by design: an entry may
legitimately cite a scene line where the figure is present but named by
patronymic, epithet, periphrasis, or across an enjambment. Every flag raised
against `entries-03.md` was checked against the text on 2026-07-27 and is listed
here with its justification, so a later reviewer need not re-derive them.

One register entry was found **wrong for this translation and dropped**:
`CONVENTIONS.md` files χρυσόθρονος "of the golden throne" at 1.611 under Dawn,
but 1.611 in the committed text reads "with Hera of the golden throne beside
him," and all four occurrences of the phrase (1.611, 8.442, 14.153, 15.5) belong
to Hera or to Zeus's own seat. The epithet was removed from the Dawn entry and the
divergence noted there; the 1.611 flag below records what remains.

The ten below are correct as written.

| Entry | Cited | Why it is not an occurrence |
|---|---|---|
| Coeranus | 17.610 | the death-blow's first line, "but struck the aide and charioteer of Meriones —" with the name enjambed to 17.611 |
| Dardanus | 20.302 | opening of Poseidon's rescue-and-dynasty speech quoted in the entry; the race of Dardanus is named at 20.303–304 |
| Dawn | 1.611 | cited only to record that the register's χρυσόθρονος first-ref lands on Hera here, not on Dawn — deliberate, and stated as such in the entry |
| Diomedes | 5.1 | first line of his aristeia, "Then it was that Pallas Athena gave Tydeus' son"; the name is enjambed to 5.2 |
| Diomedes | 11.377 | Paris' arrow through his foot; the line is the wound itself, and Diomedes is "him" (named 11.370, 11.384) |
| Dog | 22.26 | opening of the Dog-of-Orion simile quoted in the entry; the star is named at 22.29 |
| Dolon | 10.454 | the killing: "the man was reaching for his chin with his broad hand" — Dolon is "the man," named at 10.447 |
| Dolops | 15.540 | Menelaus' rescue-cast that kills him; the line names Menelaus, and Dolops is "his shoulder" at 15.541 |
| Echius | 16.415 | first line of the nine-name kill-list in which the Trojan Echius falls; his name lands on 16.416 |
| Ennomus | 2.860 | the Catalogue's death-notice, "he was broken under the hands of the swift-footed son of Aeacus"; Ennomus is "he," named at 2.858 |
| Ereuthalion | 7.153 | Nestor's account of the fight, "to fight him with its daring — and I was youngest-born of all"; Ereuthalion is "him" (named 7.150) |
