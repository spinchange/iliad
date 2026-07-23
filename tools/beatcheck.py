"""Rough beat-proxy (syllable) profile of translation lines.

Loose 5-6 beat line ~ 9-16 syllables. Reports distribution per file and
extremes, using the Odyssey translation as the calibration corpus.
"""
import re
import sys
from pathlib import Path

LINE = re.compile(r"^\s{0,5}(\d+)\s\s(.*)$")
MARKER = re.compile(r"\[\^?L?\d+\]")


def syllables(word):
    w = re.sub(r"[^a-z']", "", word.lower())
    if not w:
        return 0
    n = len(re.findall(r"[aeiouy]+", w))
    if n > 1 and w.endswith("e") and not w.endswith(("le", "ee", "ye", "oe")):
        n -= 1
    if n > 1 and w.endswith("ed") and not w.endswith(("ted", "ded")):
        n -= 1
    return max(1, n)


def line_syllables(text):
    text = MARKER.sub("", text)
    return sum(syllables(w) for w in text.split())


def profile(path):
    rows = []
    for raw in Path(path).read_text(encoding="utf-8").splitlines():
        m = LINE.match(raw)
        if m:
            n = int(m.group(1))
            if any(r[0] == n for r in rows[-3:]) :
                continue
            s = line_syllables(m.group(2))
            if s:
                rows.append((n, s, m.group(2)))
    return rows


def main(paths):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    all_long = []
    for p in paths:
        rows = profile(p)
        if not rows:
            print(f"{p}: no lines")
            continue
        ss = sorted(s for _, s, _ in rows)
        total = len(ss)
        mean = sum(ss) / total
        med = ss[total // 2]
        p5 = ss[int(total * 0.05)]
        p95 = ss[int(total * 0.95)]
        in_band = sum(1 for s in ss if 9 <= s <= 16) / total * 100
        over = sum(1 for s in ss if s >= 17) / total * 100
        under = sum(1 for s in ss if s <= 8) / total * 100
        name = Path(p).name
        print(f"{name}: n={total} mean={mean:.1f} med={med} p5={p5} p95={p95} "
              f"| in 9-16: {in_band:.1f}%  <=8: {under:.1f}%  >=17: {over:.1f}%")
        for n, s, t in rows:
            if s >= 18:
                all_long.append((s, name, n, t))
    if all_long:
        print("\nLongest lines (>=18 syllables):")
        for s, name, n, t in sorted(all_long, reverse=True)[:15]:
            print(f"  {s} syll  {name}:{n}  {t}")


if __name__ == "__main__":
    main(sys.argv[1:])
