"""Formula-conformance checker for the Iliad translation.

Mechanically verifies that registered fixed renderings (translation/CONVENTIONS.md)
actually appear wherever the Greek formula occurs. For every Greek line containing
a registered formula stem, the English at the same line number (+/- 1 line, to
absorb deliberate enjambment rebalancing) must contain one of the accepted
renderings.

This is the automatable slice of consistency checking only — it proves the
register is being obeyed, not that the translation is faithful. Fidelity is the
audit's job (audit/rubric.md).

Usage:
    python tools/check_formulas.py            # check all translated books
    python tools/check_formulas.py 2 4        # check books 2 and 4 only

Exit status 0 if no violations, 1 otherwise.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# (greek stem(s), accepted English rendering fragment(s), label)
# Stems are chosen to be inflection-safe substrings of the Greek line.
CHECKS = [
    (["πόδας ὠκὺς", "ποδάρκης"], ["swift-footed"], "swift-footed Achilles"),
    (["ἄναξ ἀνδρῶν"], ["lord of men"], "lord of men"),
    (["νεφεληγερέτα"], ["cloud-gatherer"], "cloud-gatherer Zeus"),
    (["γλαυκῶπις"], ["grey-eyed"], "grey-eyed Athena"),
    (["λευκώλεν"], ["white-armed"], "white-armed"),
    (["βοῶπις"], ["ox-eyed"], "ox-eyed Hera"),
    (["κορυθαίολος"], ["flashing helmet"], "Hector of the flashing helmet"),
    (["φιλομειδὴς", "φιλομμειδὴς"], ["laughter-loving"], "laughter-loving Aphrodite"),
    # adjectival with Apollo named: "who strikes from afar";
    # standalone substantive: "the far-striker" (matches ἕκατος)
    (["ἑκηβόλ", "ἑκατηβόλ", "ἑκατηβελέτ"], ["strikes from afar", "far-striker"],
     "who strikes from afar / the far-striker"),
    (["ἑκάεργ"], ["worker-from-afar"], "the worker-from-afar"),
    (["καλλιπάρῃ"], ["fair-cheeked"], "fair-cheeked"),
    (["ἔπεα πτερόεντα"], ["winged words"], "winged words"),
    (["ῥοδοδάκτυλος"], ["rosy-fingered"], "rosy-fingered Dawn"),
    (["πολύμητις"], ["resourceful"], "resourceful Odysseus"),
    (["πολυμήχαν"], ["many devices"], "of many devices"),
    (["κάρη κομόωντ"], ["long-haired"], "long-haired Achaeans"),
    (["ἐϋκνήμιδ"], ["strong-greaved"], "strong-greaved Achaeans"),
    (["χαλκοχιτών"], ["bronze-shirted"], "bronze-shirted Achaeans"),
    (["ἱπποδάμ", "ἱππόδαμ"], ["horse-taming", "breaker of horses",
                              "tamer of horses"], "hippodamos"),
    (["Γερήνιος"], ["Gerenian"], "Gerenian horseman Nestor"),
    (["βοὴν ἀγαθὸς"], ["good at the war-cry"], "good at the war-cry"),
    (["ἀρηΐφιλος", "ἀρηϊφίλ"], ["dear to Ares"], "dear to Ares"),
    (["ὑπόδρα"], ["darkly"], "glaring darkly (hypodra idon)"),
    (["σκότος ὄσσε"], ["darkness covered his eyes"], "death formula: darkness"),
    (["δούπησεν δὲ πεσών"], ["fell with a thud"], "death formula: thud"),
    (["λῦσε δὲ γυῖα"], ["unstrung his limbs"], "death formula: unstrung"),
    (["δολιχόσκιον"], ["long-shadowed"], "long-shadowed spear"),
    (["νηλέϊ χαλκῷ"], ["pitiless bronze"], "pitiless bronze"),
    (["πολυφλοίσβοιο"], ["loud-roaring"], "loud-roaring sea"),
    (["ἀτρυγέτοιο"], ["barren sea"], "barren sea"),
    (["ἐὺ φρονέων ἀγορήσατο"], ["With good will toward them"], "eu phroneon line"),
    (["ἔκ τʼ ὀνόμαζε"], ["named h"], "spoke a word, and named"),
    (["ποιμένα λαῶν", "ποιμένι λαῶν", "ποιμὴν λαῶν"], ["shepherd of the people"],
     "shepherd of the people"),
    (["ἑλικώπιδα", "ἑλίκωπες", "ἑλίκωπας"], ["bright-eyed"], "bright-eyed"),
    (["μερόπων ἀνθρώπων", "μερόπεσσι"], ["mortal m"], "mortal men/man"),
]

LINE_RE = re.compile(r"^\s{0,5}(\d+)\s\s(.*)$")


def load(path):
    """Return {line_number: text} for a numbered Greek or translation file."""
    out = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        m = LINE_RE.match(raw)
        if m:
            n = int(m.group(1))
            # keep the first occurrence only: note sections cannot collide
            # because notes never match the "number + two spaces" shape.
            if n not in out:
                out[n] = m.group(2)
    return out


def check_book(num):
    greek_path = ROOT / "books" / f"book_{num:02d}.txt"
    eng_path = ROOT / "translation" / f"book_{num:02d}.txt"
    if not eng_path.exists():
        return None
    greek = load(greek_path)
    eng = load(eng_path)
    violations = []
    for stems, renderings, label in CHECKS:
        for n, gline in greek.items():
            if not any(s in gline for s in stems):
                continue
            window = " ".join(eng.get(k, "") for k in (n - 1, n, n + 1))
            if not any(r.lower() in window.lower() for r in renderings):
                violations.append((n, label, gline, eng.get(n, "<missing>")))
    return violations


def main(argv):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    nums = [int(a) for a in argv] if argv else range(1, 25)
    total = 0
    for num in nums:
        v = check_book(num)
        if v is None:
            continue
        status = "OK" if not v else f"{len(v)} VIOLATION(S)"
        print(f"book {num:02d}: {status}")
        for n, label, gline, eline in sorted(v):
            print(f"  {num}.{n} [{label}]")
            print(f"    GK: {gline}")
            print(f"    EN: {eline}")
        total += len(v)
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
