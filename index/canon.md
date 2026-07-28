# Name index — Phase 2 canonicalization

This is the editorial spine of the index. Phase 1 (`tools/build_index.py`) found
*every capitalized token* and where it occurs, mechanically and without judgment.
This document supplies the judgment: it decides which tokens are real names, what
each name's canonical headword is, which other names and epithets resolve to it,
and how the families connect. Phase 3 (the entry-writers) consume this file plus
`occurrences.json`; they resolve aliases and assign genealogy **from here**, never
by independent guesswork, so that parallel writers can't contradict one another.

Two upstream files are authoritative and must not be contradicted:

- **`translation/CONVENTIONS.md`** — the binding register of fixed epithets and
  named-entity spellings, built book by book across the whole translation. Every
  headword spelling and every quoted epithet in the index comes from there.
- **`index/occurrences.json`** — every citation. Refs are real or they are wrong.

Coverage note: this seed fixes the schema, the category buckets, and — fully —
every *ambiguous or aliased* name, which in the Iliad is the hard and load-bearing
part. The unambiguous long tail (the several hundred one-line battle casualties)
is mechanical and is extended into `registry.md` before Phase 3 fans out.

---

## What makes the Iliad harder than the Odyssey

The companion Odyssey index (`..\odyssey\index\canon.md`) is the model for this
one, and the schema below is deliberately the same. Four things differ, and they
drive most of the editorial work here:

1. **Patronymics are the default mode of naming.** The Odyssey names people; the
   Iliad names them by their fathers, constantly and in the middle of combat —
   "Tydeus' son," "Peleus' son," "Atreus' son," "Telamonian Ajax." *Atreus* (181
   hits), *Peleus* (146), *Tydeus* (109), *Menoetius* (38) and *Aeacus* (25) rank
   among the most frequent tokens in the poem, and in the overwhelming majority
   of those hits the *father is not the referent*. The alias table below is
   therefore not a convenience — without it the index is wrong.
2. **The cast is enormous and mostly disposable.** Several hundred men are named
   once, to be killed in the same line or the next. They still get entries; they
   get short ones.
3. **Names collide.** The poem has two Adrastus/Adrestus, three Amphidamas, two
   Hippothous, two Polydorus, two Thoas, two Echepolus, two Noëmon, two Podargus,
   and a Lycaon who is both Pandarus's father and Priam's son. The homonym table
   below is the register; entry-writers must never silently merge them.
4. **One figure, two names, both used.** Paris/Alexandros, Ilion/Troy,
   Phoebus/Apollo, Cypris/Aphrodite, Enyalius/Ares, Scamander/Xanthus. The
   translation deliberately keeps both surface forms (see the Paris/Alexandros
   policy in `CONVENTIONS.md`), so both are headwords and each points at the other.

---

## Category buckets

Every headword is tagged with exactly one:

- **MORTAL** — human beings (Achilles, Priam, the named dead, heralds, captives).
- **GOD** — Olympians, and lesser divine/supernatural beings (river-gods, nymphs,
  the winds when personified, personified Strife, Panic, Terror, Dawn, Sleep,
  Death, Fate, Rumor, Blindness/Atē, the Prayers).
- **PEOPLE** — collective ethnonyms (Achaeans, Trojans, Myrmidons, Lycians).
- **PLACE** — lands, cities, islands, rivers, mountains, the underworld. Rivers
  that act as characters (Scamander/Xanthus, Spercheius) are PLACE, with the
  divine role noted in the entry and a `See also` to the GOD sense where the poem
  distinguishes them.
- **OTHER** — named animals (Xanthus and Balius, Achilles' horses; Aethe;
  Podargus), named objects, and constellations.

---

## Entry schema (the style contract for Phase 3)

Each entry is written to this shape. Fields in *(parentheses)* are omitted when
they don't apply.

> **Headword** (Greek Ἑλληνικά) · CATEGORY — *Say:* pro-NUN-see-AY-shun
> One to three sentences: who or what this is, the family or place it belongs to,
> and why it matters to the poem — its decisive action or role. Present tense for
> events in the narrative.
> *(Epithets:* the fixed English renderings, quoted verbatim from
> `translation/CONVENTIONS.md`, each with its Greek.*)*
> *(Also called:* aliases, patronymics, and cult titles used in the text, each
> cross-linked to its own entry.*)*
> *(Kin:* parentage and key relations, drawn from the genealogy section below or
> stated in the text.*)*
> *(Killed by / Kills:* for the battle dead — the poem's own bookkeeping, which is
> most of what a reader wants from a minor Iliad name.*)*
> **Refs:** curated key citations `book.line` — first appearance and pivotal
> scenes — then book coverage. Not an exhaustive dump.
> *(See also:* related entries.*)*

The *Say:* field is not authored per-entry: it is injected at merge time from
`index/pronunciations.tsv` (house style in `index/pron-key.md`), so writers leave
the headword line plain and pronunciations stay centralized and reviewable.

Rules for writers:

1. **Voice matches the footnote apparatus** — scholarly, plain, unfussy; the same
   register as the `[N]` notes in `translation/`. No breathless summary.
2. **Spellings are the translation's** — as fixed in the "Named-entity spellings"
   section of `CONVENTIONS.md` (Achilles not Akhilleus; Ilion and Troy both;
   Adrastus for the Sicyon king, Adrestus for the Trojan; diaereses kept in
   Eëtion, Oïleus, Leïtus).
3. **Epithets are quoted, not invented** — take the English from `CONVENTIONS.md`.
   If a name has no fixed epithet there, omit the field.
4. **Aliases resolve per the tables below** — never invent a cross-reference. A
   patronymic that is genuinely ambiguous is flagged as ambiguous, with the rule
   for deciding it, not guessed.
5. **Genealogy comes from the text or this file** — do not import parentage from
   later mythographers (Apollodorus, etc.) without marking it "(later tradition)".
6. **Citations come from `occurrences.json`** — real `book.line` refs only. Curate
   to ≤ ~8 key refs for a major name and add "…and throughout"; give the full
   short list for a minor one.
7. **Length scales with importance** — ~40–90 words for a major figure, ~15–30 for
   a walk-on. A man killed in one line gets one sentence. The index is a finding
   aid, not a set of essays.

---

## Alias-resolution table (the load-bearing part)

Maps every surface form **as it appears in this translation** to its canonical
headword. A reader who meets the phrase in the left column and is lost looks it
up here. English renderings are those fixed in `CONVENTIONS.md`.

### Patronymics — one-to-one (the father is not the referent)

| As it appears in the text | Canonical headword | Note |
|---|---|---|
| Peleus' son; son of Peleus; Pelides | **Achilles** | Πηληϊάδης / Πηλείδης |
| Aeacus' grandson | **Achilles** | Αἰακίδης of Achilles; "Aeacus' son" = **Peleus** |
| the swift-footed / war-minded son of Aeacus; Aeacus' blameless son | **Achilles** | the fixed epithet formulas, 16.140, 16.854 |
| Thetis' son | **Achilles** | |
| Tydeus' son; son of Tydeus; Tydides | **Diomedes** | Τυδεΐδης — Tydeus himself appears only in the Theban back-story |
| Menoetius' son; son of Menoetius | **Patroclus** | Μενοιτιάδης |
| Telamonian Ajax; Telamon's son; son of Telamon | **Ajax** (the greater) | see the two-Ajaxes note below |
| Oïleus' son; son of Oïleus; swift Ajax; the lesser Ajax | **Ajax son of Oïleus** | a separate headword |
| Laertes' son | **Odysseus** | |
| Nestor's son | **Antilochus** (usually) | or Thrasymedes; the scene decides |
| Neleus' son; Neleian | **Nestor** | |
| Anchises' son | **Aeneas** | |
| Hippolochus' son | **Glaucus** | |
| Lycaon's son | **Pandarus** | *this* Lycaon is Pandarus's father (2.826), **not** Priam's son |
| Panthous' son; Panthoides | **Polydamas** (usually) | also Euphorbus and Hyperenor; the scene decides |
| Priam's son; Priamides | context | Hector by default; also Paris, Helenus, Deiphobus, Polydorus, Lycaon, Troilus, and the Book 24 roll-call |
| Dardanus' descendant; Dardanides | **Priam** | Δαρδανίδης |
| Capaneus' son | **Sthenelus** | |
| Cronos' son; son of Cronos; Cronion | **Zeus** | Κρονίδης / Κρονίων; "Cronos" *alone* = the Titan father |
| Atreus' sons (dual/plural); the two sons of Atreus | **Agamemnon** and **Menelaus** together | the pair, not one man |

### Context-dependent (resolve by scene — flag, don't guess)

| As it appears | Could be | Rule |
|---|---|---|
| Atreus' son; son of Atreus; Atreides (singular) | **Agamemnon** *or* **Menelaus** | Agamemnon by a wide margin — he is "lord of men," the one in command, and the referent in the quarrel of Book 1, the assemblies, and the embassy. Menelaus when the scene is the duel with Paris (Book 3), the oath-breaking and his wounding (Book 4), his aristeia and the fight over Patroclus' body (Books 13, 17). When the poem attaches "lord of men" or "wide-ruling," it is Agamemnon. |
| Ajax (unqualified) | **Ajax** (Telamonian) *or* **Ajax son of Oïleus** | Telamonian unless the line marks the other (swift, lesser, Oïleus'). The dual **Ajaxes** (Αἴαντε) is a third headword: the pair fighting as a unit. |
| Lycaon | **Lycaon** (Priam's son, killed at 21.34–135) *or* Pandarus's father (2.826) | two men; keep two entries |
| Polydorus | **Polydorus** (Priam's youngest son, killed 20.407ff) *or* Nestor's rival in the Book 23 games | two men |
| Xanthus | the river **Scamander** *or* **Xanthus** (Achilles' immortal horse) *or* a Trojan victim (5.152) | three referents; the river is the god who fights Achilles in Book 21 |
| Adrastus / Adrestus | **Adrastus** (king of Sicyon, 2.572) *or* **Adrestus** (Trojan leader, 2.830) *or* the suppliant killed at 6.37–65 | the spelling split is deliberate; see `CONVENTIONS.md` |
| Hippothous | the Pelasgian leader (2.840) *or* Priam's son (24.251) | two men |
| Thoas | the Aetolian leader *or* Thoas king of Lemnos (Book 23) | two men |
| Chryses / Chryseis / Chryse | priest, daughter, town | three headwords, one root — cross-link all three |
| the old man | context | Priam, Nestor, Phoenix, or Chryses, per scene |

### Cult titles and second names (both forms are headwords)

| Pair | Note |
|---|---|
| **Paris** / **Alexandros** | one man; the translation uses both per the Book 3 policy in `CONVENTIONS.md` |
| **Troy** / **Ilion** | one city (Ἴλιος); both spellings occur throughout |
| **Apollo** / **Phoebus** / **Smintheus** | Phoebus and Smintheus are kept as cult titles |
| **Aphrodite** / **Cypris** | Cypris is used in Book 5 only |
| **Ares** / **Enyalius** | |
| **Athena** / **Pallas** / **Tritogeneia** | cult titles, kept as spellings. Ἀτρυτώνη is *translated*, not transliterated — it appears as "Unwearied one" (2.157, 5.115, 5.714), so it is an alias phrase, not a headword. |
| **Scamander** / **Xanthus** (the river) | "Xanthus" is what the gods call it, "Scamander" what men call it — the poem says so outright at 20.74 |
| **Ocean** / **Oceanus** | one entity, two spellings in the translation: "Ocean" as the encircling stream (15 hits, 1.423 etc.), "Oceanus" as the named god in the Deception of Zeus (4 hits, all Book 14, incl. "the begetting of the gods," 14.201). Make **Ocean** the headword and **Oceanus** a cross-reference. |

### Divine epithets that stand alone as names

Where the translation uses an epithet substantively, it resolves to the god:

| Substantive form | Headword |
|---|---|
| the far-striker; the worker-from-afar; god of the silver bow; the Lycian-born | **Apollo** |
| grey-eyes; the driver of the spoil | **Athena** |
| the cloud-gatherer; the counselor; who thunders on high; wide-seeing; aegis-bearing; father of men and gods | **Zeus** |
| the earth-shaker; who holds the earth | **Poseidon** |
| the slayer of Argus; the guide | **Hermes** |
| crook-footed; famed for craft | **Hephaestus** |
| the old man of the sea | **Nereus** — Thetis's father, so designated but never named in the Iliad |

### Collective names for the Greeks (all three = the same host)

| Ethnonym | Note |
|---|---|
| **Achaeans** | the poem's default name (also *Achaean* sg., adj.) |
| **Argives** | from Argos; interchangeable for the whole host |
| **Danaans** | third synonym, metrically convenient; same referent |

**Not** synonyms, though sometimes loosely used: **Myrmidons** and **Hellenes**
— both, with "Achaeans," are the three names of Achilles' own contingent at
2.684, and "Hellenes" is still a narrow regional term at 2.530 ("all Hellenes and
Achaeans"), not yet the later panhellenic sense. Keep these distinct from the
whole host.

---

## Genealogy skeletons

Compact family trees for the houses the poem keeps returning to. Entry-writers
draw the **Kin** field from these; anything here is attested in the text unless
marked "(later tradition)".

**House of Aeacus (Phthia / the Myrmidons).**
Aeacus → **Peleus** (m. **Thetis**, daughter of Nereus) → **Achilles** →
Neoptolemus (named at 19.326–333 as a boy on Scyros). **Patroclus**, son of
**Menoetius**, is Achilles' companion, not his kin. **Phoenix** is his foster-father
and tutor (9.432–495); **Automedon** his charioteer.

**House of Atreus (Mycenae / Sparta).**
Tantalus → Pelops → **Atreus** and **Thyestes**; Atreus → **Agamemnon** (m.
**Clytemnestra**) and **Menelaus** (m. **Helen**, daughter of Zeus and Leda).
Agamemnon's daughters are named at 9.144–148 (Chrysothemis, Laodice, Iphianassa).
The sceptre's descent — Hephaestus → Zeus → Hermes → Pelops → Atreus → Thyestes →
Agamemnon — is given at 2.101–108.

**House of Priam (Troy).**
Dardanus → Erichthonius → **Tros** → **Ilus**, **Assaracus**, Ganymede;
Ilus → **Laomedon** → **Priam** (m. **Hecuba**, daughter of Dymas) and Tithonus,
Lampus, Clytius, Hicetaon. Priam's sons include **Hector** (m. **Andromache**,
daughter of **Eëtion** of Thebe) → **Astyanax**; **Paris/Alexandros**;
**Helenus** the seer; **Deiphobus**; **Polydorus**; **Lycaon** (by **Laothoe**,
daughter of **Altes**); **Troilus** and **Mestor** (dead before the poem, 24.257);
and the Book 24 roll-call (Agathon, Pammon, Antiphonus, Polites, Dius, 24.249–252).
Daughters include **Laodice** and **Cassandra**.

**House of Assaracus (the Dardanian line).**
Assaracus → Capys → **Anchises** (+ **Aphrodite**) → **Aeneas** (m. Creusa,
Priam's daughter). Aeneas' survival and future rule over the Trojans is prophesied
by Poseidon at 20.302–308 — the poem's one glance past its own ending.

**Pylos.**
**Neleus** → **Nestor** → **Antilochus** (killed after the poem's end; his death is
foreshadowed) and **Thrasymedes**.

**Argos / the Theban war.**
**Tydeus** (of the Seven against Thebes) → **Diomedes**; **Capaneus** →
**Sthenelus**; **Talaus** → **Mecisteus** → **Euryalus**. The fathers' Theban
exploits are the standing measure Agamemnon uses to shame the sons (4.370–400).

**Lycia.**
**Zeus** + Laodameia → **Sarpedon**; **Bellerophon** → **Hippolochus** →
**Glaucus**. Glaucus and Diomedes discover their grandfathers' guest-friendship
and exchange armor instead of blows (6.119–236).

**Divine (as the poem uses them).**
**Cronos** (+ Rhea) → **Zeus**, **Poseidon**, **Hades**, **Hera**, Demeter, Hestia;
the three brothers divide sky, sea, and underworld by lot (15.187–193). Zeus's
children in the poem: **Athena**, **Apollo** and **Artemis** (by **Leto**),
**Ares** and **Hebe** (by **Hera**), **Aphrodite** (by **Dione**, 5.370–417),
**Hermes**, **Persephone**, **Heracles** (by Alcmene), **Sarpedon**.
**Ocean** and **Tethys** are named as "the origin of the gods" (14.201, 14.246).

---

## Homonym register

Names borne by more than one figure. Each gets its own entry; entries cross-link
and say plainly that the other exists. Drawn from the named-entity register in
`CONVENTIONS.md`, which logged these as they were fixed book by book.

| Name | The figures |
|---|---|
| Adrastus / Adrestus | Sicyon king (2.572); Trojan leader (2.830); suppliant killed 6.37–65 |
| Ajax | Telamonian; son of Oïleus; (and the dual **Ajaxes**) |
| Amphidamas | of Cythera (10.268–270); of Opoeis (23.87); a third at 10.269 |
| Echepolus | Trojan killed 4.458; son of Anchises of Sicyon (23.296) |
| Hippothous | Pelasgian leader (2.840); son of Priam (24.251) |
| Lycaon | father of Pandarus (2.826); son of Priam (21.34–135) |
| Noëmon | Lycian killed 5.678; companion of Antilochus (23.612) |
| Podargus | Hector's horse (8.185); Menelaus's horse (23.295) |
| Polydorus | son of Priam (20.407); Nestor's rival (23.637) |
| Thoas | Aetolian leader; king of Lemnos (23.745) |
| Chryses | the priest; also the town **Chryse** and his daughter **Chryseis** |

---

### Additions from Phase 3 (2026-07-27/28)

Entry-writing reconciled every headword against the text and found bearers the
table above missed. Recorded here so the register stays the single authority;
details and citations are in the written entries.

| Name | The bearers |
|---|---|
| Areithous | the Club-man of Nestor's tale (= Menesthius' father, 7.9–10); a Thracian charioteer killed at 20.487 |
| Asius | Hyrtacus' son of Arisbe; Dymas' son, Hecuba's brother (16.717); father of Phaenops of Abydos (17.583) |
| Bias | a Pylian (4.296); an Athenian (13.691); father of Laogonus and Dardanus (20.460) |
| Chromius | four or five bearers on both sides (4.295, 5.160, 5.677, 8.275, 17.494) |
| Echius | father of Mecisteus (8.333); an Achaean killed at 15.339; a Trojan killed at 16.416 |
| Enops | three bearers (14.444, 16.401, 23.634) |
| Epistrophus | Phocian (2.517); Halizonian (2.856); Euenus' son killed at Lyrnessus (2.692) |
| Eurypylus | Euaemon's son; the hero of Cos ("Cos, city of Eurypylus," 2.677) |
| Eëtion | Andromache's father; of Imbros, Lycaon's ransomer (21.43); Podes' father (17.575) |
| Haemon | a Pylian (4.296); a Cadmean, Maeon's father (4.394); Alcimedon's grandfather (17.467) |
| Iphiclus | Protesilaus' father; the runner Nestor beat (23.636) — the text does not say whether one man; keep unmerged |
| Mecisteus | Talaus' son (Theban generation); Echius' son the stretcher-bearer; killed at 15.339 |
| Melanippus | four bearers (8.276, 15.547ff, 16.695, 19.240) |
| Mulius | three, all killed (11.739, 16.696, 20.472) |
| Orestes | Agamemnon's son (embassy offer only); an Achaean (5.705); a Trojan killed at 12.193 |
| Peisander | Antimachus' son (11.122); a Trojan killed by Menelaus (13.601ff); a Myrmidon captain (16.193) |
| Phaenops | three (5.152, 17.312, 17.583) |
| Thestor | Calchas' father (1.69); Alcmaon's father (12.394); Enops' son killed at 16.401 |
| Thoas | a **third** bearer beyond the two above: a Trojan killed by Menelaus at 16.311 |
| Thoon | four contexts (5.152, 11.422, 12.140, 13.545) |

## Master registry (full coverage)

The complete registry lives in **[`registry.md`](registry.md)**, generated by
`tools/build_registry.py` from a curated classification joined against
`occurrences.json`, so hit-counts and book coverage stay true to the text. The
alias-resolution and genealogy sections above are the editorial judgment that
feeds it; the generator also reports every unclassified token, so coverage is
auditable.

The registry is the **work list for Phase 3**: one entry per headword, sliced
alphabetically across parallel writers.

To regenerate after any edit to the classification or the translation:

```powershell
python tools\build_index.py           # Phase 1: refresh occurrences.{json,md}
python tools\seed_pronunciations.py   # report pronunciation gaps
python tools\build_registry.py        # Phase 2: refresh registry.md + coverage audit
python tools\make_slices.py           # Phase 3: cut writer worklists
python tools\merge_index.py           # Phase 4: merge + validate -> index.md
```
