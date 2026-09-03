#!/usr/bin/env python3
"""Validate a print PDF against the specification of the edition.

Ported from the Odyssey project's tools/check_print.py. The print build
depends on several undocumented behaviours of calibre's PDF renderer
(margins render at 2x, the font size is scaled, the running head is laid
inside the top margin). Those were established by measurement, and a
calibre upgrade can change them silently — the PDF still builds, it is
just wrong. This checks the finished file against what the edition is
supposed to be, so a drift fails loudly instead of reaching a printer.

Checks:
  * trim size matches the requested one exactly
  * body text renders at the intended point size
  * the text block sits inside the intended margins, on every page
  * no page is overset (text outside the trim, i.e. would be cut off)
  * all fonts are embedded (a printer cannot substitute)
  * no character fell back to another face
  * the running head and folio are clear of the trim tolerance
  * every note marker resolves and every note is cited (from the source)
  * every contents entry points at the page its section opens on

Usage:
    python tools/check_print.py print-build/iliad-print-6x9.pdf
    python tools/check_print.py <file.pdf> --trim 6x9
"""
from __future__ import annotations
import argparse
import re
import sys
from collections import Counter
from pathlib import Path

try:
    import pdfplumber
except ImportError:
    sys.exit("check_print.py needs pdfplumber:  pip install pdfplumber")

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_print import (TRIMS, BODY_PT, BOOK_HEAD, TNOTES_TITLE,  # noqa: E402
                         FURTHER_TITLE, INDEX_TITLE)
from build_web import parse_book, REF_RE  # noqa: E402

TOL_PT = 6.0
TOL_FONT_PT = 0.4
# Printers cut to about +/-3mm. Nothing that must survive — including the
# running head and the folio — may sit closer than this to the trim edge.
TRIM_TOLERANCE_PT = 8.5
# A line-for-line edition tolerates a few long verses running over, but not
# many: past this the one-verse-one-line reading of the page breaks down.
MAX_TURNOVER_PCT = 4.0

SRC = Path(__file__).resolve().parent.parent / "translation"
BACK_LABELS = (TNOTES_TITLE, FURTHER_TITLE, INDEX_TITLE)


def check(path: Path, trim: str) -> int:
    geo = TRIMS[trim]
    want_w, want_h = geo["w"] * 72, geo["h"] * 72
    problems: list[str] = []
    notes: list[str] = []

    with pdfplumber.open(str(path)) as pdf:
        npages = len(pdf.pages)

        w, h = pdf.pages[0].width, pdf.pages[0].height
        if abs(w - want_w) > 1 or abs(h - want_h) > 1:
            problems.append(f"trim is {w/72:.3f}x{h/72:.3f}in, expected "
                            f"{geo['w']}x{geo['h']}in")
        if len({(round(p.width), round(p.height)) for p in pdf.pages}) > 1:
            problems.append("pages are not all the same size")

        # ---- verse font size, measured on verse pages only
        verse_pages = _verse_pages(pdf)
        body_size = BODY_PT
        sizes: Counter = Counter()
        for i in verse_pages[:40]:
            for c in pdf.pages[i].chars:
                if "Gentium" in str(c.get("fontname", "")):
                    sizes[round(c["size"], 1)] += 1
        if not verse_pages:
            problems.append("found no verse pages to measure")
        elif sizes:
            body_size = sizes.most_common(1)[0][0]
            if abs(body_size - BODY_PT) > TOL_FONT_PT:
                problems.append(f"verse renders at {body_size}pt, expected "
                                f"{BODY_PT}pt (calibre's font scaling may have changed)")
            else:
                notes.append(f"verse {body_size}pt over {len(verse_pages)} verse pages")

        # ---- embedded fonts (only the ones that draw glyphs)
        drawn: set[str] = set()
        for p in pdf.pages[:50]:
            for c in p.chars:
                fn = str(c.get("fontname", "")).strip("/'\"")
                if fn:
                    drawn.add(fn)
        not_embedded: set[str] = set()
        seen_fonts: set[str] = set()
        for p in pdf.pages[:50]:
            for name, is_embedded in _fonts(p).items():
                clean = name.strip("/'\"")
                if clean not in drawn:
                    continue
                seen_fonts.add(clean)
                if not is_embedded:
                    not_embedded.add(clean)
        if seen_fonts:
            notes.append((f"fonts (all embedded): " if not not_embedded else "fonts: ")
                         + ", ".join(sorted(seen_fonts)))
        if not_embedded:
            problems.append("fonts not embedded (a printer will substitute): "
                            + ", ".join(sorted(not_embedded)))

        strays: Counter = Counter()
        for p in pdf.pages:
            for c in p.chars:
                fn = str(c.get("fontname", ""))
                if "Gentium" not in fn and "Georgia" not in fn:
                    strays[(c["text"], fn.split("+")[-1])] += 1
        if strays:
            shown = ", ".join(f"{t!r} (U+{ord(t):04X}) in {f}"
                              for (t, f), _ in strays.most_common(4))
            problems.append(f"{sum(strays.values())} character(s) fell back to "
                            f"another face — missing from the subsetted font: {shown}")

        # ---- margins and overset, per page
        min_left = min_right = 1e9
        min_top = min_bottom = 1e9
        min_top_any = min_bottom_any = 1e9
        blanks: list[int] = []
        overset: list[int] = []
        for i, p in enumerate(pdf.pages, start=1):
            cs = p.chars
            if not cs:
                blanks.append(i)
                continue
            left = min(c["x0"] for c in cs)
            right = w - max(c["x1"] for c in cs)
            min_left = min(min_left, left)
            min_right = min(min_right, right)
            min_top_any = min(min_top_any, min(c["top"] for c in cs))
            min_bottom_any = min(min_bottom_any, h - max(c["bottom"] for c in cs))
            body_chars = [c for c in cs if "Gentium" in str(c.get("fontname", ""))]
            if body_chars:
                min_top = min(min_top, min(c["top"] for c in body_chars))
                min_bottom = min(min_bottom, h - max(c["bottom"] for c in body_chars))
            if left < 0 or right < 0 or min(c["top"] for c in cs) < 0 or \
                    h - max(c["bottom"] for c in cs) < 0:
                overset.append(i)
        if overset:
            problems.append(f"{len(overset)} page(s) have text outside the trim "
                            f"and would be cut off: {_brief(overset)}")
        floor = min(geo["inner"], geo["outer"])
        for label, got in (("left", min_left), ("right", min_right)):
            if got < floor - TOL_PT:
                problems.append(f"{label} margin falls to {got:.1f}pt, below the "
                                f"{floor}pt design minimum")
        for label, got, want in (("top", min_top, geo["top"]),
                                 ("bottom", min_bottom, geo["bottom"])):
            if got < want - TOL_PT:
                problems.append(f"{label} body margin is {got:.1f}pt, below the "
                                f"{want}pt design minimum")
        for label, got in (("top", min_top_any), ("bottom", min_bottom_any)):
            if got < TRIM_TOLERANCE_PT:
                problems.append(f"running head/folio is {got:.1f}pt from the {label} "
                                f"trim edge, inside the {TRIM_TOLERANCE_PT}pt cutting tolerance")
        notes.append(f"body block: left>={min_left:.0f} right>={min_right:.0f} "
                     f"top>={min_top:.0f} bottom>={min_bottom:.0f} pt")
        notes.append(f"head/folio clearance: top {min_top_any:.0f}pt, "
                     f"bottom {min_bottom_any:.0f}pt from trim")
        if blanks:
            notes.append(f"{len(blanks)} blank page(s): {_brief(blanks)}")

        # ---- verse turnover
        if verse_pages:
            cpl = _chars_per_line(pdf, verse_pages, body_size)
            if cpl:
                rate = _turnover_rate(cpl)
                notes.append(f"verse measure ~{cpl:.0f} chars/line; "
                             f"{rate:.1f}% of the poem's verses turn over")
                if rate > MAX_TURNOVER_PCT:
                    problems.append(f"{rate:.1f}% of verses would turn over (limit "
                                    f"{MAX_TURNOVER_PCT}%): the measure is too narrow")

    note_problems = _check_notes()
    problems.extend(note_problems)
    if not note_problems:
        notes.append("every note resolves to exactly one marker")

    toc_problems, toc_n = _check_contents(path)
    problems.extend(toc_problems)
    if toc_n and not toc_problems:
        notes.append(f"contents: all {toc_n} page number(s) correct")

    print(f"{path.name}: {npages} pages, {trim} trim")
    for n in notes:
        print(f"  - {n}")
    if problems:
        print("\nFAIL")
        for pr in problems:
            print(f"  * {pr}")
        return 1
    print("\nOK — matches the print specification")
    return 0


def _check_notes() -> list[str]:
    """Every marker must resolve to a note and every note must be cited.
    Checked against the source: the parser raises on a marker without a
    note and reports a note nobody cites; a merged note ('[18] - merged
    into [17]') is the one legitimate alias."""
    out: list[str] = []
    for f in sorted(SRC.glob("book_*.txt")):
        try:
            bk = parse_book(f)
        except SystemExit as e:
            out.append(str(e))
            continue
        cited = Counter(int(x) for st in bk["stanzas"] for it in st
                        if it[0] == "v" for x in REF_RE.findall(it[2]))
        defined = {nt["num"] for nt in bk["notes"]}
        missing = sorted(n for n in cited if n not in defined and n not in bk["alias"])
        if missing:
            out.append(f"{f.name}: marker with no note text: {missing[:5]}")
        # A note cited from two lines (Book 17 has three: a note on a
        # simile family, a sequence, a message chain) prints its numeral
        # twice, which is what the source intends; it is reported, not failed.
        dupes = sorted(n for n, k in cited.items() if k > 1 and n not in bk["alias"].values())
        if dupes:
            print(f"  note: {f.name}: note(s) cited from more than one line: {dupes}")
    return out


def _check_contents(path: Path) -> tuple[list[str], int]:
    """Does every arabic folio on the contents page point at the page its
    section really opens on? The front-matter row carries a roman numeral
    and is not checked."""
    try:
        from pypdf import PdfReader
    except ImportError:
        return [], 0
    reader = PdfReader(str(path))
    labels = "|".join([r"Book\s+\d+"] + [re.escape(x) for x in BACK_LABELS])
    toc: dict[str, int] = {}
    started = False
    for page in reader.pages:
        t = page.extract_text() or ""
        if not started:
            if "CONTENTS" not in t.upper()[:200] or "Book" not in t:
                continue
            started = True
        elif re.search(rf"{BOOK_HEAD}\s*[—–-]\s*Book\s+\d+", t, re.I):
            break          # the poem has begun; the contents is behind us
        rows = list(re.finditer(rf"({labels})(.*?)(\d+)[ \t]*(?:\n|$)", t, re.S))
        if not rows:
            break
        for m in rows:
            toc[re.sub(r"\s+", " ", m.group(1)).strip()] = int(m.group(3))
    if not toc:
        return [], 0

    def printed_folio(page) -> int | None:
        for ln in reversed((page.extract_text() or "").strip().split("\n")):
            s = ln.strip()
            if s.isdigit():
                return int(s)
        return None

    actual: dict[str, int] = {}
    for page in reader.pages:
        t = (page.extract_text() or "").strip()
        if not t:
            continue
        lines = [x.strip() for x in t.split("\n") if x.strip()]
        for ln in lines[1:3]:
            m = re.match(rf"{BOOK_HEAD}\s*[—–-]\s*Book\s+(\d+)\s*$", ln)
            if m:
                actual.setdefault(f"Book {int(m.group(1))}", printed_folio(page) or -1)
                break
        for ln in lines[:3]:
            for label in BACK_LABELS:
                if re.sub(r"\s+", " ", ln).upper() == label.upper():
                    actual.setdefault(label, printed_folio(page) or -1)

    out: list[str] = []
    wrong = [(k, v, actual.get(k)) for k, v in toc.items() if actual.get(k) != v]
    if wrong:
        detail = "; ".join(f"{k} says {v}, actually {a}" for k, v, a in wrong[:4])
        out.append(f"{len(wrong)} contents entry/entries point at the wrong page: {detail}")
    missing = [k for k in actual if k not in toc]
    if missing:
        out.append(f"{len(missing)} section(s) missing from the contents: "
                   + ", ".join(sorted(missing)[:6]))
    return out, len(toc)


def _verse_pages(pdf) -> list[int]:
    """Pages carrying verse: the running head names a book, the page is set
    in Gentium at body size, and it carries the hanging line numbers."""
    out = []
    for i, p in enumerate(pdf.pages):
        txt = (p.extract_text() or "").strip()
        if not txt:
            continue
        head = txt.split("\n")[0]
        if not re.match(rf"\s*{BOOK_HEAD.upper()}\s*[—–-]\s*BOOK", head, re.I):
            continue
        gent = [c for c in p.chars if "Gentium" in str(c.get("fontname", ""))]
        if len(gent) < 300:
            continue
        sizes = {round(c["size"], 1) for c in gent}
        if any(s < BODY_PT - 1.5 for s in sizes):
            out.append(i)
    return out


def _chars_per_line(pdf, verse_pages: list[int], body: float) -> float:
    lefts: Counter = Counter()
    rights: Counter = Counter()
    widths: list[tuple[float, int]] = []
    for i in verse_pages[:40]:
        main = [c for c in pdf.pages[i].chars
                if "Gentium" in str(c.get("fontname", ""))
                and abs(round(c["size"], 1) - body) < 0.3]
        rows: dict[int, list] = {}
        for c in main:
            rows.setdefault(round(c["top"]), []).append(c)
        for cs in rows.values():
            x0 = min(c["x0"] for c in cs)
            x1 = max(c["x1"] for c in cs)
            lefts[round(x0)] += 1
            rights[round(x1)] += 1
            widths.append((x1 - x0, len(cs)))
    if not lefts or not widths:
        return 0.0
    block = max(rights) - lefts.most_common(1)[0][0]
    full = [(w, n) for w, n in widths if w > block * 0.7 and n > 20]
    if not full:
        return 0.0
    adv = sum(w for w, n in full) / sum(n for w, n in full)
    return block / adv if adv else 0.0


def _turnover_rate(cpl: float) -> float:
    """Percentage of the poem's verses longer than cpl characters."""
    lens: list[int] = []
    for f in sorted(SRC.glob("book_*.txt")):
        bk = parse_book(f)
        for st in bk["stanzas"]:
            for it in st:
                if it[0] == "v":
                    lens.append(len(REF_RE.sub("", it[2])))
    if not lens:
        return 0.0
    return 100.0 * sum(1 for x in lens if x > cpl) / len(lens)


def _fonts(page) -> dict:
    from pdfminer.pdftypes import resolve1
    out: dict[str, bool] = {}
    res = resolve1(page.page_obj.resources) or {}
    fdict = resolve1(res.get("Font")) or {}
    for _k, ref in fdict.items():
        f = resolve1(ref)
        if not isinstance(f, dict):
            continue
        base = str(f.get("BaseFont", "?")).lstrip("/")
        desc = resolve1(f.get("FontDescriptor"))
        if desc is None:
            df = resolve1(f.get("DescendantFonts"))
            if df:
                desc = resolve1(resolve1(df[0]).get("FontDescriptor"))
        embedded = False
        if isinstance(desc, dict):
            embedded = any(x in desc for x in ("FontFile", "FontFile2", "FontFile3"))
        out[base] = embedded
    return out


def _brief(nums: list[int], limit: int = 8) -> str:
    if len(nums) <= limit:
        return ", ".join(map(str, nums))
    return ", ".join(map(str, nums[:limit])) + f", … (+{len(nums)-limit})"


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf", type=Path)
    ap.add_argument("--trim", default=None, choices=sorted(TRIMS))
    args = ap.parse_args()
    t = args.trim
    if t is None:
        for k in sorted(TRIMS, key=len, reverse=True):
            if k.replace(".", "-") in args.pdf.name:
                t = k
                break
        if t is None:
            t = "6x9"
            print(f"note: could not infer the trim from {args.pdf.name!r}; "
                  "checking against 6x9. Pass --trim to be explicit.")
    sys.exit(check(args.pdf, t))
