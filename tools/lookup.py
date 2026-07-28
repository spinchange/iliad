"""Print translated verse lines by reference — the entry-writer's read tool.

Phase 3 entries must be written from what the poem actually says, not from
general knowledge of Homer. This prints any line or range from the verse body of
`translation/book_NN.txt`, so a writer can read a citation before making a claim
about it.

It shares the verse-body boundary logic with `build_index.py`: the body of each
book lies between the file's two horizontal rules, which keeps the translator's
commentary (whose prose cites line numbers) and the footnote apparatus (whose
continuation lines are indented) out of the output. Inline footnote markers are
stripped.

Usage:
    python tools/lookup.py 1.1                 # one line
    python tools/lookup.py 6.390-405           # a range
    python tools/lookup.py 2.101 2.107 16.855  # several at once
    python tools/lookup.py --grep Andromache   # every line containing a word
"""
import argparse
import re
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "translation"

RULE = re.compile(r"^-{20,}\s*$")
VERSE = re.compile(r"^\s*(\d+)\s+(\S.*)$")
FOOTREF = re.compile(r"\[\d+\]")

_cache = {}


def verse(book):
    """{line_number: text} for one book's verse body."""
    if book in _cache:
        return _cache[book]
    path = SRC / f"book_{book:02d}.txt"
    if not path.exists():
        sys.exit(f"no such book: {path}")
    out, rules = {}, 0
    for raw in path.read_text(encoding="utf-8").splitlines():
        if RULE.match(raw):
            rules += 1
            if rules >= 2:
                break
            continue
        if rules < 1:
            continue
        m = VERSE.match(raw)
        if m:
            out[int(m.group(1))] = FOOTREF.sub("", m.group(2)).rstrip()
    _cache[book] = out
    return out


def show(spec):
    if "." not in spec:
        sys.exit(f"bad reference {spec!r} — expected BOOK.LINE or BOOK.START-END")
    b, rest = spec.split(".", 1)
    book = int(b)
    lines = verse(book)
    if "-" in rest:
        a, z = rest.split("-", 1)
        rng = range(int(a), int(z) + 1)
    else:
        rng = [int(rest)]
    for n in rng:
        print(f"{book}.{n}: {lines.get(n, '<no such line — absent or out of range>')}")
    print()


def grep(word):
    pat = re.compile(word, re.IGNORECASE)
    hits = 0
    for book in range(1, 25):
        for n, text in sorted(verse(book).items()):
            if pat.search(text):
                print(f"{book}.{n}: {text}")
                hits += 1
    print(f"\n{hits} lines")


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("refs", nargs="*", help="BOOK.LINE or BOOK.START-END")
    ap.add_argument("--grep", metavar="PATTERN",
                    help="print every verse line matching PATTERN")
    args = ap.parse_args(argv)
    if args.grep:
        grep(args.grep)
    elif args.refs:
        for spec in args.refs:
            show(spec)
    else:
        ap.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
