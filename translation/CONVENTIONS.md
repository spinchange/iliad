# Translation Conventions and Formula Register

The authoritative register of fixed renderings and translation policy for
this Iliad. Decisions here are binding for later books unless explicitly
revisited. Started with Book 1; restructured (2026-07-22) on the model of
the Odyssey project's FORMULAS.md.

## Principles

1. **The committed text is the source of truth.** This file must agree with
   the translated books; when in doubt, grep `translation/book_*.txt`.
   Update this register whenever a new formula is fixed, with a first-use
   reference (book.line of this translation = the Greek's line numbers).
2. **A formula, once fixed, recurs identically.** Epithets are never varied
   away for elegance. Homer's repetition is structural; the English repeats
   it verbatim, adjusting only grammatical person and inflection
   ("answered him/her").
3. **Whole-passage repetition is verbatim.** When the Greek repeats a block
   (messenger speeches, retellings, type-scenes), the English repeats its
   own earlier block word for word.
4. **Distinct Greek gets distinct English by default.** Deliberate merges
   are allowed but must be documented (current list: πόδας ὠκύς = ποδάρκης
   "swift-footed"; θεοειδής = θεοείκελος "godlike").
5. **Mechanical conformance is checked by tooling** — `python
   tools/check_formulas.py` verifies high-value formulas against the Greek.
   Add a check when fixing a formula that recurs often.

## General stance (set in Book 1)

- **Form**: plain, dignified modern English free verse, line-for-line with
  the Greek (one English line per Greek line). Target a loose five-to-six
  beat line. Books 1-4 predate the stated target but were measured
  (2026-07-23) as already conforming: median 13 syllables, 92-95% of lines
  in the 9-16 syllable band — statistically identical to the Odyssey
  project's calibration books. No retrofit needed; hold this distribution
  from Book 5 on. No meter, no rhyme.
- **Line numbers**: every translated line carries its Greek line number.
  Notes cite (book.line).
- **Epigraph**: each book opens with a one-sentence summary line.
- **Text followed**: the printed Monro-Allen text as given in `books/`,
  including athetized passages (atheteses recorded in footnotes, never
  acted on). Where the printed text goes against the manuscript vulgate
  (e.g. 1.350 "boundless" vs. "wine-dark"), translate as printed and
  footnote.
- **Footnote markers**: bracketed integers `[1]`, `[2]`… restarting at 1
  per book; each note opens with its (book.line) reference. Formulas are
  footnoted at first occurrence in the whole project only.

## Terms for the enslaved and the household (adopted from the Odyssey register)

- δμώς / δμῳή → **"slave" / "slave-woman"** — never "servant" or "maid."
  First use 6.323 (Helen's household), 6.375-376 (Hector's); checked
  mechanically by tools/check_formulas.py.
- ἀμφίπολος → "handmaid" (3.143 "two handmaids"); plural attendance
  phrases → "attendant women" as needed.
- ταμίη → "housekeeper" (6.381); τιθήνη → "nurse" (6.389).
- θεράπων → "aide" (4.227) or "henchman" (1.321, of heralds); in the
  formula θεράποντες Ἄρηος → "squires of Ares" (2.110).

## Thematic vocabulary (keep rigid)

| Greek | English | First | Notes |
|---|---|---|---|
| μῆνις | wrath | 1.1 | theme word; never "rage/anger" |
| τιμή | honor | 1.159 | |
| γέρας | prize | 1.118 | the awarded object embodying honor |
| ἄτη | blindness (ruin) | 1.412 | god-sent delusion; thread runs 1.412 → 2.111 → Book 19 |
| ἀτιμάζειν etc. | dishonor | 1.11 | |
| ἄποινα | ransom | 1.13 | |
| κλέος | fame / the report | 2.325 / 2.486 | "fame" when won and lasting; "the report" for hearsay |
| μῆτις | counsel / cunning | 2.169 | in epithets: "the equal of Zeus in counsel" |
| ἀτασθαλίαι | recklessness | 4.409 | |
| θέμιστες | the ordinances | 1.238 | |
| ξεινοδόκος / ξεῖνος | host / guest(-friend), stranger | 3.354 | xenia vocabulary kept visible |

## Epithets and names

### People and gods
| Greek | English | First |
|---|---|---|
| πόδας ὠκύς / ποδάρκης (Achilles) | swift-footed | 1.58 / 1.121 |
| δῖος | brilliant | 1.7 |
| ἄναξ ἀνδρῶν (Agamemnon) | lord of men | 1.7 |
| εὐρὺ κρείων | wide-ruling | 1.102 |
| κρείων | the lord | 1.130 |
| θεοείκελος / θεοειδής | godlike | 1.131 / 3.16 |
| διογενής | Zeus-sprung | 1.337 |
| πολύμητις (Odysseus) | resourceful | 1.311 |
| πολυμήχανος (Odysseus) | of many devices | 2.173 |
| Διὶ μῆτιν ἀτάλαντος (Odysseus) | the equal of Zeus in counsel | 2.169 |
| πτολίπορθος | sacker of cities | 2.278 |
| καλλιπάρῃος | fair-cheeked | 1.143 |
| λευκώλενος (Hera) | white-armed | 1.55 |
| βοῶπις πότνια Ἥρη | ox-eyed lady Hera | 1.551 |
| γλαυκῶπις (Athena) | grey-eyed; standalone substantive (Zeus's familiar use): "grey-eyes" | 1.206 / 8.373 |
| Παλλάς | Pallas (kept) | 1.200 |
| ἀγελείη (Athena) | the driver of the spoil | 4.128 |
| Ἀτρυτώνη (Athena) | Unwearied one | 2.157 |
| Τριτογένεια (Athena) | Tritogeneia (kept) | 4.515 |
| αἰγίοχος (Zeus) | aegis-bearing | 1.202 |
| νεφεληγερέτα (Zeus) | Zeus the cloud-gatherer | 1.511 |
| μητίετα (Zeus) | Zeus the counselor / of the counsels | 1.175 |
| τερπικέραυνος | who delights in thunder | 1.419 |
| ἀστεροπητής | lord of lightning | 1.580 |
| ὑψιβρεμέτης | who thunders on high | 1.354 |
| ὑψίζυγος | high-throned | 4.166 |
| εὐρύοπα | wide-seeing | 1.498 |
| Κρονίδης / Κρονίων | son of Cronos | 1.397 |
| ἀγκυλομήτεω Κρόνου | crooked-counseled Cronos | 2.205 |
| πατὴρ ἀνδρῶν τε θεῶν τε | father of men and gods | 1.544 |
| ταμίης πολέμοιο (Zeus) | the dispenser of war | 4.84 |
| ἀργυρόπεζα (Thetis) | silver-footed | 1.538 |
| ἅλιος γέρων | the old man of the sea (= Nereus, never named) | 1.538 |
| ἠΰκομος | lovely-haired | 1.36 |
| ἑκηβόλος / ἑκατηβόλος / ἑκατηβελέτης (Apollo) | who strikes from afar; standalone substantive: the far-striker | 1.14 / 1.96 |
| ἕκατος | the far-striker | 1.385 |
| ἑκάεργος | the worker-from-afar | 1.147 |
| ἀργυρότοξος | god of the silver bow / of the silver bow | 1.37 |
| Λυκηγενής (Apollo) | the Lycian-born | 4.101 |
| κλυτότοξος | famed for the bow | 4.101 |
| Φοῖβος | Phoebus (kept) | 1.43 |
| Σμινθεύς | Smintheus (kept, cult title) | 1.39 |
| κλυτοτέχνης (Hephaestus) | famed for craft | 1.571 |
| ἀμφιγυήεις (Hephaestus) | crook-footed | 1.607 |
| περικλυτός | famed | 1.607 |
| ῥοδοδάκτυλος Ἠώς | rosy-fingered Dawn | 1.477 |
| ἠριγένεια | early-born | 1.477 |
| χρυσόθρονος | of the golden throne | 1.611 |
| φιλομειδὴς Ἀφροδίτη | laughter-loving Aphrodite | 3.424 |
| ἀργεϊφόντης (Hermes) | the slayer of Argus | 2.103 |
| διάκτορος (Hermes) | the guide | 2.103 |
| ποδήνεμος ὠκέα Ἶρις | wind-footed swift Iris | 2.786 |
| πόδας ὠκέα Ἶρις | swift-footed Iris | 2.790 |
| πότνια Ἥβη | the lady Hebe | 4.2 |
| Δεῖμος / Φόβος / Ἔρις | Terror / Panic / Strife (personified, capitalized) | 4.440 |
| κορυθαίολος Ἕκτωρ | Hector of the flashing helmet | 2.816 |
| φαίδιμος Ἕκτωρ | glorious Hector | 4.505 |
| ἀνδροφόνος (Hector) | man-slaughtering | 1.242 |
| ἀρηΐφιλος (Menelaus) | dear to Ares | 3.21 |
| ξανθός (Menelaus; of hair) | tawny-haired / tawny | 3.284 / 1.197 |
| βοὴν ἀγαθός (Menelaus, Diomedes) | good at the war-cry | 2.408 / 2.563 |
| Γερήνιος ἱππότα Νέστωρ | the Gerenian horseman Nestor | 2.336 |
| ἱππόδαμος | breaker of horses (individual); horse-taming (Trojans) | 2.23 / 2.230 |
| ἱπποκορυσταί | men who fight from chariots | 2.1 |
| δουρὶ κλυτός | famed with the spear | 2.645 |
| μενεπτόλεμος | steadfast in battle | 2.740 |
| δαΐφρων | war-minded | 2.23 |
| ὑπέρθυμος | high-hearted | 4.365 |
| κυδάλιμος | glorious | 4.100 |
| λινοθώρηξ | in/of the linen corslet | 2.529 |
| βίη Ἡρακληείη (etc.) | the might of Heracles (periphrasis, keep) | 2.658 |
| ποιμὴν λαῶν | shepherd of the people | 1.263 |
| ὄζος Ἄρηος | scion of Ares | 2.540 |
| θεράποντες Ἄρηος | squires of Ares | 2.110 |
| ἀτάλαντος Ἄρηϊ / Ἐνυαλίῳ | the equal of Ares / of Enyalius | 2.627 / 2.651 |
| ἡγήτορες ἠδὲ μέδοντες | leaders and lords | 2.79 |
| κοσμήτορε λαῶν | marshals of the people | 1.16 |
| μερόπων ἀνθρώπων | mortal men (sg. as sense requires) | 1.250 |
| κάρη κομόωντες Ἀχαιοί | long-haired Achaeans | 2.11 |
| ἐϋκνήμιδες Ἀχαιοί | strong-greaved Achaeans | 1.17 |
| χαλκοχίτωνες Ἀχαιοί | bronze-shirted Achaeans | 1.371 |
| ἑλίκωπες / ἑλικῶπις | bright-eyed | 1.98 |
| ταχύπωλοι Δαναοί | Danaans of swift colts | 4.232 |
| ἐΰζωνος | fair-belted | 1.429 |
| τανύπεπλος | of the trailing robe | 3.228 |
| δῖα γυναικῶν | brilliant among women | 2.714 |
| ἰσόθεος φώς | a man like a god | 3.310 |
| ἀντιάνειραι (Amazons) | the match of men | 3.189 |
| ἕρκος Ἀχαιῶν (Ajax) | wall of the Achaeans | 3.229 |
| ἐϋμμελίω (Priam) | of the good ash spear | 4.47 |
| διοτρεφής | Zeus-nurtured | 1.176 |
| βροτολοιγός (Ares) | bane of mortals | 5.31 |
| μιαιφόνος (Ares) | blood-stained | 5.31 |
| τειχεσιπλήτης (Ares) | stormer of walls | 5.31 |
| θοῦρος (Ares) | rushing | 5.30 |
| χάλκεος Ἄρης | brazen Ares | 5.704 |
| ὄβριμος (Ares) | massive | 5.845 |
| ἆτος πολέμοιο (Ares) | insatiate of war | 5.388 |
| ἀλλοπρόσαλλος (Ares) | turncoat | 5.831 |
| Κύπρις (Aphrodite, Book 5 only) | Cypris (kept) | 5.330 |
| Ἐνυώ | Enyo ("sacker of cities" 5.333; "the lady Enyo" 5.592) | 5.333 |
| Κυδοιμός | Tumult (personified) | 5.593 |
| Παιήων | Paiëon (the gods' healer; distinct from Apollo) | 5.401 |
| Ὧραι | the Seasons | 5.749 |
| Διώνη | Dione | 5.370 |
| ἰοχέαιρα (Artemis) | who showers arrows | 5.53 |
| χρυσάορος (Apollo) | of the golden sword | 5.509 |
| Ἀϊδωνεύς | Aïdoneus (kept) | 5.190 |
| κλυτόπωλος (Hades) | of the famed colts | 5.654 |
| πρέσβα θεά (Hera) | eldest goddess | 5.721 |
| ὀβριμοπάτρη (Athena) | she of the mighty father | 5.747 |
| Ἄϊδος κυνέη | the helmet of Hades | 5.845 |
| ἰχώρ | ichor | 5.340 |
| εἴδωλον | phantom | 5.449 |
| ἑλκεσίπεπλος (Trojan women) | with (their) trailing gowns | 6.442 |
| ἐϋπλόκαμος | lovely-braided | 6.380 |
| χρυσήνιος (Artemis) | of the golden reins | 6.205 |
| ἐρυσίπτολις (Athena) | guardian of the city | 6.305 |
| ἠπιόδωρος (Hecuba) | gentle-giving | 6.251 |
| πολύδωρος (wife) | richly dowered | 6.394 |
| χαλκοκορυστής | of the bronze helmet | 6.199 |
| ἠθεῖος (address to elder brother) | Elder brother | 6.518 |
| ἐνοσίχθων / ἐννοσίγαιος (Poseidon) | the earth-shaker | 7.445 / 7.455 |
| εὐρυσθενής (Poseidon) | wide-ruling | 7.455 |
| ἐρίγδουπος πόσις Ἥρης (Zeus) | the loud-thunderer, Hera's lord | 7.411 |
| ἠπύτα κῆρυξ | the far-calling herald | 7.384 |
| χαλκοκνήμιδες (hapax) | bronze-greaved | 7.41 |
| θεόφιν μήστωρ ἀτάλαντος (Priam) | the equal of the gods in counsel | 7.366 |
| ῥηξήνωρ (Achilles) | breaker of men | 7.228 |
| θυμολέων (Achilles, Heracles) | the lion-heart(ed) | 7.228 / 5.639 |
| χλωρὸν δέος | green fear | 7.479 |
| κροκόπεπλος Ἠώς | Dawn in her saffron robe | 8.1 |
| ἐΰθρονος Ἠώς | fair-throned Dawn | 8.565 |
| πολύτλας δῖος Ὀδυσσεύς | much-enduring brilliant Odysseus | 8.97 |
| χρυσόπτερος (Iris) | of the golden wings | 8.398 |
| ἀελλόπος (Iris) | storm-footed | 8.409 |
| Γερήνιος οὖρος Ἀχαιῶν (Nestor) | the Gerenian, warden of the Achaeans | 8.80 |
| πολυπίδαξ Ἴδη, μήτηρ θηρῶν | Ida of the many springs, mother of wild things | 8.47 |
| Πανομφαῖος (Zeus) | Zeus of All Voices | 8.250 |
| πυλάρτης (Hades) | the gate-closer | 8.367 |
| τανηλεγὴς θάνατος | death that lays men low | 8.70 |
| ἀπτοεπές (address) | reckless of tongue | 8.209 |
| ἄττα (address to aged guardian) | old father | 9.607 |
| πολύαινος (Odysseus) | of the many tales | 9.673 |
| γαιήοχος (Poseidon) | the holder of the earth | 9.183 |
| Λιταί | the Prayers (personified; with Ἄτη "Blindness") | 9.502 |
| Φύζα | Panic (personified) | 9.2 |
| κλέος ἄφθιτον | imperishable fame | 9.413 |
| ἄλοχος θυμαρής | bed-dear wife | 9.336 |
| μύθων τε ῥητῆρα πρηκτῆρά τε ἔργων | a speaker of words, and a doer of deeds | 9.443 |
| τλήμων (Odysseus) | hardy | 10.231 |
| ἄλκιμος | stout (spear, man) | 3.338 / 10.110 |
| ἀγήνωρ | proud (θυμὸς ἀγήνωρ = proud spirit) | 10.220 |
| ἀγαυός | illustrious | 10.392 |
| ποδώκης | swift-footed (= πόδας ὠκύς merge; of Dolon 10.316) | 2.860 |
| Ἀθηναίη ληῖτις | Athena of the Spoils (only 10.460) | 10.460 |
| ἀλαοσκοπιὴν εἶχε | kept no blind man's watch | 10.515 |
| μενεπτόλεμος Θρασυμήδης | Thrasymedes, steadfast in battle | 10.255 |
| μενεχάρμης | staunch in the fight | 11.122 |
| ταλασίφρων (Odysseus) | patient-hearted | 11.466 |
| ποικιλομήτης (Odysseus) | of the subtle wiles | 11.482 |
| πλήξιππος | lasher of horses | 11.93 |
| Εἰλείθυιαι μογοστόκοι | the Eileithyiai of hard labor | 11.270 |
| Γοργώ | the Gorgon | 11.36 |
| κύανος | (dark) blue enamel | 11.24 |
| νυκτὸς ἀμολγῷ | in the milking-dark of night | 11.173 |
| νηλεὲς ἦμαρ | the pitiless day | 11.484 |
| χάλκεον ὕπνον | a sleep of bronze | 11.241 |
| κυκειών | posset | 11.624 |
| μήστωρ φόβοιο | machine(s) of rout | 5.272 / 6.97 / 6.278 / 8.108 / 12.39 / 23.16 (6/8/23 harmonized in audit, 2026-07-26) |
| ἡμιθέων γένος ἀνδρῶν | the race of half-god men (12.23 only) | 12.23 |
| ἀκόρητος πολέμου | never sated with war | 12.335 |
| νυκτὶ θοῇ ἀτάλαντος | the very likeness of swift night | 12.463 |
| ὀλέθρου πείρατα ἐφῆπται | the cables of destruction are fastened | 7.402 / 12.79 |
| νήπιος/νήπιοι (narrator's) | the fool / the fools | 2.38 / 12.113 |
| εἷς οἰωνὸς ἄριστος ἀμύνεσθαι περὶ πάτρης | One bird-sign is best: to fight for your fatherland. | 12.243 |
| μήστωρες ἀϋτῆς | masters of the war-shout | 13.93 |
| ἀρίγνωτοι δὲ θεοί περ | the gods are easy to know | 13.72 |
| ἀκεσταί τοι φρένες ἐσθλῶν | The minds of good men can be healed. | 13.115 |
| ὀαριστύς (of battle) | trysting-place (front-fighters') | 13.291 |
| Ζεὺς ξείνιος | Zeus of Guest-right | 13.625 |
| χρόα λειριόεντα | lily-soft skin | 13.830 |
| βουγάϊος | blundering ox of a braggart | 13.824 |
| κυανοχαίτης (Poseidon) | blue-maned | 13.563 |
| θυμοραϊστής (θάνατος) | (death) that breaks the spirit | 13.544 |
| Ὕπνος / Θάνατος | Sleep, the brother of Death | 14.231 |
| Νὺξ δμήτειρα θεῶν καὶ ἀνδρῶν | Night, subduer of gods and men | 14.259 |
| κεστὸς ἱμάς | the pierced, embroidered band (the kestos) | 14.214 |
| Ὠκεανὸς θεῶν γένεσις / μήτηρ Τηθύς | Oceanus, the begetting of the gods / mother Tethys | 14.201 |
| Τιτῆνες ὑποταρτάριοι | the gods under Tartarus, who are called the Titans | 14.279 |
| χαλκίς / κύμινδις | the bird the gods call chalkis, and men kymindis | 14.291 |
| ἀνδράγρια | the bloody spoils of men (hapax) | 14.509 |
| Πασιθέη | Pasithea (one of the younger Graces) | 14.276 |
| στρεπταὶ μέν τε φρένες ἐσθλῶν | The hearts of the great can turn. | 15.203 |
| Ἐρινύες (πρεσβυτέροισιν) | the Erinyes (side with the elder-born) | 15.204 |
| ξυστὸν ναύμαχον | pike for sea-fighting (naval pike) | 15.388 / 15.677 |
| θρῆνυς ἑπταπόδης | the seven-foot bridge-plank | 15.729 |
| τὼ ἐν χερσὶ φόως | Our light of safety is in our hands | 15.741 |
| ἐγέλασσε χείλεσιν... | she laughed with her lips; but the forehead... did not warm | 15.101-103 |
| αἰναρέτης | cursed in your valor | 16.31 |
| μέγα νήπιος | the great fool | 16.46 |
| Πηλιάς μελίη | the Pelian ash (Chiron's spear, "death for heroes") | 16.143 |
| Σελλοί | the Selloi, interpreters, of unwashed feet, who sleep on the ground | 16.234-235 |
| τὸ γὰρ γέρας ἐστὶ θανόντων | for that is the honor-right of the dead | 16.457 / 16.675 |
| Ὕπνος καὶ Θάνατος διδυμάονε | the twin brothers Sleep and Death | 16.672 / 16.682 |
| κεῖτο μέγας μεγαλωστί | lay mighty in his mightiness (his horsemanship all forgotten) | 16.776 |
| δαίμονι ἶσος | like more than man | 5.438 / 16.705, 786 |
| ψυχὴ δʼ ἐκ ῥεθέων πταμένη... (soul-flight couplet) | his soul, flying from his limbs, went down to the house of Hades, / wailing its fate, leaving its manhood and its youth | 16.856-857 = 22.362-363 (reuse verbatim) |
| ἐν χερσὶ τέλος πολέμου, ἐπέων δʼ ἐνὶ βουλῇ | In hands lies the outcome of war; of words, in council | 16.630 |
| ῥεχθὲν δέ τε νήπιος ἔγνω | When the thing is done, even the fool learns. | 17.32 |
| θεῶν ἐν γούνασι κεῖται | these things lie on the knees of the gods | 17.514; also 20.435 |
| οὐ κατὰ κόσμον | not by right | 17.205 |
| ἐν δὲ φάει καὶ ὄλεσσον | and in the light — kill us | 17.647 |
| θρέπτρα | the price of his rearing | 17.302 (cf. 4.478) |
| μαλθακὸς αἰχμητής | a soft spearman | 17.588 |
| εἰλαπιναστής | companion at the feast | 17.577 |
| ἀτρύγετος (of αἰθήρ) | barren (air) — sea formula lent to the ether | 17.425 |
| οὐ μὲν γάρ τί πού ἐστιν ὀϊζυρώτερον ἀνδρός... | there is nothing anywhere more pitiful than man, / of all things that breathe and creep upon the earth | 17.446-447 |

### Things, places, seascape
| Greek | English | First |
|---|---|---|
| πολυφλοίσβοιο θαλάσσης | loud-roaring sea | 1.34 |
| ἁλὸς ἀτρυγέτοιο | barren sea | 1.316 |
| οἴνοπα πόντον | wine-dark sea (where printed; 1.350 prints "boundless") | 2.613 |
| πολιῆς ἁλός | grey sea / grey salt water | 1.350 |
| ὑγρὰ κέλευθα | the watery ways | 1.312 |
| εὐρέα νῶτα θαλάσσης | the broad back of the sea | 2.159 |
| θῖνʼ ἁλός / παρὰ θῖνα | the shore / surf-line of the sea | 1.34 |
| θοαὶ νῆες | swift ships | 1.12 |
| νῆες ἐΐσαι | balanced ships | 1.306 |
| κορωνίσιν νηυσί | beaked ships | 1.170 |
| ὠκύποροι νῆες | swift-faring ships | 1.421 |
| κοίλῃσι νηυσί | hollow ships | 1.26 |
| νηῒ μελαίνῃ | black ship | 1.141 |
| πολυκλήϊσι | many-benched | 2.74 |
| ἐϋσσέλμοιο | well-benched | 2.170 |
| μιλτοπάρῃοι | with cheeks of vermilion | 2.637 |
| ἑκατόμβη | hecatomb | 1.65 |
| κλισίη | hut (never "tent") | 1.185 |
| δολιχόσκιον ἔγχος | long-shadowed spear | 3.346 |
| νηλέϊ χαλκῷ | the pitiless bronze | 3.292 |
| πάντοσε ἴση (shield) | balanced every way | 3.347 |
| κῆρα μέλαιναν | black doom | 3.360 |
| χθὼν πουλυβότειρα | the earth that feeds so many | 3.89 |
| φυσίζοος αἶα | the life-giving earth | 3.243 |
| ζείδωρος ἄρουρα | the grain-giving earth | 2.548 |
| Ὄλυμπος ἀγάννιφος / αἰγλήεις | snow-capped / shining Olympus | 1.420 / 1.532 |
| Ἴλιος ἱρή | holy Ilion | 4.46 |
| ἕρκος ὀδόντων | the fence of (your) teeth | 4.350 |
| νήδυμος ὕπνος | sweet sleep | 2.2 |
| μελίφρων ὕπνος | honey-hearted sleep | 2.34 |
| οὖλος ὄνειρος | baneful Dream (capitalized as person) | 2.6 |
| φλὸξ Ἡφαίστοιο | the flame of Hephaestus (metonymy, keep) | 2.426 |

## Speech-introduction formulas (fixed whole lines; person-slots adapt)

| Greek cue | English | First |
|---|---|---|
| τὸν/τὴν δʼ ἀπαμειβόμενος προσέφη [name] | Answering him/her spoke [name]: | 1.84 |
| τὸν/τὴν δʼ ἠμείβετʼ ἔπειτα [name] | Then answered him/her [name] / Then [name] answered him/her: | 1.121 |
| τὸν/τὴν δʼ αὖτε προσέειπε [name] | Then [name] answered him/her: | 1.206 |
| τὸν δʼ ἄρʼ ὑπόδρα ἰδὼν προσέφη [name] | Glaring at him darkly, [name] spoke/answered: | 1.148 |
| ὅ σφιν ἐὺ φρονέων ἀγορήσατο καὶ μετέειπεν | With good will toward them he spoke and addressed them: | 1.73 |
| καί μιν φωνήσας ἔπεα πτερόεντα προσηύδα | and speaking winged words he/she addressed him/her: | 1.201 |
| ἀγχοῦ δʼ ἱσταμένη/-ος … προσηύδα | Standing close, [name] spoke … | 2.172 |
| ἔπος τʼ ἔφατʼ ἔκ τʼ ὀνόμαζε | and spoke a word, and named him/her: | 1.361 |
| τοῖσι δʼ ἀνιστάμενος μετέφη [name] | [name] rose and spoke among them: | 1.58 |
| τοῖσι δὲ καὶ μετέειπε [name] | And among them spoke [name]: | 2.336 |
| ὣς φάτο / ὣς ἔφατ(ο) | So he/she spoke, … | 1.33 |
| ἦ (ῥα) καί … | He/She spoke, and … | 1.219 |
| ἤτοι ὅ γʼ ὣς εἰπὼν κατʼ ἄρʼ ἕζετο· τοῖσι δʼ ἀνέστη | So he spoke and sat down; and among them rose | 1.68 |
| ὣς ἔφατʼ, οὐδʼ ἀπίθησε [name] | So he/she spoke, and [name] did not disobey | 2.166 |
| μειλιχίοισιν (ἐπέεσσιν) | with honeyed words | 4.256 |
| χολωτοῖσιν ἐπέεσσιν | with angry words | 4.241 |
| αἰσχροῖς ἐπέεσσιν / νείκεσσεν | with shaming words / raked him | 3.38 |
| κερτομίοισι (ἐπέεσσι) | with cutting/needling words | 1.539 / 4.6 |

## Vocative address formulas (fixed verbatim)

| Greek | English | First |
|---|---|---|
| διογενὲς Λαερτιάδη, πολυμήχανʼ Ὀδυσσεῦ | Zeus-sprung son of Laertes, Odysseus of many devices | 2.173 |
| Ἀτρεΐδη κύδιστε, ἄναξ ἀνδρῶν Ἀγάμεμνον | Most glorious son of Atreus, lord of men Agamemnon | 2.434 |
| ὦ φίλοι ἥρωες Δαναοὶ θεράποντες Ἄρηος | Friends, Danaan heroes, squires of Ares | 2.110 |
| Ζεῦ πάτερ Ἴδηθεν μεδέων κύδιστε μέγιστε | Father Zeus, ruling from Ida, most glorious, greatest | 3.276 |
| Ζεῦ κύδιστε μέγιστε κελαινεφές | Zeus most glorious, greatest, lord of the dark cloud | 2.412 |
| αἰνότατε Κρονίδη, ποῖον τὸν μῦθον ἔειπες | Most dread son of Cronos, what a word you have spoken! | 1.552 |
| δαιμονίη / δαιμόνιε | Strange one / Possessed one / Fool (context-graded; see 1.561, 4.31, 2.190, 2.200) | 1.561 |
| ὦ πόποι | Shame! / Well now! (indignant vs. amused; 1.254, 2.272) | 1.254 |
| ὦ γέρον | Old man, … | 4.313 |
| τέττα | Old friend (4.412 only) | 4.412 |
| κέκλυτέ μευ [group] | Hear (from) me, [group] … | 3.86 |

## Recurring whole lines and refrains (fixed verbatim)

| English (fixed) | First | Notes |
|---|---|---|
| and when early-born rosy-fingered Dawn appeared, | 1.477 | the dawn line |
| they feasted, and no heart lacked a fair share of the feast. | 1.468 | also 1.602, 2.431 |
| And when they had put away desire for eating and drinking, | 1.469 | feast close; also 2.432 |
| the young men filled the mixing-bowls brim-high with drink | 1.470 | |
| Sacrifice block: "they first drew back the victims' heads, cut their throats, and flayed them, / carved out the thigh-pieces and wrapped them in fat, / making a double fold, and laid raw flesh upon them" | 1.459-461 | = 2.422-424 verbatim; continuations follow the Greek where it diverges |
| When the thighs were burned and they had tasted the inner parts, / they cut up the rest and threaded it on spits, / roasted it with care, and drew it all off. | 1.464-466 | = 2.427-429 |
| bearing ransom past counting, | 1.13 | = 1.372 |
| but the two sons of Atreus most of all, marshals of the people | 1.16 | = 1.375 |
| Then all the other Achaeans shouted assent: / respect the priest, take the shining ransom. | 1.22-23 | = 1.376-377 |
| he sent him off harshly, and laid a hard command on him: | 1.25 | = 1.379; cf. 1.326 |
| he has taken and keeps his/my prize; he seized it himself. | 1.356 | also 1.507, 2.240 — the quarrel's refrain |
| loving both men alike in her heart, and caring for both. | 1.196 | = 1.209 |
| I tell you this outright, and it will be accomplished: | 1.212 | ὧδε γὰρ ἐξερέω…; cf. 2.257 |
| and let them drag / do not let them drag the balanced ships down to the sea | 2.165 | = 2.181 |
| the struggles and groans of Helen | 2.356 | = 2.590 |
| With him/them followed forty black ships. | 2.524 | catalogue refrain; variants per Greek |
| With them thirty hollow ships sailed in order. | 2.516 | catalogue refrain |
| he was broken under the hands of the swift-footed son of Aeacus / in the river | 2.860-861 | = 2.874-875 |
| death and doom (θάνατον καὶ πότμον) | 2.359 | πότμος = doom; μοῖρα = fate |
| Then let the wide earth gape for me. | 4.182 | recurs later (8.150) |
| glory for him, grief for us. | 4.197 | = 4.207 |
| over his eyes closed purple death, and fate the overpowering | 5.83 | grand death-formula |
| such as mortals are now | 5.304 | diminished-present motif; also 12.383, 12.449, 20.287 |
| Whom first, whom last did they strip of his arms …? | 5.703 | narrator's roll-call; also 8.273, 11.299, 16.692 |
| And when they were close, advancing on one another, | 3.15 | engagement line; 5.14, 5.630, 5.850 |
| like more than man (δαίμονι ἶσος) | 5.438 | the three-then-fourth pattern; recurs 16.705, 16.786 |
| and the two flew, nothing loath | 5.366 | divine horses; 5.768 |
| the day of freedom / the day of slavery | 6.455 / 6.463 | condition-as-date idiom |
| the stalled-horse simile (6.506-511) | 6.506 | = 15.263-268 verbatim; English fixed |
| the day will come when holy Ilion shall perish, / and Priam, and the people of Priam of the good ash spear | 4.164-165 | = 6.448-449; threat in Agamemnon's mouth, knowledge in Hector's |
| It is good to yield to night as well. | 7.282 | = 7.293 |
| Later we will fight again, until the god / decides between us, and hands victory to one side or the other. | 7.291-292 | = 7.377-378, 7.396-397 |
| so I may say what the heart in my chest commands me | 7.68 | = 7.349, 7.369 |
| out of the fury of war and the dread combat | 7.119 | = 7.174 |
| Women of Achaea, men of Achaea no longer | 2.235 | = 7.96 (Thersites' taunt in Menelaus's mouth) |
| and took the gift of sleep | 7.482 | book-close formula |
| he went into the middle and held back the Trojan lines, / gripping his spear by the middle; and they all sat down | 3.77-78 | = 7.55-56 |
| So long as it was morning, and the sacred day still growing, / so long the missiles of both sides struck home, and the people fell. | 8.66-67 | recurs 11.84-85 |
| So he spoke, and they murmured at it, Athena and Hera, / who sat side by side plotting evils for the Trojans. | 4.20-21 | = 8.457-458 (+ 4.22-24 = 8.459-461) |
| he held a spear eleven cubits long; and before him the bronze / point of the shaft shone, and a ring of gold ran round it | 6.318-320 | = 8.493-495 |
| And terrible grief closed over Hector's heart for his driver; / but he left him lying there, though grieving for his companion | 8.124-125 | = 8.316-317 |
| in a clear space, where ground showed empty of the dead | 8.491 | = 10.199 |
| my own heart and my proud spirit urge me | 10.220 | = 10.319 (Diomedes/Dolon twinned volunteer-speeches) |
| to go close to the swift-faring ships, and find out | 10.308 | = 10.320; ≈ 10.395 |
| whether the swift ships are guarded as before, / or whether by now, beaten down under our hands, / they are planning flight among themselves, and have no wish / to keep watch through the night, sodden with brutal weariness. | 10.309-312 | = 10.396-399 (Dolon relays Hector verbatim) |
| what they are counseling among themselves — whether they mean / to stay where they are by the ships, far away, or will withdraw / back to the city, since they have beaten down the Achaeans. | 10.208-210 | = 10.409-411 (Odysseus repeats Nestor) |
| taking counsel together, whether to run or fight | 10.147 | = 10.327 |
| But come, tell me this, and recount it truly: | 10.384 | = 10.405; Odyssean interrogation formula |
| Well then, I will recount (all) this (too) to you very truly. | 10.413 | = 10.427 |
| fiery, huge, reaching his feet; and he took up a spear. | 10.24 | = 10.178 (lion-skin line) |
| Come, tell me, Odysseus of the many tales, great glory of the Achaeans: | 9.673 | = 10.544 |
| Nestor, Neleus' son, great glory of the Achaeans | 10.87 | = 10.555 |
| through the ambrosial night | 10.41 | = 10.142; night-phrase register: δι' ὀρφναίην = "in/through the murky night" (10.83 = 10.386, 10.276), θοὴν διὰ νύκτα μέλαιναν = "through the swift black night" (10.394, 10.468), διὰ νύκτα μέλαιναν = "through the black night" (10.297) |
| Dawn rose from her bed beside illustrious Tithonus / to bring light to the immortals and to mortal men | 11.1-2 | = Od. 5.1-2 (cross-epic) |
| Troubled, he/she spoke to his/her own great-hearted spirit: | 11.403 | soliloquy frame; recurs 17.90, 18.5, 20.343, 21.53, 22.98 |
| But why does my own heart debate these things with me? | 11.407 | recurs 17.97, 21.562, 22.122, 22.385 |
| Dog! Again you have run out from under death — and yet the evil... (11.362-367, six lines) | 11.362 | = 20.449-454 (Achilles); reuse verbatim |
| He sprang into the chariot and told his charioteer / to drive to the hollow ships; for his heart was heavy. | 11.273-274 | = 11.399-400 |
| But he kept ranging down the ranks of the other men / with spear and sword and with great stones | 11.264-265 | = 11.540-541 |
| lie by the ships, hit from afar or stabbed close | 11.659 | = 11.826 |
| and the wound began to dry, and the blood stopped | 11.267 | = 11.848 (book's ring) |
| always to be the best, and to hold his head above all others | 6.208 | = 11.784 (Peleus's charge) |
| Trojans and Lycians and Dardanians who fight at close quarters — / be men, my friends; remember your rushing courage. | 8.173-174 | = 11.286-287; 13.150, 15.425, 15.486, 17.184 |
| Tell me now, Muses, who keep your homes on Olympus | 2.484 | = 11.218; 14.508, 16.112 |
| Whom first, whom last did he/they strip of his arms | 5.703 | = 8.273, 11.299, 16.692 |

## Ritual and formal language (set in Book 3)

- ὅρκια τάμνειν kept literal: "cut the (sworn) oaths" — from cutting the
  victims' throats; never softened to "swear a treaty." ὅρκια πιστά =
  "sworn oaths" / "oath-offerings" (when the physical victims are meant).
- Oath-witness invocation (3.276-280) and curse formula (3.298-301)
  rendered with deliberate stiffness — reuse this register for later
  truce/oath scenes.
- Prayer shape: invocation with cult titles → past services or grounds →
  request. Keep the three-step structure visible.
- Arming type-scene order (3.330-338): greaves → corslet → sword →
  shield → helmet → spear. Footnoted at first occurrence only; later
  arming scenes (Books 11, 16, 19) reuse the same English skeleton.

## Combat conventions (set in Book 4 — binding for all battle books)

Death formulas, fixed and never varied for elegance:
- τὸν δὲ σκότος ὄσσε κάλυψε → "darkness covered his eyes"
- δούπησεν δὲ πεσών, ἀράβησε δὲ τεύχεʼ ἐπʼ αὐτῷ → "he fell with a thud,
  and his armor clattered upon him"
- λῦσε δὲ γυῖα → "unstrung his limbs"
- τὸν μὲν λίπε θυμός / θυμὸν ἀποπνείων → "the spirit left him" /
  "gasping out his life"
- μοῖρα πέδησε → "fate shackled (him)"

Armor vocabulary:
- ζωστήρ = war-belt; ζῶμα = loin-guard; μίτρη = waist-guard;
  θώρηξ = corslet; κνημῖδες = greaves; κυνέη / κόρυς = helmet;
  σάκος / ἀσπίς = shield (ὀμφαλόεσσαι = "bossed"); φάλος = (helmet-)ridge.
- Wound anatomy kept clinically precise, as the Greek gives it.
- Weapons are bronze; note rare iron exceptions when they occur
  (4.123 arrowhead; iron otherwise = tools/wealth).
- πρόμαχοι = "the front-fighters."

## Paris / Alexandros (set in Book 3)

The poem uses both names, Ἀλέξανδρος predominating. Reproduce whichever
name the Greek has in each line; do not normalize. Δύσπαρι (3.39) =
"Paris — evil Paris."

## Catalogue style (set in Book 2, applies to any later list passages)

- One English line per Greek line, litany register preserved.
- Ship-count refrains rendered identically wherever the Greek is identical.
- Relative-clause chains kept as "they who dwelt in… / who held…" anaphora.
- Place-epithets always translated ("rocky Aulis," "Thisbe of the many
  doves," "hundred-citied Crete").

## Named-entity spellings

Familiar Latinized forms throughout: Achilles, Agamemnon, Menelaus, Ajax,
Odysseus, Patroclus, Nestor, Calchas, Chryses, Chryseis, Briseis (father:
Briseus), Clytemnestra, Hector, Priam, Peleus, Thetis, Zeus, Hera, Athena,
Apollo, Leto, Poseidon, Hephaestus, Peirithous, Dryas, Caeneus, Exadius,
Polyphemus, Theseus, Aegeus, Talthybius, Eurybates, Idomeneus, Eëtion
(keep diaeresis), Briareus / Aegaeon, Sintians.

Added in Book 2: Thersites, Telemachus, Hermes, Pelops, Atreus, Thyestes,
Iris, Aeneas, Anchises, Aphrodite, Sarpedon, Glaucus, Pandarus, Meriones,
Tlepolemus, Heracles, Nireus, Philoctetes, Protesilaus, Podarces, Eumelus,
Alcestis, Admetus, Machaon, Podaleirius, Eurypylus, Polypoetes, Leonteus,
Meges, Thoas, Menestheus, Diomedes, Sthenelus, Euryalus, Ascalaphus,
Ialmenus, Schedius, Epistrophus, Elephenor, Agapenor, Gouneus, Prothoos,
Thamyris, Eurytus, Meleager, Oeneus, Erechtheus, Polites, Aesyetes,
Asius, Hippothous, Acamas, Peiroos, Pyraechmes, Pylaemenes, Ennomus,
Phorcys, Ascanius, Mesthles, Antiphus, Nastes, Amphimachus, Typhoeus,
Myrine. "Adrastus" for the Sicyon king (2.572), "Adrestus" for the
Trojan-side leader (2.830). Contingent peoples: Boeotians, Phocians,
Locrians, Abantes, Epeians, Cephallenians, Aetolians, Cretans, Rhodians,
Myrmidons/Hellenes/Achaeans, Magnetes, Enienes, Peraebians; Trojan-side:
Dardanians, Pelasgians, Thracians, Cicones, Paeonians, Paphlagonians,
Halizones, Mysians, Phrygians, Maeonians, Carians, Lycians.

Added in Book 3: Helen, Paris/Alexandros (see policy above), Antenor,
Laodice, Helicaon, Aethra, Pittheus, Clymene, Panthous, Thymoetes, Lampus,
Clytius, Hicetaon, Ucalegon, Idaeus (herald of Troy), Laomedon, Castor,
Polydeuces (not "Pollux"), Otreus, Mygdon, Lycaon (Paris's brother — same
name as Pandarus's father, 2.826), Dardanus ("Dardanus' descendant" for
Δαρδανίδης Priam). Scaean Gates. Kranae. Sangarius (river). Phrygia,
Maeonia, Lacedaemon.

Added in Book 24: Mestor and Troilus (Priam's dead sons, named
only here), Agathon, Pammon, Antiphonus, Dius (the nine-son
roll-call, 24.249-252; Helenus, Paris, Polites, Deiphobus,
Hippothous already registered — this Hippothous distinct from
the Pelasgian, 2.840), Polyctor (Hermes' fictional father),
Niobe, Sipylus, Macar of Lesbos (24.544), Cassandra (her one
living appearance; first named 13.366), the Mysians as
mule-givers (24.278). Closed threads: the raw-eating triplet
(4.35, 22.346, 24.212); the ford of Xanthus (14.433-434 =
21.1-2 = 24.692-693, third and last); the supplication arc
(Tros → Lycaon → Hector refused; Priam accepted, 24.477-570);
Priam's father-argument (22.416-428 → 24.486-506); "your heart
must be iron" (24.205 = 24.521); Iris's message = Zeus's
verbatim (24.146-158 ≈ 175-187, one line shorter as in the
Greek); Andromache's paired laments (22.477-514 bodiless,
24.725-745 at the bier); "man-slaughtering" given last to
Hector's own head (24.724); Briseis restored (24.676). The
poem ends on the registered "Hector, the tamer of horses."

Added in Book 23: Amphidamas (of Opoeis — his son the boy
Patroclus killed over dice; a third Amphidamas, cf. 10.268-270),
Aethe (Agamemnon's mare) and Podargus (Menelaus's horse — same
name as Hector's horse, 8.185), Echepolus son of Anchises of
Sicyon (distinct from the Trojan victim, 4.458), Arion (Adrastus's
divine horse), Amarynceus and Buprasium (from 2.615-624),
Clytomedes son of Enops (a third Enops), Ancaeus of Pleuron,
Iphiclus, Phyleus and Polydorus as Nestor's rivals (a third
Polydorus), the Actor-sons / Molione twins (cf. 2.621, 11.709-752),
Epeius son of Panopeus, Euryalus's Theban games for "fallen
Oedipus" (the poem's only Oedipus), Thoas of Lemnos (the king —
distinct from the Aetolian), Noëmon (Antilochus's companion —
same name as the Lycian victim, 5.678), Sidon / Sidonian
craftsmen (cf. 6.290-291). The mare-for-mule prize list, the
twelve-oxen tripod and four-oxen woman (23.703-705) — keep these
valuations if echoed.

Added in Book 22: no new named persons — the poem's cast is
closed for its climax. New fixed items: the Dog of Orion /
harvest star (22.26-31); the two springs and the washing-troughs
(22.147-156); Hesperus (22.317-318); "the day of orphaning"
(22.490); Astyanax glossed "lord of the city" (22.506-507, as at
6.402-403). "But why does my own heart argue these things with
me?" now five-fold: 11.407 (Odysseus) and 17.97 (Menelaus) — both
harmonized from "debate" in audit, 2026-07-26 — 21.562 (Agenor),
22.122 (Hector), 22.385 (Achilles) — kept identical; any further
occurrence must match.

Added in Book 21: Laothoe (daughter of Altes; mother of Lycaon
and Polydorus), Altes (lord of the Lelegians; his Pedasus is the
town on the Satnioeis, 6.34-35), Euneus son of Jason ("the son of
Jason," 21.41 — named at 7.468), Eëtion of Imbros (a third
Eëtion), Imbros, Arisbe (from 2.836), Pelegon, Asteropaeus (first
named 12.102), Axius and Paeonia (from 2.848-850), Periboea,
Acessamenus, the seven Paeonians (Thersilochus, Mydon — a second
Mydon, cf. 5.580 — Astypylus, Mnesus, Thrasius, Aenius,
Ophelestes — a second, cf. 8.274), Achelous, Simoïs (the river as
combatant; named since 4.475), the Ileian plain (21.558), Agenor
son of Antenor (active since 4.467). "Dog-fly" (κυνάμυια) for
Ares' and Hera's insult, 21.394, 421. "Unwearied One" (Ἀτρυτώνη)
21.420 as registered since 2.157.

Added in Book 20: Callicolone, Erichthonius, Tros the ancestor
(distinct from Tros son of Alastor, killed 20.463), Assaracus,
Capys (Ganymede, Ilus, Laomedon, Tithonus, Lampus, Clytius,
Hicetaon already registered), Otrynteus, Iphition, Hyde, Hyllus
(river), Demoleon, Hippodamas, Polydorus son of Priam (by
Laothoe — named 21.84-91, 22.46-53), Dryops (victim; the name
only here in the poem), Demuchus son of Philetor, Philetor, Laogonus and Dardanus sons of Bias (a
third Bias; Laogonus a second — cf. 16.604), Alastor (a third
bearer), Mulius (a second — cf. the Epeian, 11.739), Echeclus
son of Agenor (a second — cf. 16.694), Deucalion (Trojan victim
— same name as Idomeneus's father, 13.451), Rhigmus son of
Peiros (= Peiroos of 2.844, 4.520; "Peiros" as printed here),
Areithous the aide (a third bearer — cf. the club-fighter and
his line, 7.8-10), the Heliconian lord (Poseidon of Helice —
cult title, 20.404).

Added in Book 19: Eileithyia / the Eileithyiae (birth-goddesses,
19.103, 119), Alcmene, Eurystheus, Sthenelus son of Perseus
(distinct from Sthenelus son of Capaneus, 2.564), Perseus,
Neoptolemus (named only here in the poem, 19.327), Scyros (cf.
9.668), Alcimus (19.392 — the short form of Alcimedon, 16.197;
both forms kept as printed), Mynes (Briseis's husband, 19.296;
his city cf. 2.690-693), Hyperion (as the shining sun, 19.398 —
cf. 8.480).

Added in Book 18: the thirty-three Nereids (18.39-49): Glauce,
Thaleia, Cymodoce, Nesaea, Speio, Thoë, Halië, Cymothoë, Actaea,
Limnoreia, Melite, Iaera, Amphithoë, Agave, Doto, Proto, Pherousa,
Dynamene, Dexamene, Amphinome, Callianeira, Doris, Panope,
Galateia, Nemertes, Apseudes, Callianassa, Clymene (a second
bearer — same name as Helen's attendant, 3.144), Ianeira, Ianassa,
Maera, Oreithyia, Amatheia. Also: Charis (Hephaestus's wife here;
the Odyssey gives him Aphrodite — cross-epic divergence permitted),
Eurynome daughter of Ocean, Opoeis (Menoetius's home; recurs
23.85), Daedalus, Ariadne, Knossos, the Linos-song (λίνος, the
harvest lament).

Added in Book 17: Phrontis (Euphorbus's mother), Mentes of the
Cicones (not the Odyssey's Taphian), Hippothous son of Pelasgian
Lethus (dies; from 2.840-843), Lethus, Larisa (from 2.841),
Schedius son of Iphitus (dies; the 2.517 Phocian — distinct from
Schedius son of Perimedes, 15.515), Panopeus, Phorcys son of
Phaenops (dies; from 2.862), Periphas the herald son of Epytus
(distinct from the Aetolian Periphas, 5.842), Epytus, Leiocritus
son of Arisbas, Arisbas, Apisaon son of Hippasus (second Apisaon,
cf. 11.578; fourth Hippasus), Paeonia, Aretus (dies), Podes son of
Eëtion (Hector's feast-companion; the name Eëtion again),
Phaenops son of Asius of Abydos (Hector's guest-friend — same name
as 5.152's Phaenops; the Asius name a fourth time), Coeranus of
Lyctus (dies; distinct from the Lycian Coeranus, 5.677), Lyctus,
Alectryon (Leïtus's father), Laodocus (Antilochus's companion —
distinct from 4.87's Laodocus), Dioreus/Diores (Automedon's
father — distinct from the Epeian 2.622 and the victim 4.517).

Added in Book 16: Automedon (active), Xanthus and Balius (the
horses), Podarge the harpy, Zephyrus (as sire), Pedasus the horse
(same name as the town and the twin), Spercheius, Polydora, Borus
son of Perieres (same name as 5.44's Maeonian), Menesthius the
Myrmidon (distinct from Areithous's son, 7.9), Eudorus, Polymele,
Phylas, Echecles son of Actor, Peisander son of Maemalus (third
Peisander), Alcimedon son of Laerces, Dodona, the Selloi,
Pyraechmes (from 2.848), Amydon, Axius, Areïlycus (the second),
Amphiclus, Atymnius and Maris sons of Amisodarus (Atymnius also
5.581), Amisodarus, the Chimaera (from 6.179), Cleobulus, Lycon,
Erymas (two in this book: 345, 415), Thestor son of Enops (same
name as Calchas's father and 12.394's Alcmaon's father), Pronous,
Erylaus, Amphoterus, Epaltes, Tlepolemus son of Damastor (distinct
from Heracles' son, 2.653), Echius (third bearer), Pyris, Ipheus,
Euippus, Polymelus son of Argeas, Thrasymelus, Epeigeus son of
Agacles, Budeum, Sthenelaus son of Ithaemenes, Bathycles son of
Chalcon, Hellas (as Myrmidon home-district), Laogonus son of Onetor
(a second Laogonus 20.460), Onetor, Asius son of Dymas (Hecuba's
brother — third Asius), Dymas, Sangarius (from 3.187), Cebriones
(dies; first named 8.318), Euphorbus son of Panthous, Adrestus
(fifth bearer!), Autonous (second), Echeclus (another 20.474),
Perimus son of Megas, Epistor, Melanippus (fourth!), Elasus,
Mulius (second, cf. 11.739), Pylartes (second, cf. 11.491).

Added in Book 15: Themis (active), Sphelus, Boucolus, Deiochus,
Caletor son of Clytius (distinct from Caletor father of Aphareus,
13.541), Lycophron son of Mastor (Cytheran exile), Cleitus son of
Peisenor, Astynous son of Protiaon (second Astynous, cf. 5.144),
Schedius son of Perimedes (distinct from Schedius son of Iphitus,
2.517), Laodamas son of Antenor, Otus of Cyllene (distinct from the
Aload Otus, 5.385), Croesmus, Dolops son of Lampus (distinct from
Dolops son of Clytius, 11.302), Euphetes of Ephyra, Melanippus son
of Hicetaon (third bearer), Copreus, Periphetes of Mycenae (the
greater of the two Periphetes, cf. 14.515), Phylace (Medon's exile
home; also 2.695).

Added in Book 14: Portheus, Agrius, Melas (Diomedes' great-uncles),
Rhea (first named), Tethys, Pieria, Emathia, Athos, Pasithea, the
Graces (Charites, as marriageable persons), Lecton, Gargaron (peak —
from 8.48), Ixion (via "Ixion's wife"), Danaë, Acrisius, Perseus,
Europa (as "the daughter of far-famed Phoenix" — Phoenix here the
Phoenician eponym, not the tutor), Rhadamanthys, Semele, Dionysus,
Alcmene (first named), Demeter (as love-object), Satnius, Enops
(same name recurs 16.401, 23.634), Prothoenor (from 2.495),
Areïlycus (another at 16.308), Archelochus (dies; from 12.100),
Promachus, Alegenor, Ilioneus, Phorbas (Trojan, Hermes-loved —
distinct from 9.665's Lesbian Phorbas), Hyrtius, Gyrtius, Mermerus,
Prothoon, Periphetes (a second, greater Periphetes dies 15.638),
Hyperenor (recalled 17.24-28), Cos, Styx (as oath-water in full
ceremony).

Added in Book 13: the Hippemolgoi ("Mare-milkers") and Abioi,
Samothrace ("Thracian Samos"), Imbros, Imbrius, Mentor (Trojan-side —
not the Odyssey's), Pedaeum, Medesicaste, Amphimachus son of Cteatus
(distinct from the Elean 2.620 and the Carian 2.870), Stichius,
Pleuron, Calydon (from Book 9), Othryoneus, Cabesus, Cassandra
(first appearance), Deucalion (Idomeneus's father; the flood-hero is
not in Homer), Minos, Ephyri and Phlegyes, Hypsenor son of Hippasus
(second Hypsenor, cf. 5.76; second Hippasus, cf. 11.426), Aesyetes
(the tomb 2.793), Hippodameia (Alcathous's wife — same name as
Peirithous's, 2.742), Ascalaphus (dies; from 2.512), Aphareus son of
Caletor (a second Caletor 15.419), Thoon (again), Adamas, Deïpyrus
(dies; from 9.83), Peisander (Trojan — second bearer, cf. 11.122),
Harpalion, Euchenor, Polyidus the seer of Corinth (distinct from the
Trojan Polyidus 5.148), Ionians (only here), Phthians, Pheidas, Bias
(third bearer), Amphion, Dracius, Medon (= 15.333ff), Eriopis,
Iphiclus, Podarces (from 2.704), Phalces, Orthaeus, Polyphetes,
Palmys, Ascanius and Morys sons of Hippotion, Ascania.

Added in Book 12: the eight rivers of Ida (Rhesus — same name as the
Thracian king of Book 10, Heptaporus, Caresus, Rhodius, Granicus,
Aesepus — also the twin 6.21, Scamander, Simois), Alcathous (dies
13.427ff), Asteropaeus (first appearance — the river-duel of Book 21),
Deucalion (Idomeneus's father), Iamenus, Orestes (Trojan — third
bearer of the name), Adamas son of Asius, Oenomaus (second bearer,
cf. 5.706), Damasus, Pylon, Ormenus (third bearer), Hippomachus son
of Antimachus (brother of 11.122's pair), Antiphates, Menon, Epicles,
Alcmaon son of Thestor (same name as Calchas's father), Thootes the
herald, Pandion, Lapiths (as a people in battle).

Added in Book 11: Tithonus, Cinyras, Polydamas (first appearance),
Bienor, Oïleus the charioteer (distinct from Ajax's father), Isus,
Antiphus (Priam's son — third bearer: cf. 2.678, 2.864), Peisander
(a second follows 13.601), Hippolochus (Antimachus's son — same name
as Glaucus's father, 6.119), Antimachus, Iphidamas, Coon, Cisses,
Asaeus, Autonous, Opites, Dolops son of Clytius (another Dolops
15.525), Opheltius (second bearer, cf. 6.20), Agelaus (second, cf.
8.257), Aesymnus, Orus, Hipponous, Thymbraeus, Molion, Hippodamus,
Hypeirochus (and Hypeirochus father of Itymoneus, 11.673),
Agastrophus, Paeon, Deïopites, Thoon (third bearer), Ennomus (second,
cf. 2.858), Chersidamas, Charops, Socus, Hippasus, Doryclus,
Pandocus, Lysander, Pyrasus (also a town 2.695), Pylartes (another
16.696), Apisaon, Phausius, Eurymedon (Nestor's aide — same name as
Agamemnon's driver 4.228 area), Hecamede, Arsinous, Itymoneus,
Mulius, Agamede, Augeias, Moliones/Actor's line (Cteatus and Eurytus
unnamed here), Thryoessa, Alpheius, Minyeïus, Arene, Buprasion,
Olenian rock, Alesion, Eleians/Epeians, Asclepius, Podaleirius,
Chiron (named 4.219 first), Pramnian wine, Tenedos.

Added in Book 10: Dolon, Eumedes, Rhesus, Eïoneus, Hippocoon,
Autolycus (Odysseus's maternal grandfather), Amphidamas of Cythera
(distinct from the Epeian 2.622 area names; second bearer of the name),
Molus, Eleon, Scandeia, Cythera, Thymbre, Caucones (first appearance —
not in the Book 2 catalogue), Ilus (tomb of; the founder-eponym).
"Thracians of Rhesus" are new-come and stand outside the Book 2
catalogue.

Added in Book 9: Thrasymedes, Aphareus, Deïpyrus, Lycomedes, Creon,
Automedon (first active), Phoenix (active; named 9.168), Amyntor, Ormenus
(Phoenix's grandfather — same name as the victim 8.274), Dolopes,
Curetes, Althaea, Cleopatra (Meleager's wife — see note 9.[35]),
Marpessa, Idas, Euenus (her father — same name as Mynes' father, 2.693),
Alcyone, Phorbas, Diomede (woman of Lesbos), Iphis, Scyros, Enyeus,
Chrysothemis, Iphianassa, Orestes (Agamemnon's son — a Trojan victim
5.705 shares the name), Odius the herald (distinct from the Halizone
captain 2.856), the seven cities (Cardamyle, Enope, Hire, Pherae —
fourth bearer, Antheia, Aipeia, Pedasus — third bearer), Lesbos,
Egyptian Thebes ("of the hundred gates").

Added in Book 8: Eniopeus, Thebaeus, Archeptolemus, Cebriones (Hector's
brother), Agelaus, Phradmon, Orsilochus (a Trojan — third bearer),
Ormenus, Ophelestes, Daetor, Chromius (fourth bearer), Lycophontes,
Amopaon, Polyaemon, Melanippus, Gorgythion, Castianeira, Aesyme,
Mecisteus son of Echius (distinct from Euryalus's father, 2.566),
Echius, Alastor (second bearer), Eurystheus, Erebus, Iapetus, Hyperion,
Gargaron, Helice and Aegae (Poseidon's seats), Hector's horses Xanthus,
Podargus, Aethon, Lampus (Xanthus also names Achilles' horse and the
river — distinct).

Added in Book 7: Areithous "the Club-man," Menesthius (Areithous's son —
distinct from the Myrmidon Menesthius, 16.173), Phylomedusa, Eioneus,
Iphinous, Dexias, Ereuthalion (story told; named 4.319), Lycurgus the
Arcadian (distinct from the Thracian, 6.130), Celadon, Pheia, Iardanus,
Tychius, Euneus, Jason, Hypsipyle, Salamis (Ajax's home; cf. 2.557).

Added in Book 6: Axylus, Calesius, Dresus, Opheltius, Aesepus and
Pedasus (twins — same names as the river 2.825 and the town 6.35),
Abarbarea, Bucolion, Astyalus, Pidytes, Aretaon, Ablerus, Elatus,
Phylacus, Melanthius, Adrestus the suppliant (6.37 — fourth bearer),
Teucer (first appearance), Helenus the seer, Glaucus the Lycian (his
great-grandfather Glaucus son of Sisyphus shares the name), Hippolochus,
Bellerophon, Proetus, Anteia, Sisyphus, Aeolus, Isander, Laodameia,
Chimaera, Solymi, Lycurgus, Dryas (his father — same name as the Lapith
1.263), Dionysus, Nysa, Hecuba (first named), Cisseus, Andromache,
Astyanax/Scamandrius (see note 6.[24]), Messeïs, Hypereia (spring — same
name as the spring 2.734), Sidon/Sidonian, Satnioeis (river), Arisbe,
Percote, Placus, Cilicians (Eëtion's people — Anatolian, not the later
Cilicia).

Added in Book 5: Dares, Phegeus, Idaeus (Dares' son — distinct from
Priam's herald, 3.248), Phaestus, Borus, Scamandrius the hunter (distinct
from Hector's son, Book 6), Strophius, Phereclus, Tecton, Harmon, Pedaeus,
Theano, Hypsenor, Dolopion, Astynous, Hypeiron, Abas, Polyidus, Eurydamas,
Xanthus and Thoon (sons of Phaenops), Echemmon, Chromius (a Priam son;
same name: a Pylian 4.295, a Lycian 5.677), Deipylus, Cypris, Enyo, Dione,
Otus, Ephialtes, Aloeus, Eëriboea, Amphitryon, Paiëon, Aegialeia, Adrastus
of Argos (her father — third bearer of the name), Ganymede, Tros,
Deicoon, Pergasus, Crethon, Orsilochus, Diocles, Ortilochus (grandfather —
spelling varies in the Greek; follow the printed text), Pylaemenes,
Mydon, Atymnius, Menesthes, Anchialus, Amphius son of Selagus (distinct
from Amphius 2.830), Paesus, Coeranus, Alcandrus, Halius, Noëmon,
Prytanis, Teuthras, Orestes (Trojan-side; not Agamemnon's son), Trechus,
Oenomaus, Helenus son of Oenops (distinct from Priam's seer son),
Oresbius, Hyle, Stentor, Periphas, Ochesius, Tarne, Pherae (Diocles'
town; also 2.711 Thessalian Pherae).

Added in Book 4: Hebe, Chiron, Antilochus, Echepolus, Agenor, Simoeisios,
Leucus, Democoon, Diores, Eurymedon, Tydeus, Polyneices, Eteocles, Maeon,
Ereuthalion, Pelagon, Alastor, Chromius, Haemon, Bias. Cadmeans (people
of Thebes). Pergamos (Troy's citadel). Rivers: Simois, Asopus. Tricca,
Abydos, Aenus, Zeleia. "Seven-gated Thebes" (Greek Thebes); "the walls of
Thebe" for Eëtion's city only.

Places: Troy, Ilion, Chryse, Cilla, Tenedos, Phthia, Pylos, Argos, Lemnos,
Thebe (Eëtion's city — not Greek Thebes), Ocean (Ὠκεανός). Catalogue
place names in familiar Latinized forms; keep diaeresis in Eïones,
Boebeïs, Selleïs. Rivers: Cephisus, Alpheius, Peneius, Titaressus, Axius,
Maeander, Scamander (adj. "Scamandrian"), Xanthus, Hellespont
("strong-flowing").

Patronymics: rendered as "Atreus' son / son of Atreus," "Peleus' son,"
etc., not transliterated ("Atreides" avoided in the translation itself).
Peoples: Achaeans / Danaans / Argives — follow whichever the Greek uses.

## Cross-epic notes (Odyssey project, `..\odyssey`)

Where the two projects render the same formula differently, the divergence
is currently intentional (independent projects); revisit only if they are
to become companion volumes. Known divergences: their "gray-eyed" (our
"grey-eyed"); "Zeus who gathers the clouds" ("Zeus the cloud-gatherer");
"Menelaus of the great war-cry" ("good at the war-cry"); "Dawn… with
fingers of rose" ("rosy-fingered Dawn"); "Odysseus of the many designs"
("resourceful Odysseus"); "noble" for δῖος ("brilliant"); "Zeus-born"
("Zeus-sprung").

## Notes for later books

- Formula notes already placed in Books 1-4 establish the conventions
  above — do not re-footnote them in Books 5-24.
- 2.111-118 ≈ 9.18-25: reuse the Book 2 English verbatim in Book 9
  (there spoken in earnest).
- The δαῖτα decision at 1.4-5: vulgate followed; precedent for preferring
  the vulgate over singly-attested Zenodotean readings.
- ἀμφιγυήεις "crook-footed": revisit if Book 18's Hephaestus scenes make
  it awkward.
- Duals rendered as explicit "the two …" where English needs it
  (1.327-347); keep in mind for the Book 9 embassy crux.
- βαρβαρόφωνος "of barbarous speech" (2.867) — "barbarian" reserved
  (anachronistic) throughout.
- Diomedes' silence under rebuke (4.401-402) paid off at 9.32-49 (done).
- 9.14-15 (dark-spring simile) = 16.3-4 verbatim: reuse the Book 9
  English for Patroclus's tears.
- The Meleager/Cleopatra paradigm (9.524-599) is the map of Book 16:
  the wife's plea comes last and works; keep note 9.[35] in view.
- books/book_09.txt lacks 9.458-461 (numbering jumps 457→462); the
  translation reproduces the gap, with the missing lines translated
  inside note 9.[32]. Line-count checks must expect 709 lines.
- δμώς/δμῳή "slave" policy becomes live in Book 6 (Hector's household)
  — see the household-terms section above.
- ἀλαοσκοπιή "kept no blind man's watch" (10.515) recurs at 13.10 and
  14.135 (Poseidon) — reuse verbatim.
- The Book 10 interrogation formulas ("But come, tell me this, and
  recount it truly") recur at 24.380, 24.656 — reuse verbatim.
- Nestor's "shall I be wrong, or right, in what I say?" (10.534) = Od.
  4.140 (cross-epic; divergence permitted per policy).
- γλαφυρός and κοῖλος are both "hollow" (ships) — documented merge,
  set by Books 1-2 usage.
- Riding (not driving) horses: 10.513, 10.529 bareback escape; the
  only other riding is the simile 15.679-684 — keep the distinction
  visible there.
- Achilles' horses coveted: Dolon 10.321-323, warned of at 17.75-78 —
  echo "the horses of the war-minded son of Aeacus" (10.402) when
  17.76 recurs (ἵππους Αἰακίδαο δαΐφρονος).
- books/book_11.txt lacks 11.543 (numbering jumps 542→544); the
  translation reproduces the gap, with the Aristotle-quoted line
  translated in note 11.[35]. Line-count checks must expect 847
  lines. (book_14.txt similarly lacks 14.269 — handle the same way.)
- 11.362-367 = 20.449-454: reuse the Book 11 "Dog!" speech verbatim
  for Achilles in Book 20. (Done.)
- 11.794-803 ≈ 16.36-45: Patroclus repeats Nestor's plan — reuse the
  Book 11 English nearly verbatim at the opening of Book 16 (16.44-45
  = 11.802-803 exactly).
- 11.654 "He would quickly blame even the blameless" — Patroclus's
  fear; its harder twin is 16.29-35.
- Patroclus is still in Eurypylus's hut at 15.390-404 — continuity.
- The sunset clause of Zeus's plan (11.193-194 = 11.208-209) —
  fulfilled (done, 18.239-242: Hera sends the unwilling Sun into
  Ocean).
- Muse invocations remaining: 14.508, 16.112 — reuse 2.484 line.
- Polydamas's four counsels: 12.61 (accepted), 12.211 (rejected),
  13.726 (accepted), 18.254 (rejected — fatal; done). Hector
  recalls the rejection at 22.99-107 — keep the 18.311-314 wording
  ("whose counsels were ruinous") in view there.
- Glaucus's arm wound (12.387-391) is begged healed at 16.508-531.
- Sarpedon's deferred death (12.402-403) is weighed at 16.433-461;
  echo "he was not to be broken by the ships' sterns."
- Asius's death-notice (12.116-117) is paid at 13.384-393.
- The diver-fall image (12.385-386) recurs at 16.742 (Cebriones).
- 13.131-133 (phalanx: "buckler pressed on buckler...") = 16.215-217
  — reuse verbatim for the Myrmidons.
- 13.389-391 (shipwright tree-fall) = 16.482-484 (Sarpedon) — reuse.
- 13.694-697 (Medon's exile biography) = 15.333-336 — reuse; Medon
  dies there.
- Ascalaphus dead, Ares ignorant (13.518-525) — paid at 15.110-142.
- Aeneas's grudge (13.460-461) — cf. 20.178-183, 20.302-308.
  (Done: Poseidon's rescue and dynastic prophecy, 20.300-308.)
- The Theomachy pairings (20.67-74) are fought out at 21.383-513
  — keep the pairing-list wording when each match is called.
- Polydorus dies clutching his bowels (20.413-418); he and Lycaon
  are Laothoe's sons — the debt is completed at 21.34-135
  (Lycaon) and mourned at 22.46-53 (Priam names the pair). Echo
  "clutching his bowels" when Priam imagines his sons' deaths.
- The wall of Heracles and the sea-monster (20.144-148) is the
  Hesione backstory: Poseidon recalls building Troy's wall for
  Laomedon at 21.441-457 — keep the two wall-stories distinct
  (Heracles' refuge-wall vs the city wall).
- Refused supplication: Tros son of Alastor (20.463-472) opens
  the sequence that runs Lycaon (21.64-119, done) → Hector
  (22.337-354, done: the raw-flesh wish). The sequence is
  answered — supplication finally accepted — at 24.477-570.
- 16.856-857 = 22.361-363 soul-flight couplet: done, verbatim.
  16.441-443 = 22.179-181 (the rescue-rebuke): done, verbatim.
  18.115-116 = 22.365-366: done. 22.99-107 answers 18.249-313
  (Polydamas shame): done.
- Corpse-preservation: Hector dragged (22.395-404); Aphrodite
  and Apollo protect the body at 23.184-191; the gods' debate
  and the ransom at 24 — keep "defiled in his own fatherland"
  and "portion of fire" wording in view.
- Priam's plan announced at 22.416-428 ("He too has a father —
  Peleus") is executed at 24.159ff; reuse the father-argument
  wording at 24.486-506.
- Andromache's headdress flung off (22.468-472, Aphrodite's
  wedding veil) — the wedding at Eëtion's house; cf. her Book 6
  biography; her final lament at 24.723-745 completes the pair
  (this one bodyless, that one at the bier).
- Achilles' "eat it raw" (22.346-347) caps Hera's 4.35-36 and
  Hecuba's 24.212-213 raw-eating wishes — keep the three in
  one register ("raw" + "hack/devour").
- The funeral-games inversion (22.159-166: they ran "for the
  life of Hector") is answered by the real games of Book 23 —
  done (the prize-lists; the turn-post as an old grave-mark,
  23.331-333).
- The twelve youths: vow 18.336-337 → taken 21.27-32 → killed
  23.175-176 with the narrator's verdict ("evil was the work his
  heart intended") — thread closed.
- Achilles' fast/wash vow (19.208-210) honored at 23.42-48 —
  done. The shared-urn instruction (23.83-92, 243-245) and the
  double mound (23.126, 245-248) are the poem's forward pointer
  beyond itself (cf. Od. 24.71-84).
- Aphrodite's rose-oil and Apollo's cloud over Hector
  (23.184-192) begin Book 24's corpse-preservation — continue
  the wording at 24.18-21, 24.411-423.
- Achilles' only smile: 23.556 (at Antilochus) — as registered
  from the 17.698-701 pointer on Antilochus's gentleness.
- The Book 1 inversions of Book 23 (Achilles as peacemaker
  23.492-498; the prize freely given to Agamemnon 23.890-897;
  Talthybius receiving 23.897 vs taking Briseis 1.320-348) —
  cite in Book 24's commentary if the reconciliation-arc is
  summarized.
- 14.433-434 = 21.1-2 (ford of eddying Xanthus) — done; the same
  ford recurs at 24.692-693 on Priam's return — reuse again.
- The twelve youths taken alive (21.27-32) pay the vow of
  18.336-337 (done); they are killed at 23.175-176 — reuse
  "twelve" + "blood-price" wording there.
- 21.111-113 ("a dawn, or an evening, or a midday") — Achilles'
  own death-terms; keep in view for 22.359-360 and Thetis's
  echoes in 24.
- 21.374-376 = 20.315-317 (Hera's Troy-burning oath-clause,
  sworn back by the river) — kept verbatim; done.
- Achilles chased Apollo-as-Agenor (21.599-605); Apollo reveals
  himself at 22.7-20 — keep "you chased" continuity and the
  "quick feet" taunt in view.
- The Theomachy pairings (20.67-74) fought out at 21.383-513 —
  done. Hermes/Leto and Poseidon/Apollo settled without blows.
- 18.115-116 ("My own death-spirit I will accept whenever / Zeus
  wills to accomplish it, and the other immortal gods") ≈
  22.365-366 — reuse the Book 18 English verbatim there.
- The vow of the twelve Trojan youths (18.336-337) is repeated
  nearly verbatim at 23.22-23 ("and before your pyre I will cut
  the throats of twelve / shining children of the Trojans") —
  reuse; paid at 21.27-32 (the taking) and 23.175-176 (the
  killing).
- Thetis's sapling lament 18.56-62 = 18.437-443 — kept verbatim
  (internal; done).
- Hephaestus's guest-greeting 18.386-387 = 18.424-425 (Charis,
  then Hephaestus) — kept verbatim (internal; done).
- Book 19 opens with the armor laid down clashing (19.12-13);
  the marvel-formula of 18.466-467 ("any man of the many who see
  it hereafter will marvel") is answered by the Myrmidons' fear
  to look at 19.14-15. (Done.)
- Pylaemenes contradiction: killed 5.576-579, mourns 13.658-659
  (ath.) — documented in note 13.[29]; do not "fix."
- books/book_14.txt lacks 14.269 (numbering jumps 268→270); the
  translation reproduces the gap; the line is translated in note
  14.[13]. Line-count checks must expect 521 lines. All three known
  source gaps (9.458-461, 11.543, 14.269) are now handled.
- 14.433-434 (ford of eddying Xanthus, "whom immortal Zeus begot")
  ≈ 21.1-2 — reuse the wording at Book 21's opening.
- Sleep and Death carry Sarpedon at 16.672, 16.682 — echo "Sleep,
  the brother of Death" (14.231).
- Hyperenor's death (14.516-519) is retold with added insult at
  17.24-28 — the ledgers do not reconcile; keep both as printed.
- Hector returns at 15.239 only by Apollo's intervention — the
  concussion sequence 14.433-439 is continuous with 15.9-11,
  15.239-262. (Done.)
- Zeus's plan-speech 15.56-77 is the outline of Books 16-22 and the
  fall of Troy: echo its wording as each clause is fulfilled (16.
  Patroclus/Sarpedon; 22. Hector; "through the counsels of Athena").
- Hector's burial-denial threat (15.348-351) prefigures the corpse-
  treatment theme of Books 22-24 — echo "portion of fire."
- The burning-ship flare Zeus waits for (15.599-602) arrives at
  16.122-124 — reuse "the flare of a burning ship" wording.
- 15.610-614 (Athena speeding Hector's death-day) is the counterpart
  of 22.212-213 (the scales) — keep phrasing in view.
- 16.856-857 = 22.361-363: reuse the soul-flight couplet verbatim
  for Hector, and 16.844-854's dying-prophecy frame recurs there.
- The armor-transfer chain (16.793-804): Achilles' helmet/armor to
  Hector — stripped at 17.125, worn 17.192-214 (Zeus's comment),
  reclaimed on Hector's corpse in 22. Echo "and his destruction was
  near him."
- Euphorbus dies 17.9-60 (the Graces-hair simile) — keep his resume
  wording in view; Menelaus's shield-dedication is post-Homeric
  (Pythagoras legend — noted at 16.[43]).
- Achilles' cup and Dodona prayer (16.220-248): the prayer-form
  returns at 24.306ff. The Selloi do not recur.
- 16.7-11 (little-girl simile) is answered by Achilles' own tears at
  18.316ff, 23.222ff — keep the tenderness-register.
- The wrath's formal end-date moved: 16.60-63 ("when the war reached
  my own ships") supersedes 9.650-655; cite in Book 18-19 notes.
- Hector's beheading intent (17.125-127) is the corpse-outrage
  baseline for Books 22-24; Glaucus's corpse-exchange proposal
  (17.160-163) prefigures the ransom of Book 24.
- Zeus's ποινή speech (17.198-208): Andromache and the armor —
  echo at 22.437ff (Andromache weaving, unaware) and at the
  armor's recovery in 22.
- Antilochus runs unarmed and weeping (17.698-701) → Book 18 opens
  with his arrival; his gentleness is recalled at 23.556.
- The weeping horses (17.426-440) speak at 19.404-417 (Xanthus's
  prophecy) — done; the mane-to-the-ground bow renders the
  17.437-440 grief-posture.
- 17.454-455 reuses the sunset clause (= 11.193-194) — third
  statement; fulfilled 18.239-242.
- Xanthus's "by a god, and by a man" (19.416-417, ath. Ar.) is
  specified at 22.359-360 (Paris and Phoebus Apollo) — echo the
  wording in Hector's dying prophecy.
- Ate is "Blindness" (9.502-512, 19.85-136 both) — Book 9 gives
  her sound feet, Book 19 soft ones; both portraits kept, note
  19.[9] documents the pair. Any later ἄτη-personification stays
  "Blindness."
- Achilles' fast (19.208-210, 19.305-308) continues into Book 23:
  at 23.42-53 he yields to the meal but refuses to wash before
  the pyre is built — keep the vow's wording in view there.
