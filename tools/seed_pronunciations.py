"""Seed index/pronunciations.tsv from the companion Odyssey project.

The two poems share a large cast — roughly two hundred names, from Achilles and
Agamemnon down to walk-on Myrmidons — and the Odyssey project already carries a
hand-checked respelling for each. Those rows are inherited verbatim rather than
re-derived, so a reader of both books never meets the same name said two ways.

This tool is **additive and idempotent**: a headword already present in the Iliad
TSV is never touched, whatever the Odyssey says. It exists to do the mechanical
lift once and then to report, every time it runs, which Iliad headwords still
need a hand-written row — that report is the actual work list.

Usage:
    python tools/seed_pronunciations.py            # report only, writes nothing
    python tools/seed_pronunciations.py --write    # append inherited rows
    python tools/seed_pronunciations.py --todo 5   # list gaps with >=5 hits
"""
import argparse
import json
import re
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

ROOT = Path(__file__).resolve().parent.parent
OCC = ROOT / "index" / "occurrences.json"
TSV = ROOT / "index" / "pronunciations.tsv"
ODYSSEY_TSV = ROOT.parent / "odyssey" / "index" / "pronunciations.tsv"

HEADER = [
    "# Iliad index — anglicized pronunciations. "
    "Format: headword <TAB> say <TAB> variant(optional)",
    "# House style: see index/pron-key.md. CAPS = primary stress; uh = schwa.",
    "# Lines starting with # are ignored. "
    "Transparent English names are intentionally absent.",
    "# Rows marked (od) were inherited from ../odyssey by tools/seed_pronunciations.py.",
]


def read_tsv(path):
    """headword -> (say, variant|None), preserving nothing else."""
    out = {}
    if not path.exists():
        return out
    for raw in path.read_text(encoding="utf-8").splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        parts = raw.rstrip("\n").split("\t")
        hw = parts[0].strip()
        say = parts[1].strip() if len(parts) > 1 else ""
        var = parts[2].strip() if len(parts) > 2 and parts[2].strip() else None
        if hw and say:
            out[hw] = (say, var)
    return out


def load_stop():
    """The Phase 1 stoplist, imported so the two tools cannot drift apart."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("bi", Path(__file__).with_name("build_index.py"))
    bi = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bi)
    return bi.STOP


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true",
                    help="append inherited Odyssey rows to the Iliad TSV")
    ap.add_argument("--todo", type=int, default=10,
                    help="in the gap report, list headwords with >= this many hits")
    args = ap.parse_args(argv)

    if not OCC.exists():
        sys.exit(f"{OCC} not found — run tools/build_index.py first")
    occ = json.loads(OCC.read_text(encoding="utf-8"))
    stop = load_stop()
    cand = {n: d for n, d in occ.items() if n not in stop}

    mine = read_tsv(TSV)
    theirs = read_tsv(ODYSSEY_TSV)
    if not theirs:
        print(f"[!] no Odyssey TSV at {ODYSSEY_TSV} — nothing to inherit")

    inheritable = {n: theirs[n] for n in cand if n in theirs and n not in mine}
    have = set(mine) | set(inheritable)
    gaps = sorted(((d["count"], n) for n, d in cand.items() if n not in have),
                  reverse=True)

    print(f"candidate headwords (post-stoplist): {len(cand)}")
    print(f"rows already in {TSV.name}: {len(mine)}")
    print(f"inheritable from Odyssey: {len(inheritable)}")
    print(f"still needing a hand-written row: {len(gaps)}")
    for th in (20, 10, 5, 3, 2, 1):
        print(f"    with >={th:>2} hits: {sum(1 for c, _ in gaps if c >= th)}")

    if args.write and inheritable:
        lines = []
        if not TSV.exists():
            lines.extend(HEADER)
        for n in sorted(inheritable, key=str.lower):
            say, var = inheritable[n]
            lines.append(f"{n}\t{say}\t{var}" if var else f"{n}\t{say}")
        with TSV.open("a", encoding="utf-8") as fh:
            fh.write("\n".join(lines) + "\n")
        print(f"\nappended {len(inheritable)} inherited rows to {TSV}")
    elif args.write:
        print("\nnothing to inherit — TSV unchanged")
    else:
        print("\n(report only; pass --write to append the inherited rows)")

    shown = [(c, n) for c, n in gaps if c >= args.todo]
    if shown:
        print(f"\nNeeds a respelling — {len(shown)} headwords with >={args.todo} hits:")
        print("  " + ", ".join(f"{n} ({c})" for c, n in shown))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
