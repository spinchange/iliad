# Phase 3 writer brief — how to write an index entry

You have been given a worklist (`_worklist-NN.md`) with a fixed, ordered set of
headwords. Write **exactly one entry for each, in the order given**, and write
nothing else. Output goes to `index/entries/entries-NN.md`, entries separated by
a line containing only `---`.

The merge step aligns your entries to your worklist **positionally**. An extra
entry, a missing one, or a reordering silently shifts every later entry onto the
wrong headword. Count before you submit.

## Sources — and their authority

| File | What it settles |
|---|---|
| `index/canon.md` | categories, alias resolution, genealogy, homonyms. **Binding.** |
| `translation/CONVENTIONS.md` | name spellings and the fixed English of every epithet. **Binding.** |
| your `_worklist-NN.md` | the headwords, their real citations, hit counts |
| `translation/book_NN.txt` | the poem itself — read the cited lines |

Never resolve an alias or assign parentage by memory or by general knowledge of
Greek myth. If canon.md does not settle it, say the text does not settle it.

## The shape

```
**Headword** (Ἑλληνικά) · CATEGORY
One to three sentences: who or what this is, the family or place it belongs to,
and why it matters — its decisive action or role. Present tense for narrative.
*Epithets:* "the fixed English" (Greek, first ref); …
*Also called:* aliases and patronymics, each pointing to its own entry.
*Kin:* parentage and key relations.
*Killed by:* / *Kills:* for the battle dead.
**Refs:** 5.38, 5.42 … Books 5, 13.
*See also:* related entries.
```

Omit any *(italic)* field that does not apply. Do **not** write a `*Say:*` field —
pronunciations are injected at merge time from `index/pronunciations.tsv`.

## Rules

1. **Length scales with importance.** ~40–90 words for a major figure; ~15–30 for
   a walk-on; one sentence for a man named once and killed in the same line. This
   is a finding aid, not a set of essays.
2. **Voice matches the footnote apparatus** in `translation/` — scholarly, plain,
   unfussy. No breathless summary, no "tragically," no editorializing.
3. **Epithets are quoted from CONVENTIONS.md, never invented or paraphrased.**
   Give the English exactly as fixed there, with the Greek and a first reference.
   If the register has no fixed epithet for this name, omit the field.
4. **Citations are real.** Use only refs from your worklist. Curate to ≤ ~8 key
   refs for a major name (first appearance, pivotal scenes) and add "…and
   throughout" plus book coverage; give the full short list for a minor one. The
   merge step checks every `book.line` you write against the occurrence set and
   flags anything else.
5. **Homonyms stay apart.** If your note says another figure shares the name, say
   so in the entry and point to the other. Never silently merge them.
6. **Patronymics point to the son.** An entry for a father whose token is mostly
   patronymic (Atreus, Peleus, Tydeus, Menoetius, Aeacus, Neleus, Peteos …) should
   say so plainly: who he is, and that in the poem the name is usually a way of
   naming his son.
7. **Greek in parentheses** after the headword, polytonic, nominative.

## Worked examples

**Simoeisios** (Σιμοείσιος) · MORTAL
A young Trojan killed by Telamonian Ajax in the first general engagement, born by
the banks of the Simois and named for the river. The poem gives him a genealogy
and a simile — he falls like a felled black poplar — and never mentions him again;
he is the first of the Iliad's many fully-realized one-scene dead.
*Kin:* son of Anthemion.
*Killed by:* Ajax (4.473–489).
**Refs:** 4.474, 4.477, 4.488.
*See also:* Ajax, Simois.

---

**Atreus** (Ἀτρεύς) · MORTAL
Father of Agamemnon and Menelaus and, before them, holder of the sceptre whose
descent from Hephaestus the poem traces at 2.101–108. He is dead before the
action begins: in nearly all of its 181 occurrences the name is a patronymic, and
"Atreus' son" in the singular means Agamemnon unless the scene is Menelaus's — see
`canon.md` for the rule.
*Kin:* son of Pelops; brother of Thyestes; father of Agamemnon and Menelaus.
**Refs:** 1.7, 2.105, 2.106, 9.341, 11.131 …and throughout. Books 1–11, 13–14,
16–17, 19, 22–24.
*See also:* Agamemnon, Menelaus, Thyestes, Pelops.
