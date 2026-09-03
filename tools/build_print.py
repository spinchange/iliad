#!/usr/bin/env python3
"""Build a press-ready PDF interior of the Iliad translation.

Ported from the Odyssey project's tools/build_print.py. This is a *print*
build, not the EPUB re-flowed. What print needs that the EPUB does not:

  - A fixed trim size and a measure chosen so that verse lines rarely
    turn over (the reader cannot change the font size on paper).
  - Line numbers every 5th verse, not every verse.
  - Turnover indents: a verse longer than the measure continues indented
    so it still reads as one verse.
  - No hyperlinks, no return arrows. A note marker is a printed numeral.
  - Recto-forcing: each book opens on a right-hand page, with a blank
    verso inserted when needed.
  - A centered running head, and folios mirrored to the outside edge:
    bottom-left on a verso, bottom-right on a recto.
  - Black ink only: POD colour interiors cost several times mono.
  - Dictionary-style guide words on the index pages: the running head
    names the first and last entry beginning on that page.

The book's shape follows the EPUB: title page, copyright, the proem
epigraph, the General Introduction, a note on the text, the contents; the
twenty-four books, each with its argument, its verse, and its endnotes;
then the translator's notes on the books, For Further Reading, and the
index of names. The source parser is shared with tools/build_web.py.

Pipeline: translation/book_NN.txt -> one print HTML -> EPUB -> PDF
(calibre). translation/ is never modified. The EPUB intermediate exists
because calibre's html input path drops the per-file structure that gives
us running heads; the epub path keeps it.

Usage:
    python tools/build_print.py                  # all 24 books, 6x9
    python tools/build_print.py --books 1        # Book 1 only (proof)
    python tools/build_print.py --trim 5.5x8.5   # other trim sizes
    python tools/build_print.py --trim a5
"""
from __future__ import annotations
import argparse
import html
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_web import (parse_book, paragraphs, REF_RE, HEAD_RE,  # noqa: E402
                       INTRO, FURTHER, IDX)

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "translation"
BUILD = ROOT / "print-build"
WORK = BUILD / "work"
EPUB_ASSETS = ROOT / "epub-build" / "assets"

EBOOK_CONVERT = (
    os.environ.get("EBOOK_CONVERT")
    or shutil.which("ebook-convert")
    or r"C:\Program Files\Calibre2\ebook-convert.exe"
)

TITLE = "The Iliad"
BOOK_HEAD = "Iliad"           # the h1 reads "Iliad — Book N"
TNOTES_TITLE = "The Translator\u2019s Notes on the Books"
FURTHER_TITLE = "For Further Reading"
INDEX_TITLE = "Index of Names and Places"
INTRO_TITLE = "General Introduction"

# ---------------------------------------------------------------- trim sizes
# width x height in inches, plus the margins for that size in points.
# `inner` is the binding edge; calibre cannot mirror per page, so `inner`
# is applied to both sides and the value is chosen to be safe as a gutter
# on either edge. The horizontal margins are set by the verse: this is a
# line-for-line edition, and the measure has to hold nearly every verse on
# one line. tools/check_print.py re-measures the turnover rate.
TRIMS = {
    "6x9":     dict(w=6.0,  h=9.0,   inner=56, outer=38, top=58, bottom=64),
    "5.5x8.5": dict(w=5.5,  h=8.5,   inner=54, outer=38, top=54, bottom=60),
    "a5":      dict(w=5.83, h=8.27,  inner=56, outer=40, top=54, bottom=60),
}

# calibre's margin handling in the epub->pdf path, established by measuring
# the rendered output rather than from the docs (see the Odyssey builder for
# the measurements). tools/check_print.py fails the build if it drifts.
CALIBRE_MARGIN_FACTOR = 2
HEAD_ALLOWANCE_PT = 60
HEAD_PAD_PT = 24

# The body size of the printed edition, in points. calibre's PDF renderer
# applies a constant 0.75 to --pdf-default-font-size, which takes an
# INTEGER, so only multiples of 0.75 are reachable: 10.5pt is 14.
BODY_PT = 10.5
CALIBRE_FONT_SCALE = 0.75
BASE_FONT_REQUEST = round(BODY_PT / CALIBRE_FONT_SCALE)   # 10.5pt -> 14

# Number every Nth verse line in the printed margin.
NUMBER_EVERY = 5

# Characters the source uses that the subsetted Gentium does not carry.
# Left alone they fall back to a sans face, so each is mapped to a glyph
# the font does have.
GLYPH_SUBSTITUTIONS = {
    "ʼ": "᾽",   # MODIFIER LETTER APOSTROPHE -> GREEK KORONIS
    "→": "–",   # RIGHTWARDS ARROW -> EN DASH
    "≈": "c. ",  # ALMOST EQUAL TO -> "c." (circa)
}


def substitute_glyphs(text: str) -> str:
    for src, dst in GLYPH_SUBSTITUTIONS.items():
        text = text.replace(src, dst)
    return text


def esc(text: str) -> str:
    return html.escape(text, quote=False)


def md_inline(text: str) -> str:
    """The inline markdown the index uses (*em*, **bold**), escaped first."""
    out = html.escape(text, quote=False)
    out = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", out)
    out = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", out)
    return out


# ---------------------------------------------------------------- the books


def render_verse(lineno: int, text: str, alias: dict[int, int]) -> str:
    """One verse line: hanging number (every Nth), markers, turnover indent."""
    def _ref(m: re.Match) -> str:
        i = int(m.group(1))
        return f'<sup class="nm">{alias.get(i, i)}</sup>'
    body = REF_RE.sub(_ref, esc(text))
    shown = str(lineno) if lineno % NUMBER_EVERY == 0 else ""
    return f'<p class="v"><span class="ln">{shown}</span>{body}</p>'


def note_where(nt: dict) -> str:
    """'l. 337' or 'll. 590–594' from the note's own citation."""
    if nt["line"] is None:
        return ""
    span = nt["span"].replace("-", "\u2013")
    return f"ll.&nbsp;{nt['line']}{esc(span)}" if span else f"l.&nbsp;{nt['line']}"


def render_book(bk: dict) -> str:
    n = bk["n"]
    parts: list[str] = []
    # Book opener. The h1 text drives the running head via _SECTION_.
    parts.append(f"<h1>{BOOK_HEAD} \u2014 Book {n}</h1>")
    if bk["argument"]:
        parts.append(f'<p class="argument">{esc(bk["argument"])}</p>')

    parts.append('<div class="stanza">')
    for stanza in bk["stanzas"]:
        for item in stanza:
            if item[0] == "absent":
                parts.append(f'<p class="absent">{esc(item[1])}</p>')
            else:
                parts.append(render_verse(item[1], item[2], bk["alias"]))
    parts.append("</div>")

    # Endnotes for this book, under the source's own numbering (which runs
    # 1..N in order of appearance; a merged note points at its survivor).
    if bk["notes"]:
        parts.append(f'<h2 class="notes-head">Notes to Book {n}</h2>')
        for nt in bk["notes"]:
            where = note_where(nt)
            parts.append(
                f'<p class="note"><span class="nl">{nt["num"]}</span>'
                + (f"<em>{where}</em>&nbsp; " if where else "")
                + f'{esc(nt["body"])}</p>')
    return "\n".join(parts)


# ---------------------------------------------------------------- contents


def roman(n: int) -> str:
    """Lower-case roman numeral, for the front-matter folios in the contents."""
    out = ""
    for value, glyph in ((1000, "m"), (900, "cm"), (500, "d"), (400, "cd"),
                         (100, "c"), (90, "xc"), (50, "l"), (40, "xl"),
                         (10, "x"), (9, "ix"), (5, "v"), (4, "iv"), (1, "i")):
        while n >= value:
            out += glyph
            n -= value
    return out


def contents_page(book_nums: list[int], arguments: dict[int, str],
                  folios: dict[int, int] | None,
                  back: list[tuple[str, int | None]] | None = None,
                  front: list[tuple[str, str | None]] | None = None) -> str:
    """The table of contents.

    Folios are only known after a render, so the first pass is built with
    them absent: the layout is identical either way, so the page count does
    not change when the numbers are filled in on the second pass."""
    rows: list[str] = []
    for label, folio in (front or []):
        rows.append(
            '<p class="toc-line toc-front">'
            f'<span class="toc-bk">{esc(label)}</span>'
            '<span class="toc-arg"></span>'
            '<span class="toc-dots"></span>'
            f'<span class="toc-pg">{folio if folio else ""}</span>'
            "</p>")
    for n in book_nums:
        arg = arguments.get(n, "")
        folio = folios.get(n) if folios else None
        rows.append(
            '<p class="toc-line">'
            f'<span class="toc-bk">Book {n}</span>'
            f'<span class="toc-arg">{esc(arg)}</span>'
            '<span class="toc-dots"></span>'
            f'<span class="toc-pg">{folio if folio else ""}</span>'
            "</p>")
    for i, (label, folio) in enumerate(back or []):
        first = " toc-back-first" if i == 0 else ""
        rows.append(
            f'<p class="toc-line toc-back{first}">'
            f'<span class="toc-bk">{esc(label)}</span>'
            '<span class="toc-arg"></span>'
            '<span class="toc-dots"></span>'
            f'<span class="toc-pg">{folio if folio else ""}</span>'
            "</p>")
    return ('<h1 class="fm">Contents</h1>\n<div class="toc">\n'
            + "\n".join(rows) + "\n</div>")


# ---------------------------------------------------------------- front matter


def front_matter() -> list[str]:
    title = (
        '<div class="titlepage">'
        '<p class="tp-title">The Iliad</p>'
        '<p class="tp-sub">a line-for-line translation</p>'
        '<hr class="tp-rule"/>'
        '<p class="tp-role">from the Greek of</p>'
        '<p class="tp-name">Homer</p>'
        '<p class="tp-role">translated by</p>'
        '<p class="tp-name">Claude <span class="tp-small">(Fable 5)</span></p>'
        '<p class="tp-role">edited and produced by</p>'
        '<p class="tp-name">Chris Duffy</p>'
        "</div>"
    )
    copyright_html = (
        '<div class="copyright-page">'
        "<p>The English translation \u2014 the 15,687 verse lines \u2014 is "
        "dedicated to the public domain under Creative Commons CC0 1.0. No "
        "permission is needed to copy, adapt, perform, or reuse it, for any "
        "purpose, including commercially.</p>"
        "<p>The apparatus \u2014 the notes, the translator\u2019s commentary, "
        "the introduction, the guide to further reading, and the index of "
        "names and places \u2014 is &#169; 2026 Chris Duffy, licensed "
        "Creative Commons CC BY 4.0.</p>"
        "<p>The Greek underlying this translation is the Oxford Classical "
        "Text of D.&#160;B. Monro and T.&#160;W. Allen (<em>Homeri Opera</em>, "
        "3rd edition, 1920), in the public domain.</p>"
        "<p>Polytonic Greek is set in Gentium Plus, used under the SIL Open "
        "Font License.</p>"
        "<p>The text of this edition, in digital form, is at "
        "wrath-sing-goddess.com.</p>"
        "</div>"
    )
    epigraph = (
        '<div class="epigraph-page"><p class="epigraph">'
        '<span class="greek" lang="grc">'
        "\u03bc\u1fc6\u03bd\u03b9\u03bd \u1f04\u03b5\u03b9\u03b4\u03b5 "
        "\u03b8\u03b5\u1f70 \u03a0\u03b7\u03bb\u03b7\u03ca\u03ac\u03b4\u03b5\u03c9 "
        "\u1f08\u03c7\u03b9\u03bb\u1fc6\u03bf\u03c2"
        "</span>"
        "Sing, goddess, the wrath of Peleus\u2019 son Achilles"
        "</p></div>"
    )
    note = (
        f'<h1 class="fm">A Note on the Text</h1>'
        '<p class="fm">The Greek is the Oxford Classical Text of Monro and '
        "Allen (3rd edition, 1920). The English translation is original to "
        "this project; each of its 15,687 lines is keyed one-to-one to its "
        "Greek line, so a citation to the Greek finds the same line here. "
        "The printed text is followed throughout, including the passages "
        "ancient critics athetized, which are kept and noted rather than "
        "acted on.</p>"
        '<p class="fm">Three passages the printed Greek lacks '
        "(9.458\u2013461, 11.543, 14.269) are marked in place rather than "
        "supplied, and the numbering skips them.</p>"
        '<p class="fm">Line numbers are printed in the margin every fifth '
        "line. Where a verse runs past the measure of the page, the "
        "continuation is indented, so an indented line is always the tail of "
        "the verse above it and never a new verse.</p>"
        '<p class="fm">The scholarly apparatus \u2014 829 notes across the '
        "poem \u2014 is printed as endnotes at the close of each book. A "
        "raised numeral in the verse marks a note; the notes are numbered "
        "through each book, and each note also gives the line it belongs to "
        "(<em>l.&#160;337</em>), which is how it should be cited. The "
        "translator\u2019s notes on the several books are collected at the "
        "back, before the guide to further reading and the index.</p>"
    )
    return [title, copyright_html, epigraph, introduction_html(), note]


def introduction_html() -> str:
    """translation/introduction.txt as front matter, its five section heads
    promoted to headings."""
    if not INTRO.exists():
        return ""
    lines = INTRO.read_text(encoding="utf-8").splitlines()
    for i, ln in enumerate(lines):
        if ln.strip() == "GENERAL INTRODUCTION":
            lines = lines[i + 1:]
            break
    out = [f'<h1 class="fm">{INTRO_TITLE}</h1>']
    for para in paragraphs(lines):
        m = re.match(r"^([IVX]+)\.\s+([A-Z][A-Z ]+)$", para)
        if m:
            out.append(f'<h2 class="bm"><span class="num">{m.group(1)}.</span>'
                       f'{esc(m.group(2).title())}</h2>')
        else:
            out.append(f'<p class="fm">{esc(para)}</p>')
    return "\n".join(out)


# ---------------------------------------------------------------- back matter


def tnotes_html(books: dict[int, dict]) -> str:
    out = [f'<h1 class="fm">{esc(TNOTES_TITLE)}</h1>',
           '<p class="fm lede">The note on each book, collected here so the '
           "poem itself reads clean.</p>"]
    for n in sorted(books):
        if not books[n]["commentary"]:
            continue
        out.append(f'<h2 class="bm">Book {n}</h2>')
        for para in books[n]["commentary"]:
            out.append(f'<p class="fm">{esc(para)}</p>')
    return "\n".join(out)


def further_reading_html() -> str:
    """further_reading.txt: section heads, entries (a ' · ' title line that
    may wrap, then an indented body), and plain prose."""
    if not FURTHER.exists():
        return ""
    text = FURTHER.read_text(encoding="utf-8")
    paras = [p.splitlines() for p in re.split(r"\n\s*\n", text) if p.strip()]
    if paras and paras[0][0].strip() == "FOR FURTHER READING":
        paras = paras[1:]
    out = [f'<h1 class="fm">{esc(FURTHER_TITLE)}</h1>']
    if paras and paras[0][0].strip().lower().startswith("the iliad"):
        out.append(f'<p class="fm lede"><em>{esc(paras[0][0].strip())}</em></p>')
        paras = paras[1:]
    for para in paras:
        first = para[0]
        if len(para) == 1 and HEAD_RE.match(first.strip()):
            m = re.match(r"^([IVX]+)\.\s+(.*)$", first.strip())
            if m:
                out.append(f'<h2 class="bm"><span class="num">{m.group(1)}.</span>'
                           f'{esc(m.group(2).title())}</h2>')
            else:
                out.append(f'<h2 class="bm">{esc(first.strip().title())}</h2>')
        elif " \u00b7 " in first and not first.startswith(" "):
            i = 0
            while i < len(para) and not para[i].startswith(" "):
                i += 1
            title = " ".join(l.strip() for l in para[:i])
            body = " ".join(l.strip() for l in para[i:])
            out.append(f'<p class="fr-title">{esc(title)}</p>')
            if body:
                out.append(f'<p class="fr-body">{esc(body)}</p>')
        else:
            out.append(f'<p class="fm">{esc(" ".join(l.strip() for l in para))}</p>')
    return "\n".join(out)


# A headword line: "**Abantes** (Ἄβαντες) · PEOPLE — ..." ("**Refs:**" lines
# are bold too, hence the lookahead).
HEADWORD_RE = re.compile(r"^\*\*(?!Refs:)([^*]+)\*\*\s+[(·]")
GUIDE_SEP = " \u2013 "


def index_html(guides: dict[str, str] | None = None) -> str:
    """The index of names as print back matter. Citations stay as printed
    references. `guides` maps a headword to the guide words of the page that
    entry opens; the marker is a zero-size span whose text calibre's chapter
    detection turns into that page's running head."""
    if not IDX.exists():
        return ""
    text = IDX.read_text(encoding="utf-8")
    text = re.sub(r"^# .*\n", "", text, count=1)
    text = re.sub(r"^\s*Every named person.*?pronunciation scheme\.\s*\n",
                  "", text, count=1, flags=re.S)
    out = [
        f'<h1 class="fm">{esc(INDEX_TITLE)}</h1>',
        '<p class="fm">The poem\u2019s principal persons, gods, peoples, and '
        "places \u2014 every figure of consequence \u2014 with a pronunciation "
        "(<em>Say:</em>), epithets, aliases, kin, and line citations. "
        "Pronunciations give the traditional anglicized reading; stress falls "
        "on the capitalized syllable. The several hundred men named once and "
        "killed in the same breath are catalogued for a later edition.</p>",
        '<div class="name-index">',
    ]
    guides = guides or {}
    for raw in text.splitlines():
        s = raw.strip()
        if not s or s == "---":
            continue
        m = HEADWORD_RE.match(s)
        if m:
            guide = guides.get(m.group(1))
            marker = (f'<span class="guide">{esc(guide)}</span>' if guide else "")
            out.append(f'<p class="hw">{marker}{md_inline(s)}</p>')
            continue
        if s.startswith("**Refs:**"):
            cls = "refs"
        elif s.startswith("*See also:*"):
            cls = "xref"
        elif s.startswith("*"):
            cls = "meta"          # Epithets, Also called, Kin, Kills, Killed by
        else:
            cls = "desc"
        out.append(f'<p class="{cls}">{md_inline(s)}</p>')
    out.append("</div>")
    return "\n".join(out)


def _index_headwords() -> list[str]:
    if not IDX.exists():
        return []
    return [m.group(1) for ln in IDX.read_text(encoding="utf-8").splitlines()
            if (m := HEADWORD_RE.match(ln.strip()))]


# ---------------------------------------------------------------- measuring


def _pdf_pages(pdf_path: Path):
    from pypdf import PdfReader
    return PdfReader(str(pdf_path)).pages


def _heading_page(pdf_path: Path, heading: str) -> int | None:
    """1-based page on which a front/back-matter chapter opens: the first
    page whose leading lines carry the heading (set in caps)."""
    try:
        pages = _pdf_pages(pdf_path)
    except ImportError:
        return None
    want = heading.upper()
    for i, page in enumerate(pages, start=1):
        text = (page.extract_text() or "").strip()
        if not text:
            continue
        lines = [x.strip() for x in text.split("\n") if x.strip()][:3]
        # the opener carries the heading as its h1 (second line, after the
        # running head, or first when the head is the same text)
        if any(re.sub(r"\s+", " ", ln).upper() == want for ln in lines):
            return i
    return None


def _book_opener_pages(pdf_path: Path) -> dict[int, int]:
    """Which 1-based page does each book open on?"""
    try:
        pages = _pdf_pages(pdf_path)
    except ImportError:
        return {}
    found: dict[int, int] = {}
    for i, page in enumerate(pages, start=1):
        text = page.extract_text() or ""
        lines = [ln.strip() for ln in text.split("\n") if ln.strip()]
        for ln in lines[1:3]:
            m = re.match(rf"{BOOK_HEAD}\s*[\u2014\u2013-]\s*Book\s+(\d+)\s*$", ln)
            if m:
                found.setdefault(int(m.group(1)), i)
                break
    return found


def _index_guides(pdf_path: Path, headwords: list[str]) -> dict[str, str]:
    """Guide words for the index pages, measured from the rendered PDF."""
    start = _heading_page(pdf_path, INDEX_TITLE)
    if not start:
        return {}
    pages = _pdf_pages(pdf_path)
    guides: dict[str, str] = {}
    pos = 0
    orphan_pages = 0
    for i in range(start - 1, len(pages)):
        text = pages[i].extract_text() or ""
        found: list[str] = []
        for ln in text.split("\n"):
            if pos >= len(headwords):
                break
            if re.match(re.escape(headwords[pos]) + r"\s+[(·]", ln.strip()):
                found.append(headwords[pos])
                pos += 1
        if i == start - 1:
            continue
        if not found:
            orphan_pages += 1
            continue
        first, last = found[0], found[-1]
        guides[first] = first if first == last else f"{first}{GUIDE_SEP}{last}"
    if pos != len(headwords):
        print(f"  WARNING: index guide words: matched {pos} of "
              f"{len(headwords)} headwords in the rendered index")
    if orphan_pages:
        print(f"  WARNING: {orphan_pages} index page(s) on which no entry "
              "begins carry the previous page's guide words")
    return guides


def _strip_outline(pdf_path: Path, titles: set[str]) -> int:
    """Drop the outline entries whose title is in `titles` (the guide-word
    markers reach the running head by way of calibre's TOC, which is also
    written into the PDF outline)."""
    try:
        from pypdf import PdfReader, PdfWriter
        from pypdf.generic import NameObject, NumberObject
    except ImportError:
        return 0
    reader = PdfReader(str(pdf_path))
    writer = PdfWriter(clone_from=reader)
    root = writer._root_object
    if "/Outlines" not in root:
        return 0
    outlines = root["/Outlines"].get_object()
    removed = 0
    node = outlines.get("/First")
    while node is not None:
        item = node.get_object()
        nxt = item.get("/Next")
        if str(item.get("/Title", "")) in titles:
            prev = item.get("/Prev")
            if prev is not None:
                pv = prev.get_object()
                if nxt is not None:
                    pv[NameObject("/Next")] = nxt
                else:
                    del pv["/Next"]
            elif nxt is not None:
                outlines[NameObject("/First")] = nxt
            else:
                del outlines["/First"]
            if nxt is not None:
                nx = nxt.get_object()
                if prev is not None:
                    nx[NameObject("/Prev")] = prev
                else:
                    del nx["/Prev"]
            elif prev is not None:
                outlines[NameObject("/Last")] = prev
            else:
                del outlines["/Last"]
            removed += 1
        node = nxt
    if removed:
        count = int(outlines.get("/Count", 0))
        if count > 0:
            outlines[NameObject("/Count")] = NumberObject(count - removed)
        with open(pdf_path, "wb") as fh:
            writer.write(fh)
    return removed


def _find_blank_leaves(pdf_path: Path) -> set[int]:
    """0-based indices of the blank leaves inserted by the recto pass: pages
    whose only text is the running head and folio."""
    try:
        pages = _pdf_pages(pdf_path)
    except ImportError:
        return set()
    out: set[int] = set()
    for i, page in enumerate(pages):
        text = (page.extract_text() or "").strip()
        letters = [c for c in text if c.isalpha()]
        if letters and all(c.isupper() for c in letters) and len(text) < 80:
            out.add(i)
    return out


def _clear_running_heads(pdf_path: Path, pages: set[int]) -> int:
    """Empty the per-page /HeaderFooter form on the given 0-based pages."""
    try:
        from pypdf import PdfReader, PdfWriter
    except ImportError:
        return 0
    reader = PdfReader(str(pdf_path))
    cleared = 0
    for i, page in enumerate(reader.pages):
        if i not in pages:
            continue
        res = page.get("/Resources")
        xo = res.get_object().get("/XObject") if res else None
        if not xo:
            continue
        hit = False
        for name, ref in xo.get_object().items():
            if not str(name).startswith("/HeaderFooter"):
                continue
            ref.get_object().set_data(b"")
            hit = True
        if hit:
            cleared += 1
    if cleared:
        writer = PdfWriter(clone_from=reader)
        with open(pdf_path, "wb") as fh:
            writer.write(fh)
    return cleared


def page_html(title: str, body: str) -> str:
    return (
        "<!DOCTYPE html>\n"
        '<html xmlns="http://www.w3.org/1999/xhtml"><head>'
        '<meta charset="utf-8"/>'
        f"<title>{esc(title)}</title>"
        '<link rel="stylesheet" type="text/css" href="print.css"/>'
        f"</head><body>{substitute_glyphs(body)}</body></html>\n"
    )


# ---------------------------------------------------------------- the build


def build(book_nums: list[int], trim: str, force_recto: bool,
          odd_even_offset: int | None) -> Path:
    if trim not in TRIMS:
        sys.exit(f"unknown trim {trim!r}; choose from {', '.join(TRIMS)}")
    geo = TRIMS[trim]

    if WORK.exists():
        shutil.rmtree(WORK)
    (WORK / "fonts").mkdir(parents=True)
    for f in ["Gentium-Regular.woff2", "Gentium-Italic.woff2"]:
        shutil.copy(EPUB_ASSETS / f, WORK / "fonts" / f)
    shutil.copy(BUILD / "print.css", WORK / "print.css")

    front = front_matter()
    books: dict[int, dict] = {}
    rendered: dict[int, str] = {}
    for n in book_nums:
        src = SRC / f"book_{n:02d}.txt"
        if not src.exists():
            sys.exit(f"missing {src}")
        books[n] = parse_book(src)
        rendered[n] = render_book(books[n])
    arguments = {n: bk["argument"] for n, bk in books.items()}
    tnotes = tnotes_html(books)
    further = further_reading_html()
    idx = index_html()

    toc_folios: dict[int, int] | None = None
    toc_front: list[tuple[str, str | None]] = [(INTRO_TITLE, None)]
    toc_back: list[tuple[str, int | None]] = [
        (TNOTES_TITLE, None), (FURTHER_TITLE, None), (INDEX_TITLE, None)]

    # A blank page that holds (see the Odyssey builder for why each part
    # is load-bearing): explicit height, real content, INLINE styles, and
    # only page-break-before.
    BLANK = (
        '<div style="page-break-before:always;height:7in">'
        '<p style="height:6in;margin:0">&#160;</p></div>'
    )

    def assemble(blank_before: set[int]) -> str:
        parts = list(front)
        parts.append(contents_page(book_nums, arguments, toc_folios,
                                   toc_back, toc_front))
        for n in book_nums:
            if n in blank_before:
                parts.append(BLANK)
            parts.append(rendered[n])
        parts.append(tnotes)
        if further:
            parts.append(further)
        if idx:
            parts.append(idx)
        return "\n".join(parts)

    root = WORK / "iliad-print.html"
    root.write_text(page_html(TITLE, assemble(set())), encoding="utf-8")

    epub = WORK / "print-src.epub"

    def to_epub() -> None:
        subprocess.run(
            [EBOOK_CONVERT, str(root), str(epub),
             "--title", TITLE,
             "--authors", "Homer",
             "--language", "en",
             "--disable-font-rescaling",
             "--change-justification", "left",
             "--chapter", "//h:h1 | //h:span[@class='guide']",
             "--chapter-mark", "none",
             # calibre's default page-breaks-before is h1 AND h2, which
             # would start every section head of the introduction, the
             # translator's notes, and the further-reading guide on a
             # fresh page (and leave each chapter's opener nearly empty).
             # Only h1 opens a page; the stylesheet breaks before h1 and
             # the per-book notes head itself.
             "--page-breaks-before", "//h:h1",
             "--no-default-epub-cover",
             "--dont-split-on-page-breaks",
             # calibre splits any flow over 260 KB, by preference at a
             # heading, and every split file starts a new page in the PDF:
             # a chapter's first section head would jump to a fresh page
             # and leave the opener empty. The EPUB is only an intermediate
             # here, so size-based splitting is off.
             "--flow-size", "0"],
            check=True, cwd=WORK, stdout=subprocess.DEVNULL)

    print("building intermediate epub...")
    to_epub()

    suffix = trim.replace(".", "-")
    out = BUILD / (f"iliad-print-{suffix}.pdf" if book_nums != [1]
                   else f"iliad-print-{suffix}-book01.pdf")

    header = (
        '<header style="font-family:Georgia,serif;font-size:8pt;'
        'letter-spacing:0.08em;box-sizing:border-box;'
        f'padding:{HEAD_PAD_PT}pt 0.3in 0;'
        'text-transform:uppercase">'
        '<div style="margin:auto">_SECTION_</div>'
        '</header>'
    )
    footer = (
        '<footer style="font-family:Georgia,serif;font-size:9pt;'
        'box-sizing:border-box;'
        f'padding:0 0.3in {HEAD_PAD_PT}pt">'
        '<div class="even-page">_PAGENUM_</div>'
        '<div class="odd-page" style="margin-left:auto">_PAGENUM_</div>'
        '</footer>'
    )

    f = CALIBRE_MARGIN_FACTOR
    ml = geo["inner"] / f
    mr = geo["outer"] / f
    mt = (geo["top"] + HEAD_ALLOWANCE_PT) / f
    mb = (geo["bottom"] + HEAD_ALLOWANCE_PT) / f
    page_map: list[str] = []

    cmd_pdf = [
        EBOOK_CONVERT, str(epub), str(out),
        "--custom-size", f'{geo["w"]}x{geo["h"]}',
        "--unit", "inch",
        "--margin-left", str(ml),
        "--margin-right", str(mr),
        "--margin-top", str(mt),
        "--margin-bottom", str(mb),
        "--pdf-page-margin-left", "0",
        "--pdf-page-margin-right", "0",
        "--pdf-page-margin-top", "0",
        "--pdf-page-margin-bottom", "0",
        "--pdf-page-numbers",
        "--pdf-header-template", header,
        "--pdf-footer-template", footer,
        "--pdf-serif-family", "Gentium",
        "--pdf-standard-font", "serif",
        "--pdf-default-font-size", str(BASE_FONT_REQUEST),
        # The epub->pdf conversion runs calibre's structure detection again
        # on the way in, and its default is a page break before every h1
        # AND h2 — which is what pushed each prose chapter's first section
        # head onto a fresh page. Restrict it here as well as in to_epub.
        "--page-breaks-before", "//h:h1",
        # ...and its default chapter detection treats any h1/h2 whose text
        # begins "Book ..." as a chapter and marks it with a page break —
        # exactly the "Book N" heads of the translator's notes. The running
        # heads come from the EPUB's own contents, so detection here can be
        # pinned to the same expression as to_epub and marked with nothing.
        "--chapter", "//h:h1 | //h:span[@class='guide']",
        "--chapter-mark", "none",
        "--disable-font-rescaling",
        "--embed-all-fonts",
        "--subset-embedded-fonts",
    ]
    if odd_even_offset:
        cmd_pdf += ["--pdf-odd-even-offset", str(odd_even_offset)]

    def to_pdf() -> None:
        subprocess.run(cmd_pdf + page_map, check=True, cwd=WORK,
                       stdout=subprocess.DEVNULL)

    print(f"rendering pdf ({trim}, {geo['w']}x{geo['h']}in)...")
    to_pdf()

    # --- recto pass: fix one book per pass, earliest first, never take a
    # blank back (see the Odyssey builder for why that is what converges).
    blanks: set[int] = set()
    if force_recto and len(book_nums) > 1:
        for attempt in range(1, len(book_nums) + 2):
            openers = _book_opener_pages(out)
            if not openers:
                print("recto pass: could not locate book openers; skipping")
                break
            offenders = [n for n in book_nums
                         if openers.get(n) and openers[n] % 2 == 0]
            if not offenders:
                print("recto pass: every book already opens on a recto"
                      if attempt == 1 else
                      f"recto pass: all books on a recto after "
                      f"{attempt - 1} pass(es), {len(blanks)} blank(s)")
                break
            nxt = next((n for n in offenders if n not in blanks), None)
            if nxt is None:
                print(f"recto pass: cannot place {len(offenders)} book(s) "
                      f"on a recto: {', '.join(map(str, offenders))}")
                break
            blanks.add(nxt)
            print(f"recto pass {attempt}: book {nxt} opens on a verso "
                  f"({len(offenders)} left); inserting blank "
                  f"({len(blanks)} total)")
            root.write_text(page_html(TITLE, assemble(blanks)), encoding="utf-8")
            to_epub()
            to_pdf()

    # --- folios: none on the front matter; page 1 is the poem's first page.
    openers = _book_opener_pages(out)
    first = openers.get(min(book_nums)) if openers else None
    n_front = (first - 1) if first and first > 1 else 0
    if n_front:
        page_map[:] = ["--pdf-page-number-map",
                       f"if (n <= {n_front}) 0; else n - {n_front};"]
        print(f"folios: {n_front} front-matter page(s) unnumbered; "
              "page 1 is the poem's first page")
        to_pdf()

    # --- contents: fill the folios and render again; verify nothing moved.
    openers = _book_opener_pages(out)
    if openers:
        toc_folios = {n: p - n_front for n, p in openers.items() if p - n_front > 0}
        back_rows = []
        for label in (TNOTES_TITLE, FURTHER_TITLE, INDEX_TITLE):
            p = _heading_page(out, label)
            back_rows.append((label, p - n_front if p and p - n_front > 0 else None))
        toc_back = back_rows
        intro_p = _heading_page(out, INTRO_TITLE)
        toc_front = [(INTRO_TITLE, roman(intro_p) if intro_p else None)]
        print(f"contents: filling {len(toc_folios)} book page number(s) and "
              f"{sum(1 for _, p in back_rows if p)} back-matter row(s)")
        root.write_text(page_html(TITLE, assemble(blanks)), encoding="utf-8")
        to_epub()
        to_pdf()
        after = _book_opener_pages(out)
        moved = [n for n in openers if after.get(n) is not None and after[n] != openers[n]]
        if moved:
            print(f"  WARNING: {len(moved)} book(s) shifted when the contents "
                  "was filled; the printed page numbers are wrong. Check "
                  "tools/check_print.py before using this file.")
        elif len(after) != len(openers):
            print("  WARNING: the book count changed on the contents pass")

    # --- index guide words.
    guide_titles: set[str] = set()
    headwords = _index_headwords() if idx else []
    if headwords:
        guides = _index_guides(out, headwords)
        openers_before = _book_opener_pages(out)
        for attempt in range(1, 4):
            if not guides:
                break
            idx = index_html(guides)
            root.write_text(page_html(TITLE, assemble(blanks)), encoding="utf-8")
            to_epub()
            to_pdf()
            again = _index_guides(out, headwords)
            if again == guides:
                print(f"index guide words: {len(guides)} page(s)")
                guide_titles = set(guides.values())
                break
            print(f"index guide words: pagination shifted on pass {attempt}; "
                  "re-measuring")
            guides = again
        else:
            print("  WARNING: index guide words did not settle in 3 passes")
        if _book_opener_pages(out) != openers_before:
            print("  WARNING: the books shifted when the guide words were "
                  "added; the contents page numbers are wrong. Check "
                  "tools/check_print.py before using this file.")

    # --- final pass: clear the head and folio from the front matter and
    # the blank leaves.
    strip: set[int] = set(range(n_front))
    blanks_found = _find_blank_leaves(out)
    strip |= blanks_found
    if strip:
        cleared = _clear_running_heads(out, strip)
        if cleared:
            print(f"cleared the running head and folio from {cleared} page(s)"
                  f" ({len(blanks_found)} blank leaf/leaves, "
                  f"{len(strip) - len(blanks_found)} front matter)")
    if guide_titles:
        n = _strip_outline(out, guide_titles)
        if n:
            print(f"dropped {n} guide-word entries from the pdf outline")

    print(f"\nwrote {out}  ({out.stat().st_size:,} bytes)")
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--books", nargs="*", type=int,
                    help="book numbers to include (default: all 24)")
    ap.add_argument("--trim", default="6x9", choices=sorted(TRIMS),
                    help="trim size (default: 6x9 US trade)")
    ap.add_argument("--no-recto", action="store_true",
                    help="do not force book openers onto a recto page")
    ap.add_argument("--odd-even-offset", type=int, default=None,
                    help="shift text by N pt for gutter (CropBox; opt-in)")
    args = ap.parse_args()
    nums = args.books if args.books else list(range(1, 25))
    build(nums, args.trim, not args.no_recto, args.odd_even_offset)
