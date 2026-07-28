#!/usr/bin/env python3
"""Build a high-quality EPUB of the Iliad translation.

Ported from the Odyssey project's tools/build_epub.py (which shipped epub,
azw3 and pdf). The pipeline and assets are the same; the source format is
not, so this version adds a real parser. An Odyssey book is markdown with
[^L1] footnotes; an Iliad book is plain text in four rule-delimited parts:

    BOOK N                          <- title
    <epigraph sentence>             <- the one-line argument
    TRANSLATOR'S COMMENTARY
    <prose>
    ------------------------------  <- first rule
    <verse: "  NNN  text[7]">       <- bracketed-integer footnote markers
    ------------------------------  <- second rule
    [Notes]                         <- header present in Books 1-9 only
    [7] (1.123) <note text>
         <indented continuations>

The same rule-anchored boundary logic as build_index.py and lookup.py; the
translator's commentary cites line numbers in prose that would otherwise be
indistinguishable from verse.

Per book the converter emits Pandoc markdown:
  - "# Book N" chapter heading + the epigraph as a styled argument line;
  - the commentary as a "Translator's Note" section (KEEP-OR-CUT decision
    for the editor: it is included so v1 review can see it in place);
  - each verse line with its number in <span class="ln" id="vB-N"> and a
    hard break, so the index's book.line citations link straight to lines;
  - [7] -> [^b01-7] namespaced footnotes, definitions moved under a Notes
    heading, so labels can't collide when 24 books concatenate;
  - absent-verse placeholders (9.458-461, 11.543, 14.269) as styled lines.

Back matter: index/index.md with every book.line citation linkified to its
verse anchor, exactly as in the Odyssey build.

Usage:
    python tools/build_epub.py                 # all 24 books
    python tools/build_epub.py --books 1       # Book 1 proof of concept
"""
from __future__ import annotations
import argparse, os, re, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "translation"
BUILD = ROOT / "epub-build"
WORK = BUILD / "work"
ASSETS = BUILD / "assets"

PANDOC = os.environ.get("PANDOC") or shutil.which("pandoc") or \
    str(Path(os.environ["LOCALAPPDATA"]) / "Pandoc" / "pandoc.exe")

RULE_RE = re.compile(r"^-{20,}\s*$")
VERSE_RE = re.compile(r"^\s*(\d+)\s\s+(\S.*)$")
REF_RE = re.compile(r"\[(\d+)\]")                 # inline marker: wrath[1]
DEF_RE = re.compile(r"^\[(\d+)\]\s+")             # note definition: [1] (1.1) ...
ABSENT_RE = re.compile(r"^\s*\[Lines?\b.*absent from the printed text.*\]$")


def parse_book(text: str):
    """Split a book file into (title_no, epigraph, commentary, verse, notes)."""
    lines = text.splitlines()
    rules = [i for i, ln in enumerate(lines) if RULE_RE.match(ln)]
    if len(rules) < 2:
        sys.exit("book file lacks the two delimiting rules")
    head, verse, tail = lines[:rules[0]], lines[rules[0]+1:rules[1]], lines[rules[1]+1:]

    m = re.match(r"BOOK (\d+)", head[0].strip())
    if not m:
        sys.exit(f"unexpected first line: {head[0]!r}")
    book_no = int(m.group(1))

    try:
        ci = next(i for i, ln in enumerate(head) if ln.strip() == "TRANSLATOR'S COMMENTARY")
    except StopIteration:
        sys.exit(f"book {book_no}: no TRANSLATOR'S COMMENTARY header")
    epigraph = " ".join(ln.strip() for ln in head[1:ci] if ln.strip())
    commentary = "\n".join(head[ci+1:]).strip("\n")

    # Notes: drop leading blanks and the optional bare "Notes" header (Books 1-9).
    while tail and not tail[0].strip():
        tail.pop(0)
    if tail and tail[0].strip() == "Notes":
        tail.pop(0)
    notes = "\n".join(tail).strip("\n")
    return book_no, epigraph, commentary, verse, notes


def convert_book(text: str) -> tuple[str, int, str]:
    """Return (chapter_md, book_no, commentary_md).

    The commentary is NOT emitted into the chapter: the poem should open with
    the poem. It is returned separately and collected into a back-matter
    chapter ("The Translator's Notes on the Books"); the chapter carries a
    one-tap link to its section there, under the argument line.
    """
    b, epigraph, commentary, verse, notes = parse_book(text)
    tag = f"b{b:02d}"
    out = [f"# Book {b} {{#book-{b}}}", "",
           f'<p class="argument">{epigraph}</p>', "",
           f'<p class="tnote-link">[Translator’s note →](#tnote-{b})</p>', ""]

    out += ['<div class="verse">', ""]
    for idx, line in enumerate(verse):
        if not line.strip():
            out.append("")
            continue
        if ABSENT_RE.match(line):
            # Escape the leading bracket so markdown never reads it as a link.
            out.append(f'<p class="absent">\\{line.strip()}</p>')
            continue
        vm = VERSE_RE.match(line)
        if not vm:
            # Shouldn't happen inside the rules; keep the line visible so a
            # format drift is noticed in proofing rather than silently eaten.
            out.append(line)
            continue
        num, body = vm.groups()
        body = REF_RE.sub(rf"[^{tag}-\1]", body)
        formatted = f'<span class="ln" id="v{b}-{num}">{num}</span> {body}'
        nxt = verse[idx + 1] if idx + 1 < len(verse) else ""
        if nxt.strip() and VERSE_RE.match(nxt):
            formatted += "\\"           # Pandoc hard break between verse lines
        out.append(formatted)
    out += ["", "</div>", ""]

    if notes:
        out += ["## Notes {.unnumbered}", ""]
        for line in notes.splitlines():
            dm = DEF_RE.match(line)
            if dm:
                line = DEF_RE.sub(rf"[^{tag}-{dm.group(1)}]: ", line, count=1)
            out.append(line)
        out.append("")
    return "\n".join(out) + "\n", b, commentary


def intro_page() -> str:
    """translation/introduction.txt as front matter.

    The file is clean flowing prose under five roman-numeral section heads
    ("I. THE POEM"); we drop its own three-line masthead (the chapter heading
    replaces it) and promote the section heads to level-2 headings.
    """
    src = ROOT / "translation" / "introduction.txt"
    if not src.exists():
        return ""
    lines = src.read_text(encoding="utf-8").splitlines()
    # Drop everything up to and including the "GENERAL INTRODUCTION" masthead.
    for i, ln in enumerate(lines):
        if ln.strip() == "GENERAL INTRODUCTION":
            lines = lines[i + 1:]
            break
    out = ["# General Introduction {.unnumbered}", ""]
    for ln in lines:
        if re.match(r"^[IVX]+\.\s+[A-Z][A-Z ]+$", ln.strip()):
            out += ["", f"## {ln.strip()} {{.unnumbered}}", ""]
        else:
            out.append(ln)
    return "\n".join(out) + "\n"


def tnotes_page(commentaries: list[tuple[int, str]]) -> str:
    """Back-matter chapter collecting the per-book translator's commentaries.

    Kept as 24 discrete headed sections rather than merged into an essay: the
    probe that motivated this layout showed they are book-specific (only 5 of
    24 restate policy), and the General Introduction already does the
    synthesis. Each section heading links back to its book.
    """
    out = ['# The Translator’s Notes on the Books {.unnumbered .tnotes #tnotes}',
           "",
           "The note on each book, collected here so the poem itself reads "
           "clean. Each heading links back to its book; in the text, the line "
           "under every book’s argument links here.", ""]
    for b, commentary in commentaries:
        out += [f"## [Book {b}](#book-{b}) {{#tnote-{b}}}", "", commentary, ""]
    return "\n".join(out) + "\n"


def title_page() -> str:
    # Roles mirror the Odyssey edition. The translator credit is a v1 decision
    # for the editor; "Claude" is deliberately model-unversioned here.
    return (
        '# The Iliad {.unnumbered .hidden-title}\n\n'
        '<div class="titlepage">\n\n'
        '<p class="tp-title">The Iliad</p>\n\n'
        '<p class="tp-sub">a line-for-line translation</p>\n\n'
        '<hr class="tp-rule"/>\n\n'
        '<p class="tp-role">from the Greek of</p>\n\n'
        '<p class="tp-name">Homer</p>\n\n'
        '<p class="tp-role">translated by</p>\n\n'
        '<p class="tp-name">Claude <span class="tp-small">(Fable 5)</span></p>\n\n'
        '<p class="tp-role">edited and produced by</p>\n\n'
        '<p class="tp-name">Chris Duffy</p>\n\n'
        '</div>\n\n'
    )


def epigraph_page() -> str:
    return (
        '# Proem {.unnumbered .hidden-title}\n\n'
        '<div class="epigraph-page">\n\n'
        '<p class="epigraph"><span class="greek" lang="grc">'
        "μῆνιν ἄειδε θεὰ Πηληϊάδεω Ἀχιλῆος"
        "</span>\nSing, goddess, the wrath of Peleus&#8217; son Achilles</p>\n\n"
        "</div>\n\n"
    )


def source_page() -> str:
    return (
        "# A Note on the Text {.unnumbered}\n\n"
        "The Greek is the Oxford Classical Text of Monro and Allen (3rd "
        "edition, 1920). The English translation is original to this project; "
        "each of its 15,687 lines is keyed one-to-one to its Greek line, and "
        "the printed text is followed throughout — including three passages "
        "the printed Greek lacks (9.458–461, 11.543, 14.269), which are "
        "marked in place rather than supplied.\n\n"
        "Each book closes with its endnotes: a raised numeral in the text "
        "marks a note; tap it to jump there, and tap the return arrow (↩) to "
        "come back to your place in the verse. The translator's notes on the "
        "several books are collected at the back, one tap from each book's "
        "opening.\n\n"
        "Monro and Allen's 1920 text is in the public domain. Polytonic Greek "
        "is set in Gentium Plus (SIL Open Font License).\n\n"
    )


# A citation is book.line, optionally a range (–NN) or "ff". Books 1..24.
CITE_RE = re.compile(r"\b([12]?\d)\.(\d{1,3})(–\d{1,3}|ff)?")


def _link_citation(m: re.Match, present_books: set[int]) -> str:
    book, line = int(m.group(1)), m.group(2)
    text = m.group(0)
    if not (1 <= book <= 24) or book not in present_books:
        return text
    return f"[{text}](#v{book}-{line})"


def index_page(present_books: set[int]) -> str:
    """index/index.md as a back-matter chapter, citations linked to verse."""
    src = ROOT / "index" / "index.md"
    if not src.exists():
        return ""
    raw = src.read_text(encoding="utf-8").splitlines()
    out = []
    for i, line in enumerate(raw):
        if CITE_RE.search(line) and not line.startswith("#"):
            line = CITE_RE.sub(lambda m: _link_citation(m, present_books), line)
        stripped = line.strip()
        nxt = raw[i + 1].strip() if i + 1 < len(raw) else ""
        if stripped and nxt and nxt != "---" and stripped != "---":
            line = line + "\\"
        out.append(line)
    body = "\n".join(out)
    body = re.sub(r"^# .*\n", "", body, count=1)
    body = re.sub(r"^\s*Every named person.*?pronunciation scheme\.\s*\n",
                  "", body, count=1, flags=re.S)
    header = (
        '# Index of Principal Names {.unnumbered #name-index}\n\n'
        "The poem's principal persons, gods, peoples, and places — every "
        "figure of consequence — with a pronunciation (*Say:*), epithets, "
        "aliases, kin, and line citations. Each citation is a link: tap a "
        "**book.line** number to jump to that verse. Pronunciations give the "
        "traditional anglicized reading; **stress falls on the capitalized "
        "syllable**. The several hundred men named once and killed in the "
        "same breath are catalogued for a later edition.\n\n"
        '<div class="name-index">\n\n')
    return header + body + "\n\n</div>\n\n"


def build(book_nums: list[int]) -> Path:
    if WORK.exists():
        shutil.rmtree(WORK)
    WORK.mkdir(parents=True)
    (WORK / "fonts").mkdir()
    for f in ["Gentium-Regular.woff2", "Gentium-Italic.woff2"]:
        shutil.copy(ASSETS / f, WORK / "fonts" / f)

    inputs: list[Path] = []
    commentaries: list[tuple[int, str]] = []

    front = [("00-title.md", title_page()),
             ("00-epigraph.md", epigraph_page())]
    intro = intro_page()
    if intro:
        front.append(("01-intro.md", intro))
    front.append(("02-note.md", source_page()))
    for name, content in front:
        p = WORK / name
        p.write_text(content, encoding="utf-8")
        inputs.append(p)

    for n in book_nums:
        src = SRC / f"book_{n:02d}.txt"
        if not src.exists():
            sys.exit(f"missing {src}")
        chapter, book_no, commentary = convert_book(src.read_text(encoding="utf-8"))
        dst = WORK / f"{n:02d}-book.md"
        dst.write_text(chapter, encoding="utf-8")
        inputs.append(dst)
        if commentary:
            commentaries.append((book_no, commentary))

    if commentaries:
        tn = WORK / "98-tnotes.md"
        tn.write_text(tnotes_page(commentaries), encoding="utf-8")
        inputs.append(tn)

    idx_md = index_page(set(book_nums))
    if idx_md:
        idx = WORK / "99-index.md"
        idx.write_text(idx_md, encoding="utf-8")
        inputs.append(idx)

    out = BUILD / ("iliad-book01.epub" if book_nums == [1] else "iliad.epub")

    meta = WORK / "metadata.yaml"
    meta.write_text(
        "---\n"
        "title: The Iliad\n"
        "subtitle: A line-for-line translation\n"
        "creator:\n"
        "  - role: aut\n    text: Homer\n"
        "  - role: trl\n    text: Claude (Fable 5)\n"
        "  - role: edt\n    text: Chris Duffy\n"
        "language: en\n"
        "rights: >-\n"
        "  English translation original to this project. Greek source text "
        "(Monro-Allen 1920) public domain.\n"
        "...\n",
        encoding="utf-8",
    )

    cmd = [
        PANDOC,
        str(meta),
        *[str(p) for p in inputs],
        "--from=markdown+footnotes+raw_html",
        "--to=epub3",
        "--epub-title-page=false",
        "--split-level=1",
        f"--lua-filter={BUILD / 'backlinks.lua'}",
        "--toc", "--toc-depth=1",
        f"--css={BUILD / 'style.css'}",
        "--epub-embed-font=" + str(WORK / "fonts" / "Gentium-Regular.woff2"),
        "--epub-embed-font=" + str(WORK / "fonts" / "Gentium-Italic.woff2"),
        "--metadata=lang:en",
        "-o", str(out),
    ]
    # Cover: assets/cover.png is the hybrid design (art/iliad-cover-hybrid.png).
    # Falls back to cover.jpg; builds fine with neither.
    for cov in (ASSETS / "cover.png", ASSETS / "cover.jpg"):
        if cov.exists():
            cmd.insert(-2, f"--epub-cover-image={cov}")
            break
    print("running pandoc...")
    subprocess.run(cmd, check=True, cwd=WORK)
    print(f"\nwrote {out}  ({out.stat().st_size:,} bytes)")
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--books", nargs="*", type=int,
                    help="book numbers to include (default: all 24)")
    args = ap.parse_args()
    build(args.books if args.books else list(range(1, 25)))
