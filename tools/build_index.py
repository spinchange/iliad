"""Phase 1 of the name index: deterministic occurrence extraction.

Reads the authoritative translation files (translation/book_NN.txt), finds every
capitalized token in the *verse body* (never in the translator's commentary, the
epigraph, or the footnote apparatus), and records where each one occurs. Output
is a raw occurrence table — a list of candidate proper names with a citation for
every appearance — which the editorial canonicalization pass (Phase 2) then
curates and resolves into aliases.

This step makes no editorial judgments. It does exactly one non-obvious thing
beyond "find capitalized words": it drops a fixed stoplist of function words and
common line-initial words (And, But, Then, He, ...) so the candidate list isn't
drowned in sentence-openers. Everything dropped is still reported, under a
separate heading, so nothing is silently lost.

Format note (differs from the Odyssey project this is ported from): an Iliad
verse line is "<spaces><number><two spaces><text>" in a plain .txt file, and
footnote markers are bracketed integers "[7]" rather than "[^L7]". The verse
body of every book sits between the file's two horizontal rules; we key on those
rather than on the line shape, because the translator's commentary above the
first rule cites line numbers in prose ("318 (did the god make ...)") that are
otherwise indistinguishable from verse, and the footnote apparatus below the
second rule has indented continuation lines that are likewise ambiguous.

Usage:
    python tools/build_index.py                # writes index/occurrences.{json,md}
    python tools/build_index.py --min 3        # table shows names with >=3 hits
"""
import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "translation"
OUT = ROOT / "index"

# A verse line is "<optional spaces><number><whitespace><text>". Numbers are
# right-aligned in a field, hence the leading spaces.
VERSE = re.compile(r"^\s*(\d+)\s+(\S.*)$")

# The verse body is delimited above and below by a full-width rule. Every book
# has exactly two; anything outside them is commentary or apparatus.
RULE = re.compile(r"^-{20,}\s*$")

# Placeholder lines standing in for verses absent from the printed Greek, e.g.
# "[Lines 458-461 are absent from the printed text; see note 32.]" at 9.457.
# They sit inside the verse body but carry no verse of their own.
ABSENT = re.compile(r"^\s*\[Lines?\b.*absent from the printed text")

# Inline footnote markers like "wrath[1]" — stripped before tokenizing so the
# marker never fuses onto the preceding word.
FOOTREF = re.compile(r"\[\d+\]")

# A word is a run of letters (incl. accented ones); we keep the first letter's
# case to decide whether it's a candidate name.
WORD = re.compile(r"[^\W\d_]+", re.UNICODE)

# Common capitalized words that occur mainly as sentence/line openers or as
# generic address, not as proper names. Dropped from the candidate table (but
# reported separately). Kept deliberately conservative: when in doubt, a token
# stays IN the candidate list for the human curator to reject, rather than being
# hidden here.
STOP = {
    # pronouns / determiners / conjunctions / prepositions
    "A", "And", "As", "At", "But", "By", "For", "From", "He", "Her", "Here",
    "His", "How", "I", "If", "In", "It", "Its", "Me", "My", "No", "Nor", "Not",
    "Now", "O", "Of", "Oh", "On", "Or", "Our", "Out", "She", "So", "Some",
    "Such", "That", "The", "Their", "Them", "Then", "There", "These", "They",
    "This", "Those", "Thus", "To", "Up", "We", "What", "When", "Where", "Which",
    "While", "Who", "Whom", "Why", "With", "You", "Your", "Yet",
    # common verbs/adverbs that open imperative or exclamatory lines
    "Ah", "Alas", "Away", "Be", "Come", "Do", "Down", "Even", "Ever", "Give",
    "Go", "Good", "Hear", "Just", "Know", "Let", "Like", "Long", "Look", "May",
    "Much", "Nay", "Never", "Off", "Once", "Only", "Over", "Say", "See", "Since",
    "Still", "Take", "Tell", "Well", "Would",
    # generic relational / vocative nouns (people are named, these are roles)
    "Dear", "Father", "Friend", "King", "Lady", "Lord", "Man", "Master",
    "Men", "Mother", "Queen", "Sir", "Son", "Stranger", "Wife",
    # battle-narrative line-openers the Iliad adds to the above
    "Against", "Back", "Before", "Behind", "Beside", "Both", "Each", "Fight",
    "First", "Forward", "Have", "Hold", "Into", "Nine", "Rise", "Round",
    "Shame", "Stand", "Strike", "Three", "Through", "Twelve", "Two", "Under",
    "Was", "Were", "Yes",
    # participial and adverbial openers frequent in the battle books' syntax.
    # NB "Bear" is deliberately absent: it opens the imperative "Bear up"
    # three times, but it is also the constellation at 18.487 ("the Bear,
    # which men also call by the name of the Wagon"), which is a real
    # headword. The stoplist is per-token and all-or-nothing, so the name
    # wins and the three openers are left for the curator to ignore.
    "After", "Afterward", "Alike", "All", "Already", "Am", "Answering", "Are",
    "Around", "Better", "Bring", "Call", "Can", "Cease", "Drive",
    "Enough", "Fall", "Far", "Fear", "Fly", "Forth", "Friends", "Get", "Glaring",
    "Great", "Grieving", "Half", "Hard", "Him", "Holding", "Is", "Later",
    "Leaping", "Leave", "Less", "Made", "Make", "Many", "Meanwhile", "Most",
    "Move", "Near", "Neither", "Next", "Old", "One", "Poor", "Put", "Quickly",
    "Raising", "Ready", "Rouse", "Rushing", "Second", "Seeing", "Seized",
    "Send", "Set", "Sing", "Sit", "Speak", "Speaking", "Springing", "Standing",
    "Stay", "Stop", "Straight", "Strange", "Strong", "Sudden", "Surely",
    "Swift", "Swiftly", "Terrible", "Thinking", "Though", "Throw", "Together",
    "Turning", "Truly", "Turn", "Until", "Unwearied", "Wait", "Walk", "Watch",
    "Way", "Weeping", "Whole", "Whose", "Wide", "Wild", "Wise", "Work", "Yield",
    # residual line-openers surfaced by the >=3-hit gap review
    "Among", "Baby", "Brilliant", "Consider", "Did", "Either", "Everywhere",
    "Heaven", "Keep", "Lie", "Past", "Pitiless", "Rejoice", "Remember",
    "Soft", "Soon", "Therefore", "Think", "Vile", "Whichever", "Whoever",
    "Whomever", "Yours",
    # compass winds and quarters: in this poem they appear almost only inside
    # similes ("as when the South Wind comes"), as common nouns. The personified
    # wind-gods Boreas and Zephyrus are named and ARE headwords; these are not.
    "East", "North", "South", "West", "Wind", "Winds",
    # Tail sweep (2026-07-26): every one of the 902 tokens left unclassified
    # after the registry was seeded was reviewed by hand; these 167 are the
    # non-names. Mostly line-openers and common nouns that the earlier passes
    # missed because they appear once or twice rather than often. The other 735
    # are real names and are listed in index/tail-unclassified.txt as the
    # remaining entry-writing queue. Verified against the registry: none of
    # these is a classified headword.
    "Again", "Always", "Angered", "Another", "Apart", "Archer", "Bawling",
    "Because", "Begin", "Best", "Beyond", "Bid", "Blessed", "Blinded",
    "Boast", "Bowman", "Break", "Breaking", "Brightest", "Bury", "Carry",
    "Carrying", "Cattle", "Clanless", "Club", "Command", "Could", "Crook",
    "Cruel", "Damn", "Defend", "Defending", "Die", "Disperse", "Does",
    "Don", "Dropping", "Easily", "Eight", "Elder", "Eleven", "Elsewhere",
    "Endlessly", "Enemy", "Enraged", "Every", "Fearless", "Feel", "Fifty",
    "Fine", "Five", "Follow", "Foot", "Fortunate", "Four", "Fresh",
    "Friendliness", "Girded", "Goddess", "Godlike", "Gods", "Greatly",
    "Gripping", "Groaning", "Guest", "Has", "Help", "Hero", "High", "Hire",
    "Hit", "Horror", "Hurrying", "Husband", "Indeed", "Inside", "Instead",
    "Kinsmen", "Lake", "Last", "Lay", "Lead", "Leaning", "Little", "Madman",
    "Mare", "Merciless", "More", "None", "Nothing", "Often", "Other",
    "Others", "Otherwise", "Panting", "Perish", "Possessed", "Pray",
    "Press", "Promise", "Puffed", "Pursuit", "Quick", "Raging",
    "Remembering", "Renounce", "Respect", "Rivers", "Rout", "Ruinous",
    "Run", "Sack", "Seeking", "Seer", "Separately", "Seven", "Shake",
    "Shall", "Shorter", "Silence", "Sink", "Sinking", "Smiling", "Sooner",
    "Spears", "Spoils", "Step", "Stepping", "Strain", "Stretch",
    "Strongest", "Stubborn", "Swear", "Third", "Thundering", "Today",
    "Tomorrow", "Toward", "Troubled", "True", "Trust", "Trusting", "Tumult",
    "Twenty", "Unhappy", "Unshaken", "Untie", "Unwilling", "Valor",
    "Voices", "Wagon", "Wake", "War", "Weigh", "Welcome", "Whatever",
    "Wheeling", "Whenever", "White", "Will", "Wine", "Withdrawn", "Wits",
    "Woman", "Women", "Words", "Worth",
    # further relational / role nouns used vocatively rather than as names
    "Brother", "Brothers", "Captain", "Captains", "Child", "Comrade",
    "Comrades", "Daughter", "Elders", "Fool", "Fools", "Herald", "Heralds",
    "Horseman", "Nurse", "People", "Sons", "Warrior", "Wretch",
}


def book_number(path):
    m = re.search(r"book_(\d+)", path.name)
    return int(m.group(1)) if m else 0


def normalize_token(word):
    """Return a candidate name token, or None.

    Keeps only capitalized words. Single letters are dropped: they are never
    names, and the verse contains stray capitalized initials in no context that
    matters here.
    """
    if not word or not word[0].isupper() or len(word) < 2:
        return None
    return word


def scan():
    """name -> list of "book.line" refs (with duplicates if a name repeats on a line)."""
    refs = defaultdict(list)
    files = sorted(SRC.glob("book_*.txt"), key=book_number)
    if not files:
        sys.exit(f"no translation files found under {SRC}")
    counts, last_line = {}, {}
    for path in files:
        b = book_number(path)
        seen_lines = 0
        rules = 0
        for raw in path.read_text(encoding="utf-8").splitlines():
            if RULE.match(raw):
                rules += 1
                if rules >= 2:
                    break  # end of the verse body
                continue
            if rules < 1 or ABSENT.match(raw):
                continue  # still in the commentary, or an absent-verse placeholder
            m = VERSE.match(raw)
            if not m:
                continue
            line_no, text = m.group(1), m.group(2)
            text = FOOTREF.sub(" ", text)
            seen_lines += 1
            last_line[b] = int(line_no)
            for word in WORD.findall(text):
                tok = normalize_token(word)
                if tok:
                    refs[tok].append(f"{b}.{line_no}")
        counts[b] = seen_lines
    return refs, counts, last_line


def summarize(refs):
    """name -> {count, books, refs} with refs de-duplicated and sorted."""
    def key(ref):
        b, l = ref.split(".")
        return (int(b), int(l))

    out = {}
    for name, rlist in refs.items():
        uniq = sorted(set(rlist), key=key)
        books = sorted({int(r.split(".")[0]) for r in rlist})
        out[name] = {"count": len(rlist), "books": books, "refs": uniq}
    return out


def write_json(data):
    OUT.mkdir(exist_ok=True)
    ordered = dict(sorted(data.items(), key=lambda kv: (-kv[1]["count"], kv[0])))
    (OUT / "occurrences.json").write_text(
        json.dumps(ordered, ensure_ascii=False, indent=2), encoding="utf-8"
    )


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


def write_md(data, min_count):
    candidates = {n: d for n, d in data.items() if n not in STOP}
    dropped = {n: d for n, d in data.items() if n in STOP}

    def rows(items):
        items = sorted(items, key=lambda kv: (-kv[1]["count"], kv[0]))
        lines = ["| name | hits | books |", "| --- | ---: | --- |"]
        for name, d in items:
            lines.append(f"| {name} | {d['count']} | {fmt_books(d['books'])} |")
        return "\n".join(lines)

    shown = [(n, d) for n, d in candidates.items() if d["count"] >= min_count]
    tail = [(n, d) for n, d in candidates.items() if d["count"] < min_count]

    md = []
    md.append("# Name index — Phase 1 occurrence table\n")
    md.append(
        "Generated by `tools/build_index.py` from `translation/`. This is raw "
        "extraction, not an edited index: tokens are single capitalized words, "
        "aliases are NOT yet merged, and no judgment has been applied beyond a "
        "function-word stoplist. Full per-occurrence citations live in "
        "`index/occurrences.json`.\n"
    )
    md.append(f"**{len(candidates)}** candidate names "
              f"(**{len(shown)}** with ≥{min_count} hits). "
              f"**{len(dropped)}** stoplisted tokens hidden below.\n")
    md.append(f"## Candidate names (≥{min_count} occurrences)\n")
    md.append(rows(shown))
    md.append(f"\n## Long tail (< {min_count} occurrences)\n")
    md.append(rows(tail))
    md.append("\n## Stoplisted tokens (dropped as function/relational words)\n")
    md.append(rows(list(dropped.items())))
    (OUT / "occurrences.md").write_text("\n".join(md) + "\n", encoding="utf-8")


# Canonical Iliad line counts (Monro-Allen OCT), used as a scan self-check: if
# the extractor's verse-line count for a book doesn't match, the verse/footnote
# boundary logic has drifted and the occurrence table cannot be trusted.
EXPECTED_LINES = {
    1: 611, 2: 877, 3: 461, 4: 544, 5: 909, 6: 529, 7: 482, 8: 565,
    9: 713, 10: 579, 11: 848, 12: 471, 13: 837, 14: 522, 15: 746,
    16: 867, 17: 761, 18: 617, 19: 424, 20: 503, 21: 611, 22: 515,
    23: 897, 24: 804,
}


# Lines the printed Monro-Allen text does not have, so the translation skips
# their numbers. Each is marked in the verse body by an ABSENT placeholder and
# explained in that book's footnotes. Subtracted before the count check.
KNOWN_GAPS = {9: 4, 11: 1, 14: 1}  # 9.458-461, 11.543, 14.269


def check_counts(counts, last_line):
    """Verify each book's scan against the canonical OCT line numbering.

    Two independent checks: the last line number must equal the book's canonical
    length (catches a truncated or over-run scan), and the number of verse lines
    actually present must equal that length minus the documented gaps (catches
    silently dropped or duplicated lines in the middle).
    """
    bad = []
    for b, expected in sorted(EXPECTED_LINES.items()):
        end = last_line.get(b)
        if end != expected:
            bad.append(f"  book {b}: last verse line is {end}, expected {expected}")
        want = expected - KNOWN_GAPS.get(b, 0)
        got = counts.get(b)
        if got != want:
            gap = f" ({expected} minus {KNOWN_GAPS[b]} absent)" if b in KNOWN_GAPS else ""
            bad.append(f"  book {b}: scanned {got} verse lines, expected {want}{gap}")
    return bad


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--min", type=int, default=3,
                    help="minimum hits to appear in the main table (default 3)")
    args = ap.parse_args(argv)

    refs, counts, last_line = scan()
    data = summarize(refs)
    write_json(data)
    write_md(data, args.min)
    total = sum(d["count"] for d in data.values())
    cands = sum(1 for n in data if n not in STOP)
    print(f"scanned {len(counts)} books, {sum(counts.values())} verse lines")
    print(f"{len(data)} distinct capitalized tokens, {total} total occurrences")
    print(f"{cands} candidate names after stoplist")
    bad = check_counts(counts, last_line)
    if bad:
        print("\n[!] verse-line count mismatch — check the scan boundary:")
        print("\n".join(bad))
    else:
        print("line-count self-check: OK (all 24 books match the OCT numbering)")
    print(f"wrote {OUT/'occurrences.json'} and {OUT/'occurrences.md'}")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
