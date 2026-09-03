#!/usr/bin/env python3
"""Build the web reading edition: one HTML page per book, into docs/read/.

Ported from the Odyssey project's tools/build_web.py (theclaudyssey.com);
the site structure, styling, search, and machine-readable layer are the
same, but the source format is the Iliad's plain-text book files, so the
parser is the one from build_epub.py rather than the Odyssey's markdown
reader. Reads translation/book_NN.txt (untouched) and emits:

    docs/read/read.css               shared stylesheet (matches the landing page)
    docs/read/index.html             contents page: all 24 books with their
                                     arguments, plus site search
    docs/read/book-NN.html           one page per book: the argument, the
                                     translator's note (collapsed), the verse
                                     with line anchors, and the endnotes
    docs/read/names.html             index of names & places, from index/index.md
    docs/read/introduction.html      the General Introduction
    docs/read/further-reading.html   For Further Reading

Each verse line gets an anchor (#L123); every fifth line shows its number in
the gutter and every line's number is a copyable permalink. The bracketed
[7] note markers become superscript links to endnotes at the foot of the
page, keeping the source's own per-book numbering; each endnote links back
to its marker and to the verse line it glosses. The three passages the
printed Greek lacks (9.458-461, 11.543, 14.269) are shown as the source's
bracketed placeholders, in place.

names.html renders every entry of index/index.md with its line citations
turned into deep links (12.184 -> book-12.html#L184), plus client-side
category chips, an A-Z bar, and a live name filter.

docs/api/ is a machine-readable mirror for LLMs and scripts that fetch the
site: registry.json (the name index with refs), book-NN.txt (each book's
translation source, verbatim), aligned-NN.jsonl (the Greek and the English
paired line by line, one JSON object per verse), manifest.json describing
all of it, and an index.html landing page documenting the formats.

Book pages, names.html, and the two prose pages carry data-pagefind-body so
the site search covers the poem, the notes, the index, and the front and
back matter. After building, refresh the search bundle with:

    npx -y pagefind --site docs

Usage:
    python tools/build_web.py
"""
from __future__ import annotations
import hashlib
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "translation"
GREEK = ROOT / "books"
INTRO = SRC / "introduction.txt"
FURTHER = ROOT / "further_reading.txt"
IDX = ROOT / "index" / "index.md"
REGISTRY = ROOT / "index" / "registry.json"
DOCS = ROOT / "docs"
OUT = DOCS / "read"
OUT_API = DOCS / "api"
SITE = "https://wrath-sing-goddess.com"
REPO = "https://github.com/spinchange/iliad"
SITE_NAME = "The Iliad — Wrath, Sing, Goddess"
TAGLINE = "wrath, sing, goddess"

# --- the book-file format (shared with build_epub.py) -----------------------
# BOOK N / epigraph / TRANSLATOR'S COMMENTARY / prose / ---- / verse / ---- /
# [Notes|NOTES] / "[7] (1.123-125) note text" with indented continuations.
RULE_RE = re.compile(r"^-{20,}\s*$")
VERSE_RE = re.compile(r"^\s*(\d+)\s\s+(\S.*)$")
REF_RE = re.compile(r"\[(\d+)\]")                        # inline marker: wrath[1]
DEF_RE = re.compile(r"^\[(\d+)\]\s+(?:\((\d+)\.(\d+)([^)]*)\)\s*)?(.*)$")
ABSENT_RE = re.compile(r"^\s*\[Lines?\b.*absent from the printed text.*\]$")

# a book.line citation in prose, book bounded to 1-24. Group 1 catches a
# preceding author/work abbreviation so citations of other texts ("Od. 11.5",
# "Hdt. 2.116") are left unlinked.
CITE_RE = re.compile(
    r"((?:\b(?:Od|Odyssey|Odyssey's|Hdt|Herodotus|Thuc|Thucydides|Theog|Theogony|"
    r"WD|Works|Aen|Aeneid|Met|Metamorphoses|Hymn|Pind|Pindar|Ol|Pyth|Nem|Isthm|"
    r"Plut|Plutarch|Strabo|Paus|Pausanias|Apollod|Apollodorus|Bibl|Epit|Diod|"
    r"Cypria|Aethiopis|fr|frr|Il|Iliad|Sch|Schol|Eust|Poet|Poetics|Rep|Republic|"
    r"Ion|Sym|Symposium|Athen|Athenaeus|Verg|Virgil|Ov|Ovid|Hor|Horace|Cic|Cicero|"
    r"Quint|Quintus|Dio|Chrys|Philostr|Philostratus|Her|Heroicus|Dict|Dictys|"
    r"Dares|Trag|Soph|Sophocles|Aesch|Aeschylus|Eur|Euripides|Ar|Aristophanes|"
    r"Arist|Aristotle|Pl|Plato|Xen|Xenophon|Lucian|Nonn|Nonnus|Trypho|Tzetz|"
    r"Tzetzes|Proclus|Chrest|Chrestomathy|Heraclitus|Sappho|Alcaeus|Archil|"
    r"Sublime|Laertius|Memorabilia|Mem|Longinus|Diogenes|Geography|Hist|"
    r"Archilochus|Simon|Simonides|Bacchyl|Bacchylides|Callim|Callimachus|Theoc|"
    r"Theocritus|Apoll|Apollonius|Arg|Argonautica|Posthomerica|Vit|Vita|p|pp|"
    r"vol|vols|no|nos|c|ca|ch|chs|bk|bks|Book|Books|book|books|lines?|ll|l|"
    r"cf|Catalogue|Scholia|Scholium|A|B|T|D|bT|Ven|Venetus)\.?\s+)?)"
    r"\b(2[0-4]|1[0-9]|[1-9])\.([1-9]\d{0,2})\b")

ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI",
         "XII", "XIII", "XIV", "XV", "XVI", "XVII", "XVIII", "XIX", "XX",
         "XXI", "XXII", "XXIII", "XXIV"]

TOTAL_LINES = 15687  # 24 books, Monro-Allen numbering, minus the 6 absent lines
GAPS = "9.458–461, 11.543, 14.269"


# ---------------------------------------------------------------------------
# Parsing


def esc(text: str) -> str:
    return html.escape(text, quote=False)


def paragraphs(lines: list[str]) -> list[str]:
    """Blank-line-separated runs of lines, each joined into one string."""
    out: list[str] = []
    cur: list[str] = []
    for ln in lines:
        if ln.strip():
            cur.append(ln.strip())
        elif cur:
            out.append(" ".join(cur))
            cur = []
    if cur:
        out.append(" ".join(cur))
    return out


def parse_book(path: Path) -> dict:
    """Return {n, argument, commentary, stanzas, notes}.

    stanzas: list of stanzas, each a list of ("v", lineno, text) or
    ("absent", text) items. notes: list of {num, book, line, span, body} in
    file order, num being the source's own bracketed number."""
    lines = path.read_text(encoding="utf-8").splitlines()
    rules = [i for i, ln in enumerate(lines) if RULE_RE.match(ln)]
    if len(rules) != 2:
        raise SystemExit(f"{path.name}: expected two rules, found {len(rules)}")
    head, verse, tail = (lines[:rules[0]], lines[rules[0] + 1:rules[1]],
                         lines[rules[1] + 1:])

    m = re.match(r"BOOK (\d+)", head[0].strip())
    if not m:
        raise SystemExit(f"{path.name}: unexpected first line {head[0]!r}")
    n = int(m.group(1))
    try:
        ci = next(i for i, ln in enumerate(head)
                  if ln.strip() == "TRANSLATOR'S COMMENTARY")
    except StopIteration:
        raise SystemExit(f"{path.name}: no TRANSLATOR'S COMMENTARY header")
    argument = " ".join(ln.strip() for ln in head[1:ci] if ln.strip())
    commentary = paragraphs(head[ci + 1:])

    stanzas: list[list[tuple]] = []
    cur: list[tuple] = []
    for ln in verse:
        if not ln.strip():
            if cur:
                stanzas.append(cur)
                cur = []
            continue
        if ABSENT_RE.match(ln):
            cur.append(("absent", ln.strip()))
            continue
        vm = VERSE_RE.match(ln)
        if not vm:
            raise SystemExit(f"{path.name}: unparsed verse line {ln!r}")
        cur.append(("v", int(vm.group(1)), vm.group(2)))
    if cur:
        stanzas.append(cur)

    notes: list[dict] = []
    for ln in tail:
        if not ln.strip() or ln.strip().lower() == "notes":
            continue
        dm = DEF_RE.match(ln)
        if dm:
            num, book, line, span, body = dm.groups()
            notes.append({"num": int(num), "book": int(book) if book else n,
                          "line": int(line) if line else None,
                          "span": (span or "").strip(), "body": body.strip()})
        elif notes and ln.startswith(" "):
            notes[-1]["body"] += " " + ln.strip()
        else:
            raise SystemExit(f"{path.name}: unparsed note line {ln!r}")

    # Every marker in the verse must have a note; a note nobody cites (Book
    # 9's "[18] - merged into [17]") is dropped from the page.
    cited = {int(x) for st in stanzas for it in st if it[0] == "v"
             for x in REF_RE.findall(it[2])}
    defined = {nt["num"] for nt in notes}
    if cited - defined:
        raise SystemExit(f"{path.name}: markers without notes "
                         f"{sorted(cited - defined)}")
    for orphan in sorted(defined - cited):
        print(f"  (book {n}: note [{orphan}] is never cited; omitted)")
    # A note reading "[18] - merged into [17]." keeps its marker in the verse
    # but has no text of its own: the marker is pointed at the surviving note.
    alias: dict[int, int] = {}
    for nt in notes:
        am = re.match(r"^[—-]+\s*merged into \[(\d+)\]\.?$", nt["body"])
        if am:
            alias[nt["num"]] = int(am.group(1))
    if any(t not in defined or t in alias for t in alias.values()):
        raise SystemExit(f"{path.name}: bad merged-note alias {alias}")
    notes = [nt for nt in notes if nt["num"] in cited and nt["num"] not in alias]
    return {"n": n, "argument": argument, "commentary": commentary,
            "stanzas": stanzas, "notes": notes, "alias": alias}


# ---------------------------------------------------------------------------
# Page furniture


def css_version() -> str:
    """Short content hash of the stylesheet, used to cache-bust the CSS link."""
    return hashlib.md5(CSS.encode("utf-8")).hexdigest()[:8]


def social_meta(title: str, desc: str, path: str) -> str:
    """Canonical + Open Graph + Twitter card tags, all with absolute URLs.

    Scrapers (X, Discord, Slack, Facebook) ignore relative og: URLs, so
    everything here is rooted at SITE. The card image is the 1200x630
    social render of the shield (docs/social.jpg, from
    art/iliad-social-shield-nourl.png)."""
    url = f"{SITE}/{path}"
    t, d = html.escape(title), html.escape(desc)
    return f"""<link rel="canonical" href="{url}">
<meta property="og:title" content="{t}">
<meta property="og:description" content="{d}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="{html.escape(SITE_NAME)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/social.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
"""


def page(title: str, desc: str, body: str, path: str, depth_home: str = "../",
         indexed: bool = False, head_extra: str = "") -> str:
    body_attr = " data-pagefind-body" if indexed else ""
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
{social_meta(title, desc, path)}<link rel="stylesheet" href="read.css?v={css_version()}">
{head_extra}</head>
<body>
<div class="meander"></div>
<div class="wrap"{body_attr}>
<p class="site" data-pagefind-ignore><a href="{depth_home}">The Iliad · {TAGLINE}</a></p>
{body}
</div>
<div class="meander"></div>
<footer>
  <a href="index.html">Contents</a> · <a href="names.html">Index</a> · <a href="{depth_home}">About &amp; downloads</a><br>
  translation <a href="https://creativecommons.org/publicdomain/zero/1.0/">CC0</a> (public domain) ·
  notes, introduction &amp; index © 2026 Chris Duffy, <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a> ·
  Greek source public domain
</footer>
</body>
</html>
"""


def booknav(n: int, bottom: bool = False) -> str:
    prev_a = (f'<a href="book-{n-1:02d}.html">&lsaquo; Book {n-1}</a>'
              if n > 1 else "<span></span>")
    next_a = (f'<a href="book-{n+1:02d}.html">Book {n+1} &rsaquo;</a>'
              if n < 24 else "<span></span>")
    cls = "booknav bottom" if bottom else "booknav"
    return (f'<nav class="{cls}" data-pagefind-ignore>{prev_a}'
            f'<span class="mid"><a href="index.html">Contents</a> · '
            f'<a href="names.html">Index</a></span>{next_a}</nav>')


def cite_links(escaped: str, here: int | None = None) -> str:
    """Turn book.line citations in already-escaped text into deep links.

    A citation preceded by another work's abbreviation ("Od. 11.5") is left
    alone. `here` is the current book: citations into it link within the
    page rather than to a fresh copy of it."""
    def link(m: re.Match) -> str:
        if m.group(1):
            return m.group(0)
        b, l = int(m.group(2)), m.group(3)
        target = f"#L{l}" if b == here else f"book-{b:02d}.html#L{l}"
        return f'<a class="cite" href="{target}">{b}.{l}</a>'
    return CITE_RE.sub(link, escaped)


def prose(text: str, here: int | None = None) -> str:
    """One paragraph of source prose: escaped, with citations linked."""
    return cite_links(esc(text), here)


# ---------------------------------------------------------------------------
# Book pages


def build_book(bk: dict) -> str:
    n = bk["n"]
    out = [booknav(n)]
    out.append('<header class="bookhead">')
    out.append(f'<h1 data-pagefind-meta="title">Book {ROMAN[n-1]}</h1>')
    if bk["argument"]:
        out.append(f'<p class="argument">{esc(bk["argument"])}</p>')
    out.append("</header>")

    if bk["commentary"]:
        out.append('<details class="tnote">')
        out.append(f'<summary>Translator’s note on Book {n}</summary>')
        for para in bk["commentary"]:
            # "note [20]" / "note 20" in the commentary -> the endnote
            text = re.sub(r"\bnote \[?(\d+)\]?(?!\d)",
                          r'<a href="#n\1">note \1</a>', prose(para, n))
            out.append(f"<p>{text}</p>")
        out.append("</details>")

    out.append('<div class="verse">')
    seen: set[int] = set()  # the first marker for a note carries the back-link id
    for stanza in bk["stanzas"]:
        out.append('<div class="stanza">')
        for item in stanza:
            if item[0] == "absent":
                text = re.sub(r"note (\d+)", r'note <a href="#n\1">\1</a>',
                              esc(item[1]))
                out.append(f'<p class="absent">{text}</p>')
                continue
            _, lineno, text = item

            def ref(m: re.Match) -> str:
                i = bk["alias"].get(int(m.group(1)), int(m.group(1)))
                anchor = "" if i in seen else f' id="r{i}"'
                seen.add(i)
                return (f'<a class="fnref"{anchor} href="#n{i}">'
                        f'<sup>{i}</sup></a>')
            # substitute markers on the escaped text: the marker pattern
            # contains no characters that html.escape rewrites
            body = REF_RE.sub(ref, esc(text))
            # Every line gets a copyable permalink in the gutter; only every
            # fifth is visible at rest, the others appear on hover ("ghost").
            # data-pagefind-ignore keeps the numerals out of search excerpts;
            # ghosts are hidden from AT and tab order (the id itself is the
            # anchor - the visible fifth-line links remain accessible).
            shown = lineno % 5 == 0 or lineno == 1
            cls = "ln" if shown else "ln ghost"
            extra = "" if shown else ' aria-hidden="true" tabindex="-1"'
            num = (f'<a class="{cls}" href="#L{lineno}" data-pagefind-ignore'
                   f' title="copy link to line {lineno}"{extra}>{lineno}</a>')
            out.append(f'<p class="v" id="L{lineno}">{num}{body}</p>')
        out.append("</div>")
    out.append("</div>")

    if bk["notes"]:
        out.append('<section class="notes">')
        out.append("<h2>Notes</h2>")
        for nt in bk["notes"]:
            i = nt["num"]
            if nt["line"] is not None:
                span = esc(nt["span"]).replace("-", "–")
                where = f'line{"s" if span else ""} {nt["line"]}{span}'
                line_a = f'<a class="nline" href="#L{nt["line"]}">{where}</a> — '
            else:
                line_a = ""
            out.append(
                f'<p class="note" id="n{i}">'
                f'<span class="nnum">{i}</span> '
                f'{line_a}{prose(nt["body"], n)} '
                f'<a class="back" href="#r{i}" title="back to the text">&#8617;</a></p>')
        out.append("</section>")

    out.append(booknav(n, bottom=True))
    out.append(COPY_JS)

    arg = bk["argument"].rstrip(".")
    desc = (f"Book {n} of the Iliad, in a line-for-line English translation"
            + (f": {arg}." if arg else "."))
    return page(f"Iliad, Book {n} — Wrath, Sing, Goddess", desc,
                "\n".join(out), f"read/book-{n:02d}.html", indexed=True)


# Clicking a line number still navigates to its anchor (which is what turns
# on the :target highlight) and additionally puts the absolute permalink on
# the clipboard, with a small confirmation by the number. Clipboard access
# needs a secure context; elsewhere the numbers stay plain anchor links.
COPY_JS = """\
<script>
(function () {
  if (!navigator.clipboard) return;
  document.addEventListener('click', function (ev) {
    var a = ev.target.closest && ev.target.closest('a.ln');
    if (!a) return;
    var url = new URL(a.getAttribute('href'), location.href).href;
    navigator.clipboard.writeText(url).then(function () {
      var t = document.createElement('span');
      t.className = 'copied';
      t.textContent = 'link copied';
      var r = a.getBoundingClientRect();
      t.style.left = (r.left + window.scrollX) + 'px';
      t.style.top = (r.top + window.scrollY) + 'px';
      document.body.appendChild(t);
      setTimeout(function () { t.remove(); }, 1200);
    }).catch(function () {});
  });
})();
</script>"""

SEARCH_HEAD = '<link rel="stylesheet" href="../pagefind/pagefind-ui.css">\n'

SEARCH_BLOCK = """\
<div id="search"></div>
<script src="../pagefind/pagefind-ui.js"></script>
<script>
window.addEventListener('DOMContentLoaded', function () {
  if (window.PagefindUI) new PagefindUI({
    element: '#search', showSubResults: true, showImages: false,
    translations: { placeholder: 'Search the poem, the notes, and the index\\u2026' }
  });
});
</script>"""


def build_contents(books: dict[int, dict]) -> str:
    out = ['<header class="bookhead"><h1>The Iliad</h1>',
           '<p class="argument">a line-for-line translation '
           '&middot; twenty-four books</p></header>',
           SEARCH_BLOCK,
           '<ol class="toc">']
    for n in range(1, 25):
        arg = esc(books[n]["argument"])
        out.append(
            f'<li><a href="book-{n:02d}.html"><b>Book {ROMAN[n-1]}</b>'
            f'<span>{arg}</span></a></li>')
    out.append("</ol>")
    out.append(
        '<p class="apparatus"><a href="introduction.html">General introduction</a>'
        ' — the poem, the art of repetition, the Greek text, the English '
        'line, and this edition.</p>')
    out.append(
        '<p class="apparatus"><a href="names.html">Index of names &amp; places</a>'
        ' — the poem’s principal persons, gods, peoples, and places, with '
        'pronunciations and linked citations.</p>')
    out.append(
        '<p class="apparatus"><a href="further-reading.html">For further reading</a>'
        ' — the Iliad’s ancient company: the Cycle, the tragedians, the '
        'parodies, Rome’s answer, the hoaxes, the scholars.</p>')
    return page("Read the Iliad — Wrath, Sing, Goddess",
                "Homer's Iliad complete in a line-for-line English "
                "translation with notes: all twenty-four books, free to read "
                "online.", "\n".join(out), "read/index.html",
                head_extra=SEARCH_HEAD)


# ---------------------------------------------------------------------------
# Front and back matter: the introduction and the further-reading guide

HEAD_RE = re.compile(r"^(?:[IVX]+\.\s+)?[A-Z][^a-z]*$")


def build_introduction() -> str:
    lines = INTRO.read_text(encoding="utf-8").splitlines()
    for i, ln in enumerate(lines):
        if ln.strip() == "GENERAL INTRODUCTION":
            lines = lines[i + 1:]
            break
    out = ['<nav class="booknav" data-pagefind-ignore>'
           '<a href="index.html">&lsaquo; Contents</a><span></span>'
           '<a href="book-01.html">Book 1 &rsaquo;</a></nav>',
           '<header class="bookhead">',
           '<h1 data-pagefind-meta="title">General Introduction</h1>',
           '<p class="argument">the poem, the art of repetition, the Greek '
           'text, the English line, and this edition</p>',
           '</header>', '<div class="prose">']
    for para in paragraphs(lines):
        if re.match(r"^[IVX]+\.\s+[A-Z][A-Z ]+$", para):
            num, _, title = para.partition(". ")
            out.append(f'<h2 id="{num.lower()}"><span class="num">{num}.</span> '
                       f'{esc(title.title())}</h2>')
        else:
            out.append(f"<p>{prose(para)}</p>")
    out.append("</div>")
    return page("General Introduction — the Iliad, Wrath, Sing, Goddess",
                "The translator's introduction to this line-for-line Iliad: "
                "what the poem narrates, how its repetition works, the Greek "
                "text followed, the shape of the English line, and the plan "
                "of the edition.", "\n".join(out), "read/introduction.html",
                indexed=True)


def build_further_reading() -> str:
    """further_reading.txt: a two-line masthead, then paragraphs of three
    shapes: a section head (single all-caps line, optionally roman-numbered);
    an entry (a title line containing " · " separators, which may wrap onto
    further non-indented lines, followed by a 2-space indented body); and
    plain prose."""
    text = FURTHER.read_text(encoding="utf-8")
    paras = [p.splitlines() for p in re.split(r"\n\s*\n", text) if p.strip()]
    if paras and paras[0][0].strip() == "FOR FURTHER READING":
        paras = paras[1:]
    out = ['<nav class="booknav" data-pagefind-ignore>'
           '<a href="index.html">&lsaquo; Contents</a><span></span>'
           '<a href="names.html">Index &rsaquo;</a></nav>',
           '<header class="bookhead">',
           '<h1 data-pagefind-meta="title">For Further Reading</h1>',
           '<p class="argument">the Iliad’s ancient company: a guide</p>',
           '</header>', '<div class="prose">']
    if paras and paras[0][0].strip().lower().startswith("the iliad"):
        paras = paras[1:]  # the subtitle line; the argument carries it
    for para in paras:
        first = para[0]
        if len(para) == 1 and HEAD_RE.match(first.strip()):
            m = re.match(r"^([IVX]+)\.\s+(.*)$", first.strip())
            if m:
                out.append(f'<h2><span class="num">{m.group(1)}.</span> '
                           f'{esc(m.group(2).title())}</h2>')
            else:
                out.append(f"<h2>{esc(first.strip().title())}</h2>")
        elif " · " in first and not first.startswith(" "):
            i = 0
            while i < len(para) and not para[i].startswith(" "):
                i += 1
            title = " ".join(l.strip() for l in para[:i])
            body = " ".join(l.strip() for l in para[i:])
            out.append(f'<p class="fr-title">{prose(title)}</p>')
            if body:
                out.append(f'<p class="fr-body">{prose(body)}</p>')
        else:
            out.append(f'<p>{prose(" ".join(l.strip() for l in para))}</p>')
    out.append("</div>")
    return page("For Further Reading — the Iliad, Wrath, Sing, Goddess",
                "A guide to the Iliad's ancient company: the Epic Cycle, the "
                "tragedians, the parodies, Rome's answer, the eyewitness "
                "hoaxes, and the scholars, with what survives of each and "
                "where to find it.", "\n".join(out),
                "read/further-reading.html", indexed=True)


# ---------------------------------------------------------------------------
# Index of names & places (names.html), from index/index.md

EM_RE = re.compile(r"\*([^*]+)\*")
STRONG_RE = re.compile(r"\*\*([^*]+)\*\*")
# entry headline: **Headword** (Greek) · CAT — *Say:* pro-nun-see-AY-shun
ENTRY_HEAD_RE = re.compile(
    r"^\*\*(.+?)\*\*\s*(?:\((.*?)\))?\s*·\s*(\w+)(?:\s*—\s*\*Say:\*\s*(.+))?$")
FIELD_RE = re.compile(r"\*(Epithets|Also called|Kin|Kills|Killed by):\*")


def slugify(headword: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", headword.lower()).strip("-")


def entry_inline(text: str) -> str:
    """Escape, render **strong** / *em*, then link citations."""
    out = esc(text)
    out = STRONG_RE.sub(r"<strong>\1</strong>", out)
    out = EM_RE.sub(r"<em>\1</em>", out)
    return cite_links(out)


CAT_LABEL = {"MORTAL": "mortal", "GOD": "god", "PEOPLE": "people",
             "PLACE": "place", "OTHER": "other"}
CAT_CHIPS = [("", "All"), ("MORTAL", "Mortals"), ("GOD", "Gods"),
             ("PEOPLE", "Peoples"), ("PLACE", "Places"), ("OTHER", "Other")]


def parse_index_entries():
    """Return entries as dicts; index.md blocks are separated by --- rules."""
    entries = []
    for block in IDX.read_text(encoding="utf-8").split("\n---\n"):
        lines = [ln.rstrip() for ln in block.strip().splitlines()]
        head = next(((i, m) for i, ln in enumerate(lines)
                     if (m := ENTRY_HEAD_RE.match(ln))), None)
        if head is None:  # the file preamble carries no entry headline
            continue
        i, m = head
        headword, greek, cat, say = m.groups()
        if cat not in CAT_LABEL:
            raise SystemExit(f"index entry {headword}: unknown category {cat}")
        # entry prose is hard-wrapped; a field or refs line starts a new
        # logical line, everything else continues the previous one
        rest: list[str] = []
        for ln in lines[i + 1:]:
            if not ln.strip():
                continue
            starts = (FIELD_RE.match(ln) or ln.startswith("*See also:*")
                      or ln.startswith("**Refs:**"))
            if starts or not rest or rest[-1].startswith("**Refs:**") \
                    or rest[-1].startswith("*See also:*"):
                rest.append(ln.strip())
            else:
                rest[-1] += " " + ln.strip()
        entries.append({
            "headword": headword, "greek": greek or "", "cat": cat,
            "say": say or "", "slug": slugify(headword), "rest": rest,
        })
    slugs = [e["slug"] for e in entries]
    dupes = {s for s in slugs if slugs.count(s) > 1}
    if dupes:
        raise SystemExit(f"duplicate index slugs: {sorted(dupes)}")
    return entries


# see-also spellings that differ from the entry headword
SEE_ALSO_SPELLING: dict[str, str] = {}


def resolve_see_also(name: str, by_headword: dict[str, str]) -> str | None:
    """Slug for a see-also target: exact headword, headword without a
    parenthetical qualifier ("Ajax (the lesser)"), or a spelling variant."""
    name = SEE_ALSO_SPELLING.get(name, name)
    slug = by_headword.get(name)
    if slug is None:
        slug = by_headword.get(name.split(" (")[0])
    return slug


def render_entry(e: dict, by_headword: dict[str, str]) -> str:
    # filter key: headword, greek, and any "Also called" aliases
    also = next((ln for ln in e["rest"] if ln.startswith("*Also called:*")), "")
    key = html.escape(f'{e["headword"]} {e["greek"]} {also}'.lower(), quote=True)
    out = [f'<article class="entry" id="{e["slug"]}" data-cat="{e["cat"]}" '
           f'data-key="{key}">']
    grc = (f' <span class="grc" lang="grc">{esc(e["greek"])}</span>'
           if e["greek"] else "")
    out.append(f'<h3>{esc(e["headword"])}{grc}'
               f'<span class="cat">{CAT_LABEL[e["cat"]]}</span></h3>')
    if e["say"]:
        out.append(f'<p class="say">Say: {entry_inline(e["say"])}</p>')
    for ln in e["rest"]:
        if ln.startswith("*See also:*"):
            names = [n.strip(" .") for n in
                     ln[len("*See also:*"):].split(",") if n.strip(" .")]
            links = []
            for name in names:
                slug = resolve_see_also(name, by_headword)
                links.append(f'<a href="#{slug}">{esc(name)}</a>' if slug
                             else esc(name))
            out.append(f'<p class="ifield"><em>See also:</em> '
                       f'{", ".join(links)}.</p>')
        elif ln.startswith("**Refs:**"):
            out.append(f'<p class="irefs">{entry_inline(ln)}</p>')
        elif FIELD_RE.match(ln):
            out.append(f'<p class="ifield">{entry_inline(ln)}</p>')
        else:
            out.append(f'<p class="ibody">{entry_inline(ln)}</p>')
    out.append("</article>")
    return "\n".join(out)


NAMES_JS = """\
<script>
(function () {
  var q = document.getElementById('q');
  var chips = document.querySelectorAll('.chip');
  var entries = document.querySelectorAll('.entry');
  var groups = document.querySelectorAll('.lgroup');
  var count = document.getElementById('count');
  var total = entries.length;
  var cat = '';
  function apply() {
    var needle = q.value.trim().toLowerCase();
    var shown = 0;
    entries.forEach(function (el) {
      var ok = (!cat || el.dataset.cat === cat) &&
               (!needle || el.dataset.key.indexOf(needle) !== -1);
      el.hidden = !ok;
      if (ok) shown++;
    });
    groups.forEach(function (g) {
      g.hidden = !g.querySelector('.entry:not([hidden])');
    });
    count.textContent = (shown === total) ? total + ' entries'
                                          : shown + ' of ' + total + ' entries';
  }
  q.addEventListener('input', apply);
  chips.forEach(function (c) {
    c.addEventListener('click', function () {
      cat = c.dataset.cat;
      chips.forEach(function (o) { o.classList.toggle('on', o === c); });
      apply();
    });
  });
})();
</script>"""


def build_names() -> tuple[str, int]:
    entries = parse_index_entries()
    by_headword = {e["headword"]: e["slug"] for e in entries}
    unresolved = sorted({
        n.strip(" .") for e in entries for ln in e["rest"]
        if ln.startswith("*See also:*")
        for n in ln[len("*See also:*"):].split(",")
        if n.strip(" .") and not resolve_see_also(n.strip(" ."), by_headword)})
    if unresolved:
        print(f"  (names.html: {len(unresolved)} see-also names left unlinked: "
              f"{', '.join(unresolved[:8])}{'…' if len(unresolved) > 8 else ''})")

    out = ['<nav class="booknav" data-pagefind-ignore>'
           '<a href="index.html">&lsaquo; Contents</a><span></span><span></span></nav>',
           '<header class="bookhead">',
           '<h1 data-pagefind-meta="title">Index of Names &amp; Places</h1>',
           '<p class="argument">the poem’s principal persons, gods, peoples, '
           'and places — with pronunciations, epithets, kin, and linked '
           'citations</p>', '</header>']

    out.append('<div class="idxbar" data-pagefind-ignore>')
    out.append('<input id="q" type="search" placeholder="Filter by name…" '
               'autocomplete="off">')
    out.append('<div class="chips">')
    for val, label in CAT_CHIPS:
        on = " on" if val == "" else ""
        out.append(f'<button class="chip{on}" data-cat="{val}">{label}</button>')
    out.append(f'<span id="count">{len(entries)} entries</span>')
    out.append("</div>")
    letters = sorted({e["headword"][0].upper() for e in entries})
    out.append('<div class="letters">' + "".join(
        f'<a href="#{c}">{c}</a>' for c in letters) + "</div>")
    out.append("</div>")

    cur = ""
    for e in entries:
        letter = e["headword"][0].upper()
        if letter != cur:
            if cur:
                out.append("</section>")
            out.append(f'<section class="lgroup" id="{letter}">')
            out.append(f'<h2 class="letter" data-pagefind-ignore>{letter}</h2>')
            cur = letter
        out.append(render_entry(e, by_headword))
    out.append("</section>")
    out.append(
        '<p class="apparatus" data-pagefind-ignore>The index covers every '
        'figure of consequence: the several hundred men named once and '
        'killed in the same breath are catalogued for a later edition. '
        'Pronunciations give the traditional anglicized reading; stress '
        'falls on the capitalized syllable.</p>')
    out.append(NAMES_JS)

    return page("Index of Names & Places — the Iliad, Wrath, Sing, Goddess",
                f"The principal persons, gods, peoples, and places of the "
                f"Iliad: {len(entries)} entries with pronunciations, epithets, "
                f"kin, and line citations linked into the text.",
                "\n".join(out), "read/names.html", indexed=True), len(entries)


# ---------------------------------------------------------------------------
# Machine-readable mirror (docs/api/)


API_NOTE = (
    "Machine-readable mirror of a line-for-line English translation of "
    "Homer's Iliad. aligned-NN.jsonl is the parallel corpus for one book: "
    "one JSON object per verse line, {book, line, greek, en}, in the "
    "printed order of the Monro-Allen text, English verse only (no note "
    "markers). book-NN.txt is the full translation source for one book: a "
    "one-line argument, the translator's commentary, numbered verse lines "
    "('  123  text', one English line per Greek line, same numbering as the "
    "Greek) with bracketed [7] markers pointing into a notes section of "
    "scholarly endnotes, each opening with its (book.line) reference. "
    "registry.json is the index of names: the poem's principal persons, "
    "gods, peoples, and places, with category, aliases, note, and "
    "'book.line' refs. Cite passages as book.line, e.g. 6.146. "
    "Human-readable edition with line anchors: /read/book-NN.html#L123.")


def read_greek(n: int) -> list[tuple[int, str]]:
    rows = []
    for raw in (GREEK / f"book_{n:02d}.txt").read_text(
            encoding="utf-8").splitlines():
        m = VERSE_RE.match(raw)
        if m:
            rows.append((int(m.group(1)), m.group(2).strip()))
        elif raw.strip() and not re.match(r"^(BOOK \d+|=+)$", raw.strip()):
            raise SystemExit(f"books/book_{n:02d}.txt: unparsed line {raw!r}")
    return rows


def aligned_book(bk: dict) -> list[dict]:
    """Pair one book's Greek and English texts line by line.

    Both sources carry the Monro-Allen line numbers, and both lack the same
    six lines the printed text omits (9.458-461, 11.543, 14.269), so rows
    are keyed by number and emitted in the Greek file's order. English is
    the verse text with the [7] note markers stripped."""
    n = bk["n"]
    greek = read_greek(n)
    en = {it[1]: REF_RE.sub("", it[2]).rstrip()
          for st in bk["stanzas"] for it in st if it[0] == "v"}
    if len(greek) != len(en) or sorted(num for num, _ in greek) != sorted(en):
        raise SystemExit(f"book {n}: Greek/English line numbers disagree")
    return [{"book": n, "line": num, "greek": text, "en": en[num]}
            for num, text in greek]


def build_api(books: dict[int, dict], index_entries: int) -> None:
    OUT_API.mkdir(parents=True, exist_ok=True)
    (OUT_API / "registry.json").write_text(
        REGISTRY.read_text(encoding="utf-8"), encoding="utf-8")
    manifest_books = []
    total = 0
    total_notes = 0
    sample = None
    for n in range(1, 25):
        bk = books[n]
        src = SRC / f"book_{n:02d}.txt"
        (OUT_API / f"book-{n:02d}.txt").write_text(
            src.read_text(encoding="utf-8"), encoding="utf-8")
        rows = aligned_book(bk)
        total += len(rows)
        total_notes += len(bk["notes"])
        if n == 6:
            sample = next(r for r in rows if r["line"] == 146)
        (OUT_API / f"aligned-{n:02d}.jsonl").write_text(
            "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows),
            encoding="utf-8")
        last = max(it[1] for st in bk["stanzas"] for it in st if it[0] == "v")
        manifest_books.append({
            "book": n,
            "argument": bk["argument"],
            "lines": len(rows),
            "last_line": last,
            "notes": len(bk["notes"]),
            "aligned": f"{SITE}/api/aligned-{n:02d}.jsonl",
            "text": f"{SITE}/api/book-{n:02d}.txt",
            "html": f"{SITE}/read/book-{n:02d}.html",
        })
    if total != TOTAL_LINES:
        raise SystemExit(f"aligned corpus has {total} lines, "
                         f"expected {TOTAL_LINES}")
    manifest = {
        "title": SITE_NAME,
        "description": API_NOTE,
        "site": SITE,
        "repository": REPO,
        "license": ("English translation (the 'en' fields and the verse in "
                    "book-NN.txt): CC0 1.0 (public domain dedication). "
                    "Notes, commentary, and index: CC BY 4.0, (c) 2026 Chris "
                    "Duffy. Greek: Monro-Allen, Oxford Classical Text, 1920 "
                    "(public domain)."),
        "lines": total,
        "notes": total_notes,
        "registry": f"{SITE}/api/registry.json",
        "books": manifest_books,
    }
    (OUT_API / "manifest.json").write_text(
        json.dumps(manifest, indent=1, ensure_ascii=False) + "\n",
        encoding="utf-8")
    landing = (API_LANDING
               .replace("{CSSV}", css_version())
               .replace("{SITE}", SITE)
               .replace("{REPO}", REPO)
               .replace("{TOTAL}", f"{total:,}")
               .replace("{NOTES}", f"{total_notes:,}")
               .replace("{ENTRIES}", str(index_entries))
               .replace("{SAMPLE}", esc(json.dumps(sample, ensure_ascii=False))))
    (OUT_API / "index.html").write_text(landing, encoding="utf-8")
    build_crawler_files(total, total_notes)
    print(f"  {total:,} aligned lines, {total_notes:,} notes, "
          f"{index_entries} index entries")


def build_crawler_files(total: int, total_notes: int) -> None:
    """robots.txt and llms.txt at the site root.

    Neither restricts anything: robots.txt makes the welcome explicit, and
    llms.txt is the llmstxt.org convention: a short markdown orientation
    for language models, pointing them at the machine-readable layer."""
    (DOCS / "robots.txt").write_text(
        "# Everything here is meant to be read, by people and by machines.\n"
        "# Machine-readable layer (JSONL parallel corpus, JSON name index):\n"
        f"#   {SITE}/api/manifest.json\n"
        "User-agent: *\n"
        "Allow: /\n"
        f"Sitemap: {SITE}/sitemap.xml\n",
        encoding="utf-8")
    urls = ([f"{SITE}/", f"{SITE}/read/index.html",
             f"{SITE}/read/introduction.html"]
            + [f"{SITE}/read/book-{n:02d}.html" for n in range(1, 25)]
            + [f"{SITE}/read/names.html", f"{SITE}/read/further-reading.html",
               f"{SITE}/api/"])
    (DOCS / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"<url><loc>{u}</loc></url>\n" for u in urls)
        + "</urlset>\n",
        encoding="utf-8")
    (DOCS / "llms.txt").write_text(f"""\
# {SITE_NAME}

> A complete line-for-line English translation of Homer's Iliad: all
> {total:,} lines, one English line per Greek line on the numbering of the
> Monro-Allen Oxford text (1920), translated by a language model (Claude)
> from the Greek and human-edited. The English translation is public domain
> (CC0 1.0); the scholarly notes, the translator's commentary, the
> introduction, and the name index are CC BY 4.0; the Greek is Monro and
> Allen's text (public domain).

Cite passages as book.line (e.g. 6.146). Every verse of the reading
edition has a stable anchor: /read/book-06.html#L146.

## Machine-readable layer

- [manifest.json]({SITE}/api/manifest.json): describes every file below,
  with per-book URLs, line counts, and licensing
- [aligned-01.jsonl … aligned-24.jsonl]({SITE}/api/aligned-06.jsonl): the
  Greek-English parallel corpus, one JSON object per verse line
  ({{book, line, greek, en}})
- [book-01.txt … book-24.txt]({SITE}/api/book-06.txt): full translation
  source per book: argument, translator's commentary, verse, and
  {total_notes:,} line-keyed scholarly notes across the poem
- [registry.json]({SITE}/api/registry.json): the principal persons, gods,
  peoples, and places, with citations
- [About the API]({SITE}/api/): formats, examples, licensing detail

## Reading edition

- [Contents]({SITE}/read/index.html): all 24 books, one page each
- [General introduction]({SITE}/read/introduction.html)
- [Index of names & places]({SITE}/read/names.html)
- [For further reading]({SITE}/read/further-reading.html): the Iliad's
  ancient company
- [About & downloads]({SITE}/): EPUB, Kindle, PDF

## Companion

- [The Odyssey](https://theclaudyssey.com/): the same project's
  line-for-line Odyssey, with its own machine-readable layer at
  https://theclaudyssey.com/api/

## Source

- [Repository]({REPO}): full revision history, Greek source, build tools
""", encoding="utf-8")


API_LANDING = """\
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The text as data — the Iliad, Wrath, Sing, Goddess</title>
<meta name="description" content="The full translation, CC0, structured for machines: a Greek-English parallel corpus of the Iliad in JSONL, all {TOTAL} lines aligned to the Monro-Allen numbering, plus the name index as JSON.">
<link rel="canonical" href="{SITE}/api/">
<meta property="og:title" content="The text as data — the Iliad, Wrath, Sing, Goddess">
<meta property="og:description" content="A Greek-English parallel corpus of the Iliad in JSONL, all {TOTAL} lines aligned to the Monro-Allen numbering, CC0, plus the name index as JSON. No key, no auth: static files.">
<meta property="og:type" content="article">
<meta property="og:site_name" content="The Iliad — Wrath, Sing, Goddess">
<meta property="og:url" content="{SITE}/api/">
<meta property="og:image" content="{SITE}/social.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="stylesheet" href="../read/read.css?v={CSSV}">
<style>
  pre{background:rgba(30,11,21,.55); border:1px solid rgba(201,155,63,.3);
      border-radius:6px; padding:12px 14px; overflow-x:auto;
      font-size:.82rem; line-height:1.5}
  code{font-size:.9em}
  h2{font-weight:normal; font-variant:small-caps; letter-spacing:.06em;
     margin:34px 0 10px; color:var(--gold)}
  dl.files dt{font-family:ui-monospace,Consolas,monospace; margin-top:14px}
  dl.files dd{margin:2px 0 0 0; opacity:.9; font-size:.95rem}
  .lede{font-size:1.05rem}
</style>
</head>
<body>
<div class="meander"></div>
<div class="wrap">
<p class="site"><a href="../">The Iliad · wrath, sing, goddess</a></p>
<header class="bookhead"><h1>The text as data</h1>
<p class="argument">the full translation, CC0, structured for machines</p></header>

<p class="lede">Everything on this page is a stable, fetchable URL: a complete
Greek-English parallel corpus of the Iliad ({TOTAL} verse lines, aligned
one-to-one on the numbering of the Monro-Allen Oxford text), the full
translation source with its {NOTES} scholarly notes and the translator's
commentary on each book, and an index of the poem's principal persons, gods,
peoples, and places. The English is public domain (CC0). No key, no tracking,
no limits of ours: it is a directory of static files.</p>

<h2>The files</h2>
<dl class="files">
<dt><a href="manifest.json">manifest.json</a></dt>
<dd>describes everything below: per-book URLs, line counts, note counts,
book arguments, licensing. Start here if you are a script.</dd>
<dt><a href="aligned-06.jsonl">aligned-01.jsonl … aligned-24.jsonl</a></dt>
<dd>the parallel corpus, one book per file: one JSON object per verse line,
Greek and English paired.</dd>
<dt><a href="book-06.txt">book-01.txt … book-24.txt</a></dt>
<dd>the full translation source, one book per file: the argument, the
translator's commentary, the numbered verse, and the endnotes keyed to
line numbers.</dd>
<dt><a href="registry.json">registry.json</a></dt>
<dd>the name index: {ENTRIES} entries with category, aliases, a gloss, and every
line citation.</dd>
</dl>

<h2>The aligned corpus</h2>
<p>One JSON object per line, in the printed order. From
<a href="aligned-06.jsonl">aligned-06.jsonl</a>, Glaucus to Diomedes on the
generations of men:</p>
<pre>{SAMPLE}</pre>
<p>The alignment is exact and complete: every English line was translated
from, and verified one-to-one against, the Greek line it sits beside. The
numbering is Monro and Allen's own. Their printed text lacks six lines that
the traditional numbering counts (9.458–461, 11.543, 14.269), and the
translation marks those places rather than supplying them; both files
simply skip the numbers. That is why the poem's 24 books sum to {TOTAL}
lines, not 15,693.</p>

<h2>The name index</h2>
<p>The poem's principal figures, with their citations. From
<a href="registry.json">registry.json</a>:</p>
<pre>{"headword": "Abantes", "cat": "PEOPLE", "aliases": "",
 "note": "Euboean contingent under Elephenor",
 "count": 4, "books": [2, 4], "refs": ["2.536", "2.541", "2.542", "4.464"]}</pre>

<h2>Citing and linking</h2>
<p>Cite passages as <code>book.line</code> (e.g. <code>6.146</code>). Every
line of the reading edition has a stable anchor, so any citation can become
a link: <a href="../read/book-06.html#L146">wrath-sing-goddess.com/read/book-06.html#L146</a>.</p>

<h2>Examples</h2>
<p>Fetch one book's alignment and pull out one line:</p>
<pre>curl -s {SITE}/api/aligned-06.jsonl | grep '"line": 146'</pre>
<p>Load the whole poem as a dataset:</p>
<pre>import json, urllib.request
rows = []
for n in range(1, 25):
    url = f"{SITE}/api/aligned-{n:02d}.jsonl"
    with urllib.request.urlopen(url) as f:
        rows += [json.loads(line) for line in f]
assert len(rows) == 15687</pre>

<h2>Licensing</h2>
<p>Three layers, cleanly separated. The <strong>English translation</strong>
(every <code>en</code> field, and the verse in <code>book-NN.txt</code>) is
dedicated to the public domain under
<a href="https://creativecommons.org/publicdomain/zero/1.0/">CC0 1.0</a>:
use it for anything, including commercially, with no permission or credit
required. The <strong>Greek</strong> is the Oxford Classical Text of Monro
and Allen (3rd edition, 1920), in the public domain. The <strong>notes, the
translator's commentary, and the name index</strong> are © 2026 Chris Duffy,
<a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>.</p>

<h2>Provenance</h2>
<p>The translation was produced by a language model (Claude) from the Greek,
line by line, and edited by a human; the method and the full revision
history are public in <a href="{REPO}">the repository</a>. If you use this
corpus to train or evaluate models, the alignment and the numbering are the
contract: report passages as <code>book.line</code> and they will be
checkable against any edition of the Greek. The same project's Odyssey,
with the same machine-readable layer, is at
<a href="https://theclaudyssey.com/api/">theclaudyssey.com/api/</a>.</p>

</div>
<div class="meander"></div>
<footer><a href="../read/index.html">Contents</a> · <a href="../">About &amp; downloads</a></footer>
</body>
</html>
"""


CSS = """\
:root{
  --wine:#46192b; --wine-deep:#1e0b15; --bone:#ead9b4; --gold:#c99b3f;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
html,body{margin:0}
body{
  background:
    radial-gradient(ellipse at 50% 38%, rgba(0,0,0,0) 55%, rgba(12,4,8,.55) 100%),
    linear-gradient(#46192b, #331323 55%, #1e0b15);
  background-attachment:fixed;
  color:var(--bone);
  font-family:"Palatino Linotype","Book Antiqua",Palatino,Georgia,serif;
  line-height:1.55; min-height:100vh;
}
a{color:var(--gold)}
.wrap{max-width:680px; margin:0 auto; padding:0 22px}

.meander{height:26px; background-repeat:repeat-x; background-size:auto 26px;
  background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='40' height='26'><g fill='none' stroke='%23ead9b4' stroke-width='2.6'><path d='M0 4 H40'/><path d='M0 22 H40'/><path d='M28 22 V8 H11 V18 H19'/></g></svg>");
  opacity:.85; margin:14px 0 0}

.site{text-align:center; margin:18px 0 0; font-size:.8rem;
  letter-spacing:.14em; text-transform:uppercase}
.site a{color:var(--bone); opacity:.75; text-decoration:none}
.site a:hover{opacity:1; color:var(--gold)}

.booknav{display:flex; justify-content:space-between; gap:12px;
  margin:20px 0 0; font-size:.92rem}
.booknav.bottom{margin:34px 0 8px; border-top:1px solid rgba(201,155,63,.3);
  padding-top:16px}
.booknav a{text-decoration:none}
.booknav a:hover{text-decoration:underline}
.booknav span{min-width:70px}

.bookhead{text-align:center; margin:26px 0 30px}
.bookhead h1{font-weight:normal; letter-spacing:.12em; font-size:2.1rem;
  margin:0 0 .15em}
.argument{font-style:italic; opacity:.85; margin:0}

/* the translator's note on the book, collapsed under the argument */
.tnote{margin:-10px 0 28px; padding:0 14px; font-size:.92rem;
  background:rgba(201,155,63,.06); border:1px solid rgba(201,155,63,.25);
  border-radius:6px}
.tnote summary{cursor:pointer; padding:9px 0; color:var(--gold);
  font-variant:small-caps; letter-spacing:.06em; list-style-position:inside}
.tnote summary:hover{text-decoration:underline}
.tnote[open] summary{border-bottom:1px solid rgba(201,155,63,.2);
  margin-bottom:6px}
.tnote p{margin:0 0 .8em; opacity:.92}
.tnote p:last-child{padding-bottom:6px}

.verse{padding-left:2.6rem}
.stanza{margin:0 0 1.15em}
.v{margin:0; position:relative; padding-left:1.4em; text-indent:-1.4em}
.absent{margin:.3em 0; padding-left:1.4em; font-style:italic; opacity:.6;
  font-size:.9em}
.ln{position:absolute; left:-3.4rem; top:.32em; width:2.6rem;
  text-align:right; font-size:.72em; color:var(--gold); opacity:.55;
  text-decoration:none; text-indent:0}
.ln:hover{opacity:1}
/* every line has a permalink; the non-fifth ones surface on hover only,
   and not at all on touch screens (no hover, and an invisible tap target
   in the gutter would just cause stray jumps) */
.ln.ghost{opacity:0}
.v:hover .ln.ghost{opacity:.55}
.v:hover .ln.ghost:hover{opacity:1}
@media (hover:none){.ln.ghost{display:none}}
.copied{position:absolute; z-index:9; transform:translateY(-130%);
  font-size:.7rem; font-variant:small-caps; letter-spacing:.08em;
  color:var(--gold); background:rgba(30,11,21,.95);
  border:1px solid rgba(201,155,63,.5); border-radius:10px;
  padding:2px 9px; pointer-events:none; white-space:nowrap}
.v:target, .note:target{background:rgba(201,155,63,.14); border-radius:3px}
.fnref{text-decoration:none; padding:0 .08em}
.fnref sup{font-size:.68em}

.notes{margin-top:40px; border-top:1px solid rgba(201,155,63,.3);
  padding-top:6px}
.notes h2{font-weight:normal; font-variant:small-caps; letter-spacing:.06em;
  color:var(--gold); font-size:1.25rem}
.note{font-size:.92rem; opacity:.92; margin:0 0 .85em;
  padding-left:1.6em; text-indent:-1.6em}
.nnum{color:var(--gold); font-size:.8em; vertical-align:.25em}
.nline{font-variant:small-caps; text-decoration:none; white-space:nowrap}
.nline:hover{text-decoration:underline}
.back{text-decoration:none}
.cite{text-decoration:none; white-space:nowrap}
.cite:hover{text-decoration:underline}

/* the introduction and the further-reading guide */
.prose p{margin:0 0 1em}
.prose h2{font-weight:normal; font-variant:small-caps; letter-spacing:.06em;
  color:var(--gold); font-size:1.3rem; margin:36px 0 12px;
  border-bottom:1px solid rgba(201,155,63,.3); padding-bottom:4px}
.prose h2 .num{opacity:.7; margin-right:.3em}
.fr-title{margin:18px 0 2px; color:var(--gold)}
.fr-body{margin:0 0 1em; font-size:.95rem; opacity:.92; padding-left:1.2em}

.toc{list-style:none; margin:0; padding:0}
.toc li{margin:0 0 2px}
.toc a{display:flex; gap:14px; align-items:baseline; padding:9px 12px;
  text-decoration:none; color:var(--bone); border-radius:5px;
  border:1px solid transparent}
.toc a:hover{background:rgba(201,155,63,.1); border-color:rgba(201,155,63,.35)}
.toc b{color:var(--gold); font-weight:normal; letter-spacing:.06em;
  white-space:nowrap; min-width:5.4em}
.toc span{font-style:italic; opacity:.85; font-size:.95rem}

.apparatus{margin:14px 0 8px; padding:12px 14px; font-size:.95rem;
  background:rgba(201,155,63,.07); border:1px solid rgba(201,155,63,.3);
  border-radius:6px}
.toc + .apparatus{margin-top:26px}

footer{text-align:center; font-size:.8rem; opacity:.7; padding:20px 0 40px}

/* ---- site search (Pagefind default UI, re-themed) ---- */
#search{margin:6px 0 22px;
  --pagefind-ui-scale:.9;
  --pagefind-ui-primary:var(--gold);
  --pagefind-ui-text:var(--bone);
  --pagefind-ui-background:rgba(0,0,0,.25);
  --pagefind-ui-border:rgba(201,155,63,.45);
  --pagefind-ui-tag:rgba(201,155,63,.18);
  --pagefind-ui-border-width:1px;
  --pagefind-ui-border-radius:5px;
  --pagefind-ui-font:inherit}
#search .pagefind-ui__search-input{color:var(--bone)}
#search .pagefind-ui__search-input::placeholder{color:var(--bone); opacity:.55}
#search .pagefind-ui__result{border-color:rgba(201,155,63,.25)}
#search .pagefind-ui__result-link{color:var(--gold)}
#search .pagefind-ui__result-excerpt{color:var(--bone); opacity:.9}
#search mark{background:rgba(201,155,63,.4); color:inherit; border-radius:2px}
#search .pagefind-ui__button{background:rgba(201,155,63,.1); color:var(--gold);
  border:1px solid rgba(201,155,63,.45)}
#search .pagefind-ui__message{color:var(--bone); opacity:.8}

/* ---- index of names & places ---- */
.booknav .mid{min-width:0}
.idxbar{position:sticky; top:0; z-index:5; background:rgba(30,11,21,.96);
  margin:0 -22px 18px; padding:12px 22px 10px;
  border-bottom:1px solid rgba(201,155,63,.3)}
.idxbar input{width:100%; padding:9px 12px; font:inherit; color:var(--bone);
  background:rgba(0,0,0,.25); border:1px solid rgba(201,155,63,.45);
  border-radius:5px}
.idxbar input:focus{outline:none; border-color:var(--gold)}
.chips{display:flex; gap:7px; flex-wrap:wrap; align-items:baseline;
  margin-top:9px}
.chip{font:inherit; font-size:.8rem; color:var(--bone); cursor:pointer;
  background:rgba(0,0,0,.2); border:1px solid rgba(201,155,63,.35);
  border-radius:12px; padding:2px 11px}
.chip:hover{border-color:var(--gold)}
.chip.on{background:rgba(201,155,63,.25); color:var(--gold);
  border-color:var(--gold)}
#count{margin-left:auto; font-size:.8rem; opacity:.65; white-space:nowrap}
.letters{margin-top:9px; font-size:.85rem; letter-spacing:.1em}
.letters a{text-decoration:none; padding:0 2px}
.letters a:hover{text-decoration:underline}
.letter{font-weight:normal; color:var(--gold); font-size:1.5rem;
  letter-spacing:.1em; border-bottom:1px solid rgba(201,155,63,.3);
  margin:30px 0 14px; scroll-margin-top:120px}
.entry{margin:0 0 20px; scroll-margin-top:120px}
.entry:target{background:rgba(201,155,63,.1); border-radius:5px;
  padding:6px 10px; margin-left:-10px; margin-right:-10px}
.entry h3{font-weight:normal; font-size:1.12rem; margin:0 0 2px;
  color:var(--gold); display:flex; align-items:baseline; gap:.4em;
  flex-wrap:wrap}
.entry h3 .grc{opacity:.8; font-size:.95em; color:var(--bone)}
.entry h3 .cat{margin-left:auto; flex-shrink:0; white-space:nowrap;
  font-size:.68rem; letter-spacing:.1em;
  text-transform:uppercase; opacity:.55; color:var(--bone);
  border:1px solid rgba(234,217,180,.35); border-radius:10px;
  padding:1px 8px}
.say{margin:0 0 6px; font-size:.85rem; color:var(--gold); opacity:.85;
  font-variant:small-caps; letter-spacing:.04em}
.ibody{margin:0 0 6px; font-size:.95rem}
.ifield{margin:0 0 4px; font-size:.88rem; opacity:.88}
.irefs{margin:0 0 4px; font-size:.85rem; opacity:.85}

@media (max-width:560px){
  .wrap{padding:0 14px}
  .verse{padding-left:2.1rem}
  .ln{left:-2.6rem; width:2rem}
  .toc b{min-width:4.6em}
  .idxbar{margin:0 -14px 16px; padding:10px 14px 8px}
}
"""


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "read.css").write_text(CSS, encoding="utf-8")
    books: dict[int, dict] = {}
    for n in range(1, 25):
        bk = parse_book(SRC / f"book_{n:02d}.txt")
        if bk["n"] != n:
            raise SystemExit(f"book_{n:02d}.txt says BOOK {bk['n']}")
        books[n] = bk
        (OUT / f"book-{n:02d}.html").write_text(build_book(bk), encoding="utf-8")
        print(f"book-{n:02d}.html")
    (OUT / "index.html").write_text(build_contents(books), encoding="utf-8")
    (OUT / "introduction.html").write_text(build_introduction(), encoding="utf-8")
    (OUT / "further-reading.html").write_text(build_further_reading(),
                                              encoding="utf-8")
    names_html, n_entries = build_names()
    (OUT / "names.html").write_text(names_html, encoding="utf-8")
    build_api(books, n_entries)
    print("index.html + introduction.html + further-reading.html + names.html "
          "+ read.css + api/")
    print("now refresh the search bundle:  npx -y pagefind --site docs")


if __name__ == "__main__":
    main()
