"""Phase 2, master registry: the curated classification of every real name.

Phase 1 (build_index.py) extracted every capitalized token mechanically. This
file supplies the editorial judgment Phase 1 can't: which tokens are real names,
each name's canonical headword and category, which inflectional variants and
alias-forms fold into it, and a one-line disambiguating note where the same
surface form hides several people.

The classification lives in REGISTRY below, as data. This script joins it against
`index/occurrences.json` to aggregate hit-counts and book coverage, then writes
`index/registry.{md,json}`. It also prints every occurrence token that is NOT
classified — the function-word noise plus anything a curator has not yet reached
— so coverage is auditable and nothing is dropped silently.

The Iliad's cast is long-tailed: a few dozen figures carry the poem and several
hundred are named once, killed, and never mentioned again. REGISTRY is therefore
built outward from the top: the major and middle cast are classified here, and
`--todo` reports what is left in hit-count order, which is the work queue.

Categories: MORTAL, GOD, PEOPLE, PLACE, OTHER (see canon.md).

Usage:
    python tools/build_registry.py            # build + coverage audit
    python tools/build_registry.py --todo 20  # list unclassified tokens >= 20 hits
"""
import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

# Polytonic Greek and combining diacritics must survive a legacy Windows console.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

ROOT = Path(__file__).resolve().parent.parent
OCC = ROOT / "index" / "occurrences.json"
OUT = ROOT / "index" / "registry.md"


def E(headword, cat, tokens=None, aliases="", note=""):
    return {
        "headword": headword,
        "cat": cat,
        "tokens": tokens if tokens is not None else [headword],
        "aliases": aliases,
        "note": note,
    }


# ---------------------------------------------------------------------------
# The curated registry. Every entry is an editorial decision. `tokens` lists the
# occurrence.json keys whose counts roll up into this headword (inflected forms,
# folded aliases). `aliases` records other names/epithets used for the figure;
# `note` disambiguates or places them.
#
# Patronymic tokens (Atreus, Peleus, Tydeus, Menoetius, Aeacus...) are deliberately
# NOT folded into the son's headword: they are their own headwords, because the
# fathers are real figures with their own back-stories, and the alias table in
# canon.md is what teaches a reader that "Tydeus' son" means Diomedes. Folding
# them would inflate the son's count with 100+ refs that never name him.
# ---------------------------------------------------------------------------
REGISTRY = [
    # ===================== GODS & divine / supernatural =====================
    E("Zeus", "GOD", ["Zeus"],
      "son of Cronos; the cloud-gatherer; the counselor; aegis-bearing; father of men and gods",
      "presides over the war and the plot; his promise to Thetis drives the poem"),
    E("Athena", "GOD", ["Athena", "Pallas", "Tritogeneia"],
      "Pallas; grey-eyed; grey-eyes; the driver of the spoil; Unwearied one (Ἀτρυτώνη, translated)",
      "the Achaeans' fiercest divine partisan; breaks the truce in Book 4, kills Hector's hope in 22"),
    E("Hera", "GOD", ["Hera"], "white-armed; ox-eyed lady Hera",
      "Zeus's wife and adversary; deceives him in Book 14 to turn the battle"),
    E("Apollo", "GOD", ["Apollo", "Phoebus", "Smintheus"],
      "Phoebus; Smintheus; the far-striker; the worker-from-afar; god of the silver bow; the Lycian-born",
      "opens the poem with the plague; Troy's chief defender; strikes Patroclus down"),
    E("Poseidon", "GOD", ["Poseidon"], "the earth-shaker; who holds the earth",
      "backs the Achaeans; rallies them in Books 13-14 behind Zeus's back"),
    E("Ares", "GOD", ["Ares", "Enyalius"],
      "Enyalius; bane of mortals; blood-stained; stormer of walls; brazen Ares; turncoat",
      "fights for Troy; wounded by Diomedes with Athena's help (5.855-863)"),
    E("Aphrodite", "GOD", ["Aphrodite", "Cypris"], "Cypris (Book 5 only); laughter-loving",
      "Paris's patron; rescues him from the duel; wounded by Diomedes (5.330-354)"),
    E("Thetis", "GOD", ["Thetis"], "silver-footed",
      "sea-nymph, Achilles' mother; wins Zeus's promise in Book 1 and the new armor in 18"),
    E("Hephaestus", "GOD", ["Hephaestus"], "crook-footed; famed for craft; famed",
      "smith-god; makes Achilles' shield (18.478-608) and fights the river in 21"),
    E("Hermes", "GOD", ["Hermes", "Argus"], "the slayer of Argus; the guide",
      "escorts Priam through the Achaean camp in Book 24. Every occurrence of 'Argus' "
      "in the poem is inside his fixed epithet ἀργεϊφόντης — the giant watchman is never "
      "a character here, so the token folds in rather than earning an entry"),
    E("Artemis", "GOD", ["Artemis"], "", "Apollo's sister; fights for Troy and is humiliated by Hera in Book 21"),
    E("Leto", "GOD", ["Leto"], "lovely-haired", "mother of Apollo and Artemis; Trojan-side"),
    E("Iris", "GOD", ["Iris"], "wind-footed swift Iris; swift-footed Iris",
      "the gods' messenger throughout"),
    E("Hades", "GOD", ["Hades"], "", "lord of the dead; the underworld itself by metonymy"),
    E("Cronos", "GOD", ["Cronos"], "crooked-counseled",
      "Zeus's father; the token is overwhelmingly the patronymic 'Cronos' son' = Zeus"),
    E("Hebe", "GOD", ["Hebe"], "the lady Hebe",
      "pours the gods' nectar (4.2), sets the wheels on Hera's chariot (5.722), and bathes "
      "and dresses Ares after Paieon heals him (5.905). NB not 'Ares' nurse' — the poem "
      "does not say that"),
    E("Dione", "GOD", ["Dione"], "", "Aphrodite's mother in this poem (5.370-417)"),
    E("Ocean", "GOD", ["Ocean", "Oceanus"], "Oceanus",
      "the encircling stream and the god; with Tethys 'the begetting of the gods' (14.201)"),
    E("Tethys", "GOD", ["Tethys"], "", "Ocean's consort, named in the Deception of Zeus"),
    E("Dawn", "GOD", ["Dawn"], "rosy-fingered; early-born; in her saffron robe; fair-throned",
      "personified; her formulas open days throughout. NB 'of the golden throne' "
      "(χρυσόθρονος) is Hera's, not hers — CONVENTIONS.md corrected 2026-07-27"),
    E("Sleep", "GOD", ["Sleep"], "", "personified; Hera's accomplice in Book 14"),
    E("Death", "GOD", ["Death"], "", "personified; with Sleep carries Sarpedon home (16.681-683)"),
    E("Strife", "GOD", ["Strife"], "", "Ἔρις personified, capitalized per CONVENTIONS.md"),
    E("Panic", "GOD", ["Panic"], "", "Φόβος personified"),
    E("Terror", "GOD", ["Terror"], "", "Δεῖμος personified"),
    E("Blindness", "GOD", ["Blindness"], "", "Ἄτη personified; Agamemnon's plea in Book 19"),
    E("Fate", "GOD", ["Fate"], "", "personified where capitalized; see CONVENTIONS.md on μοῖρα κραταιή"),
    E("Erinyes", "GOD", ["Erinyes", "Erinys"], "who walk in mist",
      "the avenging Furies; fixed as Erinys/Erinyes everywhere per the audit"),
    E("Muses", "GOD", ["Muses", "Muse"], "", "invoked for the Catalogue (2.484-493)"),
    E("Graces", "GOD", ["Graces"], "", "Χάριτες"),
    E("Seasons", "GOD", ["Seasons"], "", "Ὧραι, keepers of the gates of heaven"),
    E("Nereids", "GOD", ["Nereids"], "", "Thetis's sisters; the catalogue at 18.39-49"),
    E("Night", "GOD", ["Night"], "", "personified; even Zeus fears her (14.259-261)"),
    E("Dream", "GOD", ["Dream"], "", "the destructive Dream Zeus sends to Agamemnon (Book 2)"),
    E("Earth", "GOD", ["Earth"], "", "invoked in oaths alongside Zeus and the Sun"),
    E("Sun", "GOD", ["Sun"], "", "Helios; oath-witness who sees and hears all"),
    E("Paiëon", "GOD", ["Paiëon"], "", "the gods' physician, who heals Ares and Hades"),
    E("Asclepius", "GOD", ["Asclepius"], "", "healer; father of Machaon and Podaleirius"),
    E("Boreas", "GOD", ["Boreas"], "", "the north wind, personified and genealogically active"),
    E("Zephyrus", "GOD", ["Zephyrus"], "", "the west wind"),
    E("Scamander", "PLACE", ["Scamander"], "Xanthus (the gods' name for it, 20.74)",
      "Troy's river and its god, who fights Achilles in Book 21. The token 'Xanthus' is "
      "NOT folded in: it is four different things in this poem — this river, the Lycian "
      "river (2.877, 5.479, 6.172, 12.313), Achilles' immortal horse (16.149, 19.400ff) "
      "and a Trojan killed by Diomedes (5.152). Folding it made Scamander's hit-count and "
      "ref-list wrong; see the Xanthus headword"),
    E("Simois", "PLACE", ["Simois"], "", "Troy's second river; joins Scamander against Achilles"),
    E("Spercheius", "PLACE", ["Spercheius"], "", "river of Phthia; Achilles' vowed hair is cut for Patroclus instead"),
    E("Tartarus", "PLACE", ["Tartarus"], "", "the pit below Hades; Zeus's standing threat (8.13-16)"),
    E("Olympus", "PLACE", ["Olympus", "Olympian"], "Olympian", "the gods' seat"),

    # ============================== MORTALS ================================
    E("Achilles", "MORTAL", ["Achilles"],
      "swift-footed; brilliant; Zeus-sprung; Peleus' son; Aeacus' grandson; Thetis's son",
      "the poem's subject; his wrath, withdrawal, and return structure the whole"),
    E("Hector", "MORTAL", ["Hector"],
      "of the flashing helmet; glorious; man-slaughtering; breaker of horses; Priam's son",
      "Troy's champion and its doom; killed by Achilles in Book 22"),
    E("Agamemnon", "MORTAL", ["Agamemnon"],
      "lord of men; wide-ruling; the lord; Atreus' son; shepherd of the people",
      "commander of the Achaean host; his seizure of Briseis starts the action"),
    E("Patroclus", "MORTAL", ["Patroclus"], "Menoetius' son; Zeus-sprung",
      "Achilles' companion; his death in Achilles' armor (Book 16) turns the poem"),
    E("Odysseus", "MORTAL", ["Odysseus"],
      "resourceful; of many devices; the equal of Zeus in counsel; sacker of cities; Laertes' son",
      "the Achaeans' tactician; the embassy, the night raid, the assembly"),
    E("Ajax", "MORTAL", ["Ajax"],
      "Telamonian; Telamon's son; wall of the Achaeans; the great Ajax",
      "the Achaeans' bulwark; unqualified 'Ajax' means him unless the line marks the other"),
    E("Ajaxes", "MORTAL", ["Ajaxes"], "the two Ajaxes (Αἴαντε)",
      "the dual: Telamonian Ajax and Ajax son of Oïleus fighting as a unit"),
    E("Ajax son of Oïleus", "MORTAL", [], "swift Ajax; the lesser Ajax; Oïleus' son",
      "the Locrian leader, promised his own headword by canon.md's alias table but "
      "missed when the registry was seeded — found in the 2026-07-28 review pass. "
      "tokens is deliberately empty: his name IS 'Ajax', and that token stays with "
      "the Telamonian per canon's default rule, so his citations all come from "
      "shared-token lines and the merge flags every one (documented in _flags-01.md). "
      "NB: added after make_slices ran; his worklist block was inserted by hand into "
      "_worklist-01.md — rerunning make_slices would reshuffle every slice boundary "
      "and misalign all eight entries files. Do not rerun it without rewriting them."),
    E("Diomedes", "MORTAL", ["Diomedes"], "Tydeus' son; good at the war-cry",
      "the aristeia of Book 5; wounds Aphrodite and Ares"),
    E("Menelaus", "MORTAL", ["Menelaus"], "dear to Ares; tawny-haired; good at the war-cry; Atreus' son",
      "the wronged husband; duels Paris in Book 3, defends Patroclus' body in 17"),
    E("Nestor", "MORTAL", ["Nestor", "Gerenian"], "the Gerenian horseman; Neleus' son",
      "the aged counselor of Pylos; his advice sets the plot at several turns. "
      "'Gerenian' occurs only inside his fixed epithet, so the token folds in here"),
    E("Priam", "MORTAL", ["Priam"], "Dardanus' descendant; of the good ash spear",
      "king of Troy; ransoms Hector's body in Book 24"),
    E("Aeneas", "MORTAL", ["Aeneas"], "Anchises' son",
      "Dardanian leader; his survival and future rule are prophesied at 20.302-308"),
    E("Paris", "MORTAL", ["Paris", "Alexandros"], "Alexandros; godlike",
      "one man, both names used per the Book 3 policy; his abduction of Helen caused the war"),
    E("Helen", "MORTAL", ["Helen"], "of the trailing robe",
      "in Troy with Paris; her self-reproach frames Books 3, 6, and 24"),
    E("Sarpedon", "MORTAL", ["Sarpedon"], "",
      "Lycian king, son of Zeus; killed by Patroclus (16.419-505) as Zeus grieves"),
    E("Glaucus", "MORTAL", ["Glaucus"], "Hippolochus' son",
      "Lycian co-leader; exchanges armor with Diomedes (6.119-236)"),
    E("Idomeneus", "MORTAL", ["Idomeneus"], "", "Cretan leader; his aristeia in Book 13"),
    E("Meriones", "MORTAL", ["Meriones"], "the equal of Enyalius",
      "Idomeneus's squire and companion"),
    E("Antilochus", "MORTAL", ["Antilochus"], "Nestor's son",
      "brings Achilles the news of Patroclus' death; wins by guile in the Book 23 chariot race"),
    E("Teucer", "MORTAL", ["Teucer"], "", "Telamonian Ajax's half-brother; the host's best archer"),
    E("Polydamas", "MORTAL", ["Polydamas"], "Panthous' son",
      "Hector's prudent counterpart, whose advice Hector rejects to his ruin"),
    E("Andromache", "MORTAL", ["Andromache"], "white-armed",
      "Hector's wife; the farewell at the Scaean Gates (6.390-502) and the laments of 22 and 24"),
    E("Hecuba", "MORTAL", ["Hecuba"], "", "Priam's wife, mother of Hector"),
    E("Briseis", "MORTAL", ["Briseis"], "fair-cheeked",
      "Achilles' prize, seized by Agamemnon; the quarrel's occasion; laments Patroclus (19.282-302)"),
    E("Chryseis", "MORTAL", ["Chryseis"], "", "Chryses' daughter, Agamemnon's prize, returned in Book 1"),
    E("Chryses", "MORTAL", ["Chryses"], "", "priest of Apollo whose prayer brings the plague"),
    E("Calchas", "MORTAL", ["Calchas"], "Thestor's son", "the army's seer"),
    E("Phoenix", "MORTAL", ["Phoenix"], "", "Achilles' old tutor; the central speech of the embassy (9.432-605)"),
    E("Automedon", "MORTAL", ["Automedon"], "", "Achilles' charioteer"),
    E("Thersites", "MORTAL", ["Thersites"], "", "the one common soldier who speaks; beaten by Odysseus (2.211-277)"),
    E("Machaon", "MORTAL", ["Machaon"], "", "healer, son of Asclepius; his wounding drives Book 11"),
    E("Sthenelus", "MORTAL", ["Sthenelus"], "Capaneus' son", "Diomedes' charioteer"),
    E("Talthybius", "MORTAL", ["Talthybius"], "", "Agamemnon's herald"),
    E("Idaeus", "MORTAL", ["Idaeus"], "", "Trojan herald; drives Priam's wagon in Book 24"),
    E("Antenor", "MORTAL", ["Antenor"], "", "Trojan elder who urges giving Helen back"),
    E("Helenus", "MORTAL", ["Helenus"], "", "Priam's son, a seer, who advises Hector"),
    E("Deiphobus", "MORTAL", ["Deiphobus"], "", "Priam's son; Athena's fatal disguise at 22.226-247"),
    E("Agenor", "MORTAL", ["Agenor"], "", "Antenor's son; stands against Achilles at 21.544-598"),
    E("Cebriones", "MORTAL", ["Cebriones"], "", "Hector's charioteer, killed by Patroclus"),
    E("Asius", "MORTAL", ["Asius"], "", "Trojan-side leader; killed by Idomeneus in Book 13"),
    E("Pandarus", "MORTAL", ["Pandarus"], "Lycaon's son",
      "the archer whose shot breaks the truce (4.86-140); killed by Diomedes"),
    E("Euphorbus", "MORTAL", ["Euphorbus"], "Panthous' son",
      "wounds Patroclus first; killed by Menelaus in Book 17"),
    E("Asteropaeus", "MORTAL", ["Asteropaeus"], "", "Paeonian, ambidextrous; killed by Achilles in Book 21"),
    E("Lycaon", "MORTAL", ["Lycaon"], "",
      "Priam's son, killed suppliant at 21.34-135; distinct from Pandarus's father (2.826)"),
    E("Polydorus", "MORTAL", ["Polydorus"], "",
      "Priam's youngest, killed at 20.407ff; distinct from Nestor's rival at 23.637"),
    E("Astyanax", "MORTAL", ["Astyanax"], "Scamandrius",
      "Hector's infant son; glossed 'lord of the city' (6.402-403, 22.506-507)"),
    E("Peleus", "MORTAL", ["Peleus"], "Aeacus' son",
      "Achilles' father, in Phthia throughout; the token is mostly the patronymic"),
    E("Atreus", "MORTAL", ["Atreus"], "",
      "father of Agamemnon and Menelaus; the token is overwhelmingly the patronymic — see canon.md"),
    E("Tydeus", "MORTAL", ["Tydeus"], "",
      "Diomedes' father, of the Seven against Thebes; the token is mostly the patronymic"),
    E("Menoetius", "MORTAL", ["Menoetius"], "", "Patroclus' father; the token is mostly the patronymic"),
    E("Aeacus", "MORTAL", ["Aeacus"], "",
      "Peleus' father; 'Aeacus' grandson' = Achilles, 'Aeacus' son' = Peleus (see CONVENTIONS.md)"),
    E("Telamon", "MORTAL", ["Telamon", "Telamonian"], "Telamonian", "father of Ajax and Teucer"),
    E("Oïleus", "MORTAL", ["Oïleus", "Oileus"], "", "father of the lesser Ajax"),
    E("Laomedon", "MORTAL", ["Laomedon"], "", "Priam's father, who cheated Poseidon and Apollo of their wages"),
    E("Tros", "MORTAL", ["Tros"], "", "eponym of the Trojans; also a victim killed at 20.463"),
    E("Dardanus", "MORTAL", ["Dardanus"], "", "founder of the Trojan line; Zeus's son"),
    E("Ilus", "MORTAL", ["Ilus"], "",
      "son of Tros, father of Laomedon (20.231-236); his tomb is a landmark on the plain. "
      "The poem never glosses his name against Ilion — do not assert the etymology"),
    E("Anchises", "MORTAL", ["Anchises"], "", "Aeneas' father, by Aphrodite"),
    E("Panthous", "MORTAL", ["Panthous"], "", "Trojan elder; father of Polydamas, Euphorbus, Hyperenor"),
    E("Hippolochus", "MORTAL", ["Hippolochus"], "", "Glaucus' father, son of Bellerophon"),
    E("Bellerophon", "MORTAL", ["Bellerophon"], "", "Glaucus' grandfather; his story at 6.152-211"),
    E("Eëtion", "MORTAL", ["Eëtion"], "", "king of Thebe, Andromache's father, killed by Achilles"),
    E("Laothoe", "MORTAL", ["Laothoe"], "", "Altes' daughter, Priam's wife; mother of Lycaon and Polydorus"),
    E("Altes", "MORTAL", ["Altes"], "", "lord of the Lelegians, Laothoe's father"),
    E("Heracles", "MORTAL", ["Heracles"], "the might of Heracles",
      "in the past tense throughout; the sack of Troy under Laomedon"),
    E("Meleager", "MORTAL", ["Meleager"], "", "Phoenix's exemplum of ruinous anger (9.529-599)"),
    E("Eurypylus", "MORTAL", ["Eurypylus"], "Euaemon's son",
      "Thessalian leader; wounded in Book 11 and tended by Patroclus, which delays him fatally"),
    E("Euaemon", "MORTAL", ["Euaemon"], "", "Eurypylus's father; the token is the patronymic"),
    E("Neleus", "MORTAL", ["Neleus"], "", "Nestor's father, king of Pylos; mostly patronymic"),
    E("Thoas", "MORTAL", ["Thoas"], "",
      "the Aetolian leader; distinct from Thoas king of Lemnos (23.745) — see canon.md"),
    E("Phyleus", "MORTAL", ["Phyleus"], "", "Meges's father; also a rival of Nestor's in the Book 23 games"),
    E("Meges", "MORTAL", ["Meges"], "Phyleus' son", "leader of the Dulichian contingent"),
    E("Oeneus", "MORTAL", ["Oeneus"], "", "Tydeus's father and Meleager's; the Calydonian house"),
    E("Acamas", "MORTAL", ["Acamas"], "",
      "Trojan-side leader (Antenor's son) and a Thracian leader of the same name (2.844)"),
    E("Tlepolemus", "MORTAL", ["Tlepolemus"], "",
      "Heracles' son, leader of the Rhodians; killed by Sarpedon (5.628-662)"),
    E("Menestheus", "MORTAL", ["Menestheus"], "Peteos' son", "the Athenian leader"),
    E("Peteos", "MORTAL", ["Peteos"], "", "Menestheus's father; the token is the patronymic"),
    E("Polypoetes", "MORTAL", ["Polypoetes"], "", "Lapith leader, with Leonteus"),
    E("Leonteus", "MORTAL", ["Leonteus"], "", "Lapith leader, with Polypoetes"),
    E("Peneleos", "MORTAL", ["Peneleos"], "", "Boeotian leader"),
    E("Leïtus", "MORTAL", ["Leïtus"], "", "Boeotian leader"),
    E("Ascalaphus", "MORTAL", ["Ascalaphus"], "", "son of Ares, killed in Book 13"),
    E("Amphimachus", "MORTAL", ["Amphimachus"], "", "Epeian leader, killed by Hector in Book 13"),
    E("Protesilaus", "MORTAL", ["Protesilaus"], "",
      "the first Achaean ashore and the first to die; his ship is the fighting's focus in "
      "Books 15-16. His killer is withheld: 2.701 says only 'a Dardanian man had killed him', "
      "so do not credit Hector"),
    E("Dolon", "MORTAL", ["Dolon"], "",
      "the Trojan scout caught and killed by Odysseus and Diomedes in Book 10"),
    E("Rhesus", "MORTAL", ["Rhesus"], "", "Thracian king killed asleep in the Doloneia"),
    E("Socus", "MORTAL", ["Socus"], "", "Trojan who wounds Odysseus and is killed by him (11.428-458)"),
    E("Iphidamas", "MORTAL", ["Iphidamas"], "", "Antenor's son, killed by Agamemnon in Book 11"),
    E("Coon", "MORTAL", ["Coon"], "", "Antenor's son, who wounds Agamemnon avenging Iphidamas"),
    E("Melanippus", "MORTAL", ["Melanippus"], "", "Trojan killed by Antilochus in Book 15"),
    E("Alcathous", "MORTAL", ["Alcathous"], "", "Trojan killed by Idomeneus in Book 13"),
    E("Othryoneus", "MORTAL", ["Othryoneus"], "", "suitor of Cassandra, killed by Idomeneus"),
    E("Hyrtacus", "MORTAL", ["Hyrtacus"], "", "Asius's father; the token is the patronymic"),
    E("Hippothous", "MORTAL", ["Hippothous"], "",
      "Pelasgian leader (2.840); distinct from Priam's son of the same name (24.251)"),
    E("Pylaemenes", "MORTAL", ["Pylaemenes"], "", "Paphlagonian leader"),
    E("Bias", "MORTAL", ["Bias"], "", "a name borne by more than one minor figure"),
    E("Chiron", "MORTAL", ["Chiron"], "", "the centaur who taught Achilles medicine and gave Peleus his spear"),
    E("Lycurgus", "MORTAL", ["Lycurgus"], "",
      "the man who drove Dionysus into the sea (6.130-140); also an Arcadian in Nestor's tale"),
    E("Proetus", "MORTAL", ["Proetus"], "", "the king who sent Bellerophon to Lycia"),
    E("Eurystheus", "MORTAL", ["Eurystheus"], "", "the king Heracles served; in the back-story only"),
    E("Admetus", "MORTAL", ["Admetus"], "", "Eumelus's father"),
    E("Mecisteus", "MORTAL", ["Mecisteus"], "", "of the Theban generation; also a minor victim"),
    E("Capaneus", "MORTAL", ["Capaneus"], "", "Sthenelus's father, of the Seven against Thebes"),
    E("Areithous", "MORTAL", ["Areithous"], "", "'the mace-man' of Nestor's reminiscence (7.136-149)"),
    E("Ereuthalion", "MORTAL", ["Ereuthalion"], "", "the champion young Nestor killed (7.136-156)"),
    E("Amarynceus", "MORTAL", ["Amarynceus"], "", "Epeian whose funeral games Nestor recalls (23.629-642)"),
    E("Theano", "MORTAL", ["Theano"], "", "Antenor's wife, Athena's priestess in Troy (6.297-310)"),
    E("Laodice", "MORTAL", ["Laodice"], "", "Priam's daughter; also a daughter of Agamemnon (9.145)"),
    E("Cassandra", "MORTAL", ["Cassandra"], "", "Priam's daughter; first sees the body returning (24.697-706)"),
    E("Polites", "MORTAL", ["Polites"], "", "Priam's son, the Trojan lookout"),
    E("Antimachus", "MORTAL", ["Antimachus"], "", "the Trojan who urged killing Menelaus; his sons die for it (11.122-148)"),
    E("Hicetaon", "MORTAL", ["Hicetaon"], "", "Trojan elder, Priam's brother"),
    E("Thestor", "MORTAL", ["Thestor"], "", "Calchas's father; also a victim killed by Patroclus (16.401)"),
    E("Alastor", "MORTAL", ["Alastor"], "", "a Pylian companion of Nestor; also a Lycian victim"),
    E("Automedon_dup", "MORTAL", ["_none"], "", ""),
    E("Iphiclus", "MORTAL", ["Iphiclus"], "", "in the back-story; father of Protesilaus and Podarces"),
    E("Eumedes", "MORTAL", ["Eumedes"], "", "Dolon's father, a herald"),
    E("Nireus", "MORTAL", ["Nireus"], "", "the handsomest Achaean after Achilles, but weak (2.671-675)"),
    E("Schedius", "MORTAL", ["Schedius"], "", "Phocian leader"),
    E("Epistrophus", "MORTAL", ["Epistrophus"], "", "a Phocian and a Halizonian leader of the same name"),
    E("Ennomus", "MORTAL", ["Ennomus"], "", "Mysian augur, killed by Achilles"),
    E("Nastes", "MORTAL", ["Nastes"], "", "Carian leader who came to war wearing gold (2.867-875)"),
    E("Odius", "MORTAL", ["Odius"], "", "Halizonian leader, the first man Agamemnon kills (5.38-42)"),
    E("Diores", "MORTAL", ["Diores"], "", "Epeian leader killed in the Book 4 finale"),
    E("Peiroos", "MORTAL", ["Peiroos"], "", "Thracian leader who kills Diores and is killed at once"),
    E("Simoeisios", "MORTAL", ["Simoeisios"], "",
      "the youth killed by Ajax at 4.473-489, with the poem's poplar simile"),
    E("Adrastus", "MORTAL", ["Adrastus"], "",
      "king of Sicyon (2.572), Arion's owner; NB the spelling split with Adrestus — see canon.md"),
    E("Adrestus", "MORTAL", ["Adrestus"], "",
      "the Trojan-side leader (2.830) and the suppliant Agamemnon kills (6.37-65)"),
    E("Amphidamas", "MORTAL", ["Amphidamas"], "",
      "of Cythera (10.268-270) and of Opoeis (23.87) — see the homonym register in canon.md"),
    E("Echius", "MORTAL", ["Echius"], "", "a minor casualty, name borne twice"),
    E("Dolops", "MORTAL", ["Dolops"], "", "a Trojan and an Achaean of the same name"),
    E("Promachus", "MORTAL", ["Promachus"], "", "Boeotian killed by Acamas in Book 14"),
    E("Prothoenor", "MORTAL", ["Prothoenor"], "", "Boeotian killed by Polydamas in Book 14"),
    E("Archelochus", "MORTAL", ["Archelochus"], "", "Antenor's son, killed by Ajax in Book 14"),
    E("Aphareus", "MORTAL", ["Aphareus"], "", "Achaean killed by Aeneas in Book 13"),
    E("Deïpyrus", "MORTAL", ["Deïpyrus"], "", "Achaean killed by Helenus in Book 13"),
    E("Stichius", "MORTAL", ["Stichius"], "", "Athenian captain"),
    E("Periphas", "MORTAL", ["Periphas"], "", "an Aetolian herald and a Trojan of the same name"),
    E("Apisaon", "MORTAL", ["Apisaon"], "", "two Trojans of the name, both killed"),
    E("Phaenops", "MORTAL", ["Phaenops"], "", "father of several Trojan casualties; Apollo's disguise at 17.583"),
    E("Coeranus", "MORTAL", ["Coeranus"], "", "Meriones' charioteer, killed at 17.610"),
    E("Polyidus", "MORTAL", ["Polyidus"], "", "a Trojan seer's son; also a Corinthian diviner"),
    E("Mulius", "MORTAL", ["Mulius"], "", "an Epeian and a Trojan of the name"),
    E("Molus", "MORTAL", ["Molus"], "", "Meriones' father"),
    E("Oenomaus", "MORTAL", ["Oenomaus"], "", "a Trojan and an Achaean casualty of the name"),
    E("Haemon", "MORTAL", ["Haemon"], "", "in the Pylian back-story"),
    E("Enops", "MORTAL", ["Enops"], "", "father of several minor figures"),
    E("Hippasus", "MORTAL", ["Hippasus"], "", "father of several minor casualties"),
    E("Otrynteus", "MORTAL", ["Otrynteus"], "", "father of Iphition, killed by Achilles (20.382-392)"),
    E("Pelegon", "MORTAL", ["Pelegon"], "", "Asteropaeus's father, son of the river Axius"),
    E("Ilioneus", "MORTAL", ["Ilioneus"], "", "Trojan killed by Peneleos with the poem's grimmest image (14.489-505)"),
    E("Thoon", "MORTAL", ["Thoon"], "", "three Trojans of the name, all killed"),
    E("Adamas", "MORTAL", ["Adamas"], "", "Asius's son, killed by Meriones in Book 13"),
    E("Lycomedes", "MORTAL", ["Lycomedes"], "", "an Achaean captain"),
    E("Alcimedon", "MORTAL", ["Alcimedon"], "", "Myrmidon captain who takes Automedon's chariot in Book 17"),
    E("Augeias", "MORTAL", ["Augeias"], "", "Epeian king of the back-story"),
    E("Aesepus", "MORTAL", ["Aesepus"], "", "a Trojan twin killed by Euryalus (6.20-28); also a river"),
    E("Euryalus", "MORTAL", ["Euryalus"], "", "Argive captain; boxes in the Book 23 games"),
    E("Briseus", "MORTAL", ["Briseus"], "", "Briseis's father"),
    E("Hyle", "PLACE", ["Hyle"], "", "Boeotian town of the Catalogue"),
    E("Laertes", "MORTAL", ["Laertes"], "", "Odysseus's father; the token is the patronymic"),
    E("Eumelus", "MORTAL", ["Eumelus"], "Admetus' son",
      "owner of the best horses in the host (2.763-767); loses the Book 23 race to Athena's interference"),
    E("Actor", "MORTAL", ["Actor"], "",
      "father of the Molione twins (11.750) and of Astyoche's line; borne by more than one man"),
    E("Peisander", "MORTAL", ["Peisander"], "", "a Trojan killed by Agamemnon and a Myrmidon captain"),
    E("Chromius", "MORTAL", ["Chromius"], "", "several Trojan-side figures of the name"),
    E("Thrasymedes", "MORTAL", ["Thrasymedes"], "", "Nestor's son, Antilochus's brother"),
    E("Peirithous", "MORTAL", ["Peirithous"], "", "Lapith king of the back-story; Polypoetes's father"),
    E("Medon", "MORTAL", ["Medon"], "", "the lesser Ajax's half-brother, leading Philoctetes's men"),
    E("Deucalion", "MORTAL", ["Deucalion"], "", "Idomeneus's father; also a Trojan killed by Achilles"),
    E("Orestes", "MORTAL", ["Orestes"], "", "Agamemnon's son (9.142); also two casualties of the name"),
    E("Lampus", "MORTAL", ["Lampus"], "", "Trojan elder, Priam's brother; also one of Hector's horses (8.185)"),
    E("Clytius", "MORTAL", ["Clytius"], "", "Trojan elder, Priam's brother"),
    E("Antiphus", "MORTAL", ["Antiphus"], "", "a son of Priam and two others of the name"),
    E("Jason", "MORTAL", ["Jason"], "", "in the back-story; father of Euneus, who trades wine to the Achaeans"),
    E("Epeius", "MORTAL", ["Epeius"], "", "Panopeus's son; wins the boxing in Book 23"),
    E("Demeter", "GOD", ["Demeter"], "", "named in similes and formulas of the grain"),
    E("Pylians", "PEOPLE", ["Pylians"], "", "Nestor's contingent"),
    E("Pelasgians", "PEOPLE", ["Pelasgians", "Pelasgian"], "", "Trojan-side allies under Hippothous"),
    E("Hellas", "PLACE", ["Hellas"], "", "the district of Phthia, not yet all Greece"),
    E("Achaea", "PLACE", ["Achaea"], "", "the Achaeans' homeland"),
    E("Elis", "PLACE", ["Elis"], "", "in the western Peloponnese; the Epeians' land"),
    E("Lesbos", "PLACE", ["Lesbos"], "", "island Achilles sacked; Macar's seat (24.544)"),
    E("Pelion", "PLACE", ["Pelion", "Pelian"], "Pelian",
      "the Thessalian mountain; 'the Pelian ash spear' is Achilles' weapon, from Chiron"),
    E("Dog", "OTHER", ["Dog"], "the Dog of Orion",
      "the star Sirius, 'the dog of Orion,' to which Achilles' armor is compared (22.26-31)"),
    E("Orion", "OTHER", ["Orion"], "", "the constellation, on the Shield and in the star-similes"),
    E("Pleiades", "OTHER", ["Pleiades"], "", "on the Shield of Achilles (18.486)"),
    E("Bear", "OTHER", ["Bear"], "the Wagon",
      "the constellation on the Shield of Achilles, 'which men also call by the name "
      "of the Wagon' (18.487). NB only that one ref is the constellation — the token's "
      "other five hits are the imperative 'Bear up' (1.586, 2.299, 5.382, 23.587, "
      "24.549), which the entry-writer must not cite"),
    E("Niobe", "MORTAL", ["Niobe"], "", "Achilles' exemplum of eating despite grief (24.602-617)"),
    E("Bellerophon_placeholder", "MORTAL", ["_none"], "", ""),

    # ========================== PEOPLES & GROUPS ===========================
    E("Achaeans", "PEOPLE", ["Achaeans", "Achaean"],
      "long-haired; strong-greaved; bronze-shirted",
      "the poem's default name for the Greeks; = Argives = Danaans"),
    E("Argives", "PEOPLE", ["Argives", "Argive"], "", "synonym for the whole Achaean host"),
    E("Danaans", "PEOPLE", ["Danaans", "Danaan"], "of swift colts", "third synonym for the host"),
    E("Trojans", "PEOPLE", ["Trojans", "Trojan"], "horse-taming", "the defenders and their allies"),
    E("Myrmidons", "PEOPLE", ["Myrmidons"], "", "Achilles' own contingent, from Phthia"),
    E("Hellenes", "PEOPLE", ["Hellenes"], "",
      "still a narrow regional term (2.530, 2.684) — one of the three names of Achilles' contingent, not the host"),
    E("Dardanians", "PEOPLE", ["Dardanians", "Dardanian"], "", "Aeneas' Trojan-allied people"),
    E("Lycians", "PEOPLE", ["Lycians", "Lycian"], "", "Sarpedon and Glaucus's contingent, Troy's strongest allies"),
    E("Thracians", "PEOPLE", ["Thracians", "Thracian"], "", "Trojan-side allies; Rhesus's people"),
    E("Cretans", "PEOPLE", ["Cretans"], "", "Idomeneus's contingent"),
    E("Boeotians", "PEOPLE", ["Boeotians"], "", "first contingent of the Catalogue of Ships"),
    E("Locrians", "PEOPLE", ["Locrians"], "", "the lesser Ajax's contingent"),
    E("Abantes", "PEOPLE", ["Abantes"], "", "Euboean contingent under Elephenor"),
    E("Epeians", "PEOPLE", ["Epeians"], "", "Elian contingent"),
    E("Phocians", "PEOPLE", ["Phocians"], "", "Catalogue contingent"),
    E("Phthians", "PEOPLE", ["Phthians"], "", "men of Phthia"),
    E("Athenians", "PEOPLE", ["Athenians"], "", "Menestheus's contingent"),
    E("Aetolians", "PEOPLE", ["Aetolians", "Aetolian"], "", "Thoas's contingent"),
    E("Paeonians", "PEOPLE", ["Paeonians"], "", "Trojan-side allies from the Axius"),
    E("Paphlagonians", "PEOPLE", ["Paphlagonians"], "", "Trojan-side allies under Pylaemenes"),
    E("Maeonians", "PEOPLE", ["Maeonians"], "", "Trojan-side allies"),
    E("Mysians", "PEOPLE", ["Mysians"], "", "Trojan-side allies; the mule-givers of 24.278"),
    E("Cadmeans", "PEOPLE", ["Cadmeans"], "", "the Thebans of the earlier war"),
    E("Curetes", "PEOPLE", ["Curetes"], "", "besiegers of Calydon in the Meleager story"),
    E("Amazons", "PEOPLE", ["Amazons"], "the match of men", "in the back-story only"),

    # ================================ PLACES ===============================
    E("Troy", "PLACE", ["Troy", "Ilion"], "Ilion",
      "the city; both spellings occur throughout, and both are headwords"),
    E("Ida", "PLACE", ["Ida"], "", "the mountain above Troy; Zeus watches the battle from it"),
    E("Argos", "PLACE", ["Argos"], "", "Agamemnon's realm and, loosely, all Greece"),
    E("Phthia", "PLACE", ["Phthia"], "", "Achilles' homeland"),
    E("Mycenae", "PLACE", ["Mycenae"], "", "Agamemnon's city"),
    E("Pylos", "PLACE", ["Pylos"], "", "Nestor's kingdom"),
    E("Sparta", "PLACE", ["Sparta", "Lacedaemon"], "Lacedaemon", "Menelaus's city"),
    E("Crete", "PLACE", ["Crete"], "", "Idomeneus's island"),
    E("Lycia", "PLACE", ["Lycia"], "", "Sarpedon and Glaucus's homeland"),
    E("Thrace", "PLACE", ["Thrace"], "", "north of the Hellespont"),
    E("Thebe", "PLACE", ["Thebe"], "", "Eëtion's city under Placus, sacked by Achilles"),
    E("Thebes", "PLACE", ["Thebes"], "", "the Boeotian city of the earlier war (and Egyptian Thebes, 9.381)"),
    E("Lemnos", "PLACE", ["Lemnos"], "", "Hephaestus's landing-place; Thoas's island"),
    E("Scaean", "PLACE", ["Scaean", "Gates"], "the Scaean Gates",
      "Troy's main gate; the scene of Hector's farewell and death"),
    E("Lyrnessus", "PLACE", ["Lyrnessus"], "", "the town Achilles sacked, where he took Briseis"),
    E("Pergamos", "PLACE", ["Pergamos"], "", "Troy's citadel"),
    E("Chryse", "PLACE", ["Chryse"], "", "Chryses' town, where Chryseis is returned"),
    E("Hellespont", "PLACE", ["Hellespont"], "", "the strait beside the Achaean camp"),
    E("Calydon", "PLACE", ["Calydon"], "", "Meleager's city"),
    E("Percote", "PLACE", ["Percote"], "", "Trojan-allied town on the Hellespont"),
    E("Arisbe", "PLACE", ["Arisbe"], "", "Trojan-allied town"),
    E("Zeleia", "PLACE", ["Zeleia"], "", "Pandarus's town under Ida"),
    E("Abydos", "PLACE", ["Abydos"], "", "town on the Hellespont"),
    E("Imbros", "PLACE", ["Imbros"], "", "island off Troy"),
    E("Samos", "PLACE", ["Samos"], "", "Samothrace, from which Poseidon watches (13.12)"),
    E("Rhodes", "PLACE", ["Rhodes"], "", "Tlepolemus's island"),
    E("Phrygia", "PLACE", ["Phrygia"], "", "Trojan-allied land; Hecuba's connection"),
    E("Maeonia", "PLACE", ["Maeonia"], "", "Trojan-allied land in Asia Minor"),
    E("Dardania", "PLACE", ["Dardania"], "", "the Dardanians' territory near Troy"),
    E("Axius", "PLACE", ["Axius"], "", "Paeonian river, Asteropaeus's grandfather"),
    E("Alpheius", "PLACE", ["Alpheius"], "", "river of Elis"),
    E("Peneius", "PLACE", ["Peneius"], "", "Thessalian river"),
    E("Satnioeis", "PLACE", ["Satnioeis"], "", "river in the Troad"),
    E("Selleïs", "PLACE", ["Selleïs"], "", "river named in contingent formulas"),
    E("Placus", "PLACE", ["Placus"], "", "the mountain below which Thebe stood"),
    E("Pleuron", "PLACE", ["Pleuron"], "", "Aetolian city"),
    E("Opoeis", "PLACE", ["Opoeis"], "", "Patroclus's birthplace in Locris"),
    E("Cos", "PLACE", ["Cos"], "", "island, in the Heracles back-story"),
    E("Gargaron", "PLACE", ["Gargaron"], "", "the peak of Ida where Zeus sits"),
    E("Pedasus", "PLACE", ["Pedasus"], "",
      "Altes' town on the Satnioeis; also the name of Achilles' mortal trace-horse (16.152)"),

    # ==================== ANIMALS, OBJECTS & THE SKY =======================
    E("Xanthus_horse", "OTHER", ["Balius", "Xanthus"], "Xanthus and Balius",
      "Achilles' immortal horses, sired by the West Wind on the harpy Podarge; Xanthus speaks "
      "and is silenced by the Erinyes (19.404-424). The shared token 'Xanthus' is claimed here "
      "rather than by the river, because the horse is the only one of its four referents that "
      "is a character. NB the count therefore includes the river's and the Lycian river's hits; "
      "the writer must cite only 16.149 and 19.400ff. See canon.md's homonym register"),
    E("Aethe", "OTHER", ["Aethe"], "", "Agamemnon's mare, lent to Menelaus for the Book 23 race"),
    E("Podargus", "OTHER", ["Podargus"], "",
      "Menelaus's horse (23.295); also the name of one of Hector's horses (8.185)"),
    E("Arion", "OTHER", ["Arion"], "", "Adrastus's divine horse, named at 23.346"),
]

# Scaffolding rows that exist only to hold a shape; dropped before building.
DROP = {"Bellerophon_placeholder", "Automedon_dup"}


def load_occ():
    if not OCC.exists():
        sys.exit(f"{OCC} not found — run tools/build_index.py first")
    return json.loads(OCC.read_text(encoding="utf-8"))


def load_stop():
    """The Phase 1 stoplist, imported so the two tools cannot drift apart."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "bi", Path(__file__).with_name("build_index.py"))
    bi = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bi)
    return bi.STOP


def check_stop_collisions(stop):
    """Every registry token must be absent from the Phase 1 stoplist.

    A token that is both classified and stoplisted is invisible: build_index.py
    drops it before it can reach occurrences.json, so its headword silently loses
    those hits — or, if the headword has no other token, disappears from the index
    while still looking present in REGISTRY. The stoplist is long and grew in
    several passes, so this is a real hazard rather than a theoretical one; it is
    checked on every build and treated as fatal.
    """
    bad = []
    for e in REGISTRY:
        if e["headword"] in DROP:
            continue
        for t in e["tokens"]:
            if t in stop:
                bad.append((e["headword"], t))
    return bad


def fmt_books(books):
    """Compress a sorted book list into ranges: [1,2,3,5] -> '1-3, 5'."""
    if not books:
        return ""
    parts, start, prev = [], books[0], books[0]
    for b in books[1:]:
        if b == prev + 1:
            prev = b
            continue
        parts.append(f"{start}-{prev}" if start != prev else f"{start}")
        start = prev = b
    parts.append(f"{start}-{prev}" if start != prev else f"{start}")
    return ", ".join(parts)


def build():
    occ = load_occ()
    used = set()
    dup = defaultdict(list)
    missing = []
    rows = []

    entries = [e for e in REGISTRY if e["headword"] not in DROP]

    def refkey(ref):
        b, l = ref.split(".")
        return (int(b), int(l))

    for e in entries:
        count, books, refs = 0, set(), set()
        for t in e["tokens"]:
            if t in occ:
                count += occ[t]["count"]
                books |= set(occ[t]["books"])
                refs |= set(occ[t]["refs"])
                dup[t].append(e["headword"])
                used.add(t)
            else:
                missing.append((e["headword"], t))
        e["_count"] = count
        e["_books"] = sorted(books)
        e["_refs"] = sorted(refs, key=refkey)
        rows.append(e)

    # Unclassified = every occurrence token not claimed, minus the stoplist noise.
    stop = load_stop()
    unclassified = sorted(((occ[t]["count"], t) for t in occ
                           if t not in used and t not in stop), reverse=True)

    collisions = {t: hs for t, hs in dup.items() if len(hs) > 1}
    stopped = check_stop_collisions(stop)
    return rows, unclassified, collisions, missing, stopped


def write_md(rows):
    order = ["MORTAL", "GOD", "PEOPLE", "PLACE", "OTHER"]
    titles = {
        "MORTAL": "Mortals", "GOD": "Gods & divine beings",
        "PEOPLE": "Peoples & groups", "PLACE": "Places",
        "OTHER": "Animals, objects & the sky",
    }
    by_cat = defaultdict(list)
    for r in rows:
        by_cat[r["cat"]].append(r)

    out = ["# Name index — master registry (Phase 2)\n"]
    out.append(
        "Every classified proper name in the poem, canonicalized. Generated by "
        "`tools/build_registry.py` from a curated classification joined against "
        "`index/occurrences.json`; hit-counts and book coverage are computed, so this "
        "stays true to the text if a line is ever revised. Aliases and same-name "
        "collisions are resolved here and in `canon.md`. This is the work list Phase 3 "
        "draws from — one entry per headword.\n"
    )
    out.append(f"**{len(rows)} headwords.** Categories: "
               + ", ".join(f"{titles[c]} ({len(by_cat[c])})" for c in order) + ".\n")

    for c in order:
        items = sorted(by_cat[c], key=lambda r: (-r["_count"], r["headword"]))
        out.append(f"\n## {titles[c]}\n")
        out.append("| Headword | Hits | Books | Aliases / epithets | Note |")
        out.append("| --- | ---: | --- | --- | --- |")
        for r in items:
            out.append(f"| **{r['headword']}** | {r['_count']} | {fmt_books(r['_books'])} "
                       f"| {r['aliases']} | {r['note']} |")
    return "\n".join(out) + "\n"


def write_registry_json(rows):
    """Machine-readable registry with citations joined in — the source the Phase 3
    slicer turns into per-writer work packets."""
    data = [
        {
            "headword": r["headword"],
            "cat": r["cat"],
            "aliases": r["aliases"],
            "note": r["note"],
            "count": r["_count"],
            "books": r["_books"],
            "refs": r["_refs"],
        }
        for r in sorted(rows, key=lambda r: r["headword"].lower())
    ]
    (ROOT / "index" / "registry.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--todo", type=int, default=10,
                    help="list unclassified tokens with >= this many hits (default 10)")
    args = ap.parse_args(argv)

    rows, unclassified, collisions, missing, stopped = build()

    # Fatal, and checked before anything is written: a stoplisted registry token
    # would silently drop hits (or a whole headword) from the finished index.
    if stopped:
        print(f"[FATAL] {len(stopped)} registry token(s) are in the build_index.py "
              f"stoplist and can never reach the index:")
        for hw, t in stopped:
            print(f"    {hw}: token {t!r} is in STOP")
        print("\nRemove the word from STOP, or drop the token from REGISTRY. "
              "Nothing was written.")
        return 2

    OUT.write_text(write_md(rows), encoding="utf-8")
    write_registry_json(rows)

    print(f"wrote {OUT} and index/registry.json — {len(rows)} headwords")
    print(f"stoplist guard: OK (no registry token is stoplisted)")
    if missing:
        print(f"\n[!] {len(missing)} tokens in REGISTRY not found in occurrences.json:")
        for hw, t in missing:
            print(f"    {hw}: {t!r}")
    if collisions:
        print(f"\n[!] {len(collisions)} tokens claimed by >1 headword:")
        for t, hs in collisions.items():
            print(f"    {t!r}: {hs}")

    print(f"\ncoverage: {len(unclassified)} candidate tokens still unclassified")
    for th in (20, 10, 5, 3, 2, 1):
        print(f"    with >={th:>2} hits: {sum(1 for c, _ in unclassified if c >= th)}")
    shown = [(c, t) for c, t in unclassified if c >= args.todo]
    if shown:
        print(f"\nnext up — {len(shown)} unclassified with >={args.todo} hits:")
        print("  " + ", ".join(f"{t} ({c})" for c, t in shown))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
