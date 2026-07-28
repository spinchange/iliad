# Slice 01 — citation flags, reviewed

`tools/merge_index.py` flags any `book.line` an entry cites that is not an
occurrence of that headword. The check is advisory by design: an entry may
legitimately cite a scene line where the figure is present but named by
patronymic, epithet, or context. Every flag raised against `entries-01.md` was
checked against the text on 2026-07-27 and is listed here with its justification,
so a later reviewer need not re-derive them.

Two flags were **real errors and have been fixed**: Acamas cited 11.59 (that line
names Agenor; Acamas is at 11.60), and Achaeans cited 7.96 (that line has
"Achaea," not "Achaeans").

The nine below are correct as written.

| Entry | Cited | Why it is not an occurrence |
|---|---|---|
| Adamas | 13.567 | his death-blow; the line names Meriones, the killer |
| Aeneas | 20.302 | Poseidon's prophecy; Aeneas is "this man" in the line |
| Aesepus | 6.20 | start of the twins' death-scene; names Euryalus and his first two victims |
| Agamemnon | 1.7 | "Atreus' son, lord of men" — patronymic + epithet, no name |
| Agamemnon | 2.101 | first line of the sceptre's descent, which ends in his hand at 2.107 |
| Agamemnon | 19.86 | opening of his Blindness plea; he speaks, so is not named |
| Agenor | 11.407, 17.97, 22.122, 22.385 | the four other bearers of the "why does my own heart argue" formula, cited to place his 21.562 in the set |
| Agenor | 21.562 | his own line of that formula; he speaks, so is not named |
| Alcathous | 13.427 | "the dear son of Zeus-nurtured Aesyetes" — patronymic; he is named at 13.428 |
| Alpheius | 5.541 | the twins of his line whom Aeneas kills; genealogy runs 5.541–560 |
| Andromache | 22.437 | "the wife of Hector had not yet heard" — periphrasis, no name |
| Aphrodite | 24.29 | the judgment of Paris; she is "the one who fed his grievous lust" |
