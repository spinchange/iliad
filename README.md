# The Iliad — a line-for-line translation

A complete line-for-line English translation of Homer's Iliad, read online at
[wrath-sing-goddess.com](https://wrath-sing-goddess.com/). Companion to the
same project's Odyssey, [theclaudyssey.com](https://theclaudyssey.com/)
([repository](https://github.com/spinchange/claudyssey)).

- **From the Greek of** Homer
- **Translated by** Claude (Fable 5)
- **Edited and produced by** Chris Duffy

The EPUB records these as EPUB3 creators with MARC relator roles (`aut`, `trl`,
`edt`) and states them on the title page.

## Source text

The Greek is the Oxford Classical Text of Monro and Allen (*Homeri Opera*, 3rd
edition, 1920), public domain, with the traditional line numbering.

- `books/book_01.txt` … `book_24.txt` — the Greek, one book per file, one
  numbered line per verse (`    1  μῆνιν ἄειδε θεὰ …`)
- `iliad_greek_full.txt` — the whole poem in one file
- `apparatus/`, `disputed_lines.md` — the textual notes that inform the
  translation's own notes on atheteses and variants

15,687 lines. The printed text is followed throughout, including passages the
ancient critics athetized. It lacks six lines that the traditional numbering
counts — **9.458–461, 11.543, 14.269** — and the translation marks those
places in the verse rather than supplying them; the numbering skips them.

## Translation

**Complete: all 24 books, 15,687 lines — every line verified one-to-one
against the Greek**, followed by a full fidelity audit (`audit/`).

- `translation/book_01.txt` … `book_24.txt` — one file per book, plain text in
  four rule-delimited parts: the book number and a one-line argument, the
  translator's commentary on the book, the verse (one English line per Greek
  line, keyed to the same line numbers, with bracketed `[7]` note markers),
  and the notes (`[7] (1.123) …`, one per marker, 829 across the poem).
- `translation/introduction.txt` — the General Introduction: the poem, the
  art of repetition, the Greek text, the English line, this edition.
- `translation/CONVENTIONS.md` — the authoritative register of fixed
  renderings: Homer's repeated epithets, speech-formulas, and whole-line
  refrains recur verbatim in the English wherever the Greek repeats, and this
  file records every fixed choice. `tools/check_formulas.py` checks the
  high-value formulas against the Greek mechanically.
- `further_reading.txt` — *For Further Reading*: a guide to the Iliad's
  ancient company (the Cycle, the tragedians, the parodies, Rome's answer,
  the hoaxes, the scholars).

The voice is a loose five-to-six-beat unrhymed line. Names use familiar
Latinate spellings. The theme words are kept rigid so their economy stays
visible: *mēnis* is always "wrath," *timē* "honor," *geras* "prize," *atē*
"blindness." δμώς/δμῳή are "slave/slave-woman" throughout, as in the Odyssey.

`TRANSLATION_WORKFLOW.md` describes how the books were produced and checked;
`tools/lookup.py` and `tools/beatcheck.py` are the working tools.

## Index of names and places

`index/index.md` is the index of the poem's principal persons, gods, peoples,
and places — 302 entries, each with an anglicized pronunciation (*Say:*),
epithets, aliases, kin, kills, and real line citations. It is built by a
four-phase pipeline ported from the Odyssey project and documented in
`index/README.md`; `index/registry.json` is the machine-readable form. The
several hundred men named once and killed in the same breath are listed in
`index/tail-unclassified.md` for a later edition.

## EPUB, Kindle, and PDF

`tools/build_epub.py` builds the EPUB with Pandoc: title page, proem, the
General Introduction, a note on the text, the twenty-four books (each with
its argument and a link to the translator's note, the verse with line
anchors, and its endnotes with working back-links), then the translator's
notes on the books, *For Further Reading*, and the index with every
`book.line` citation linked into the verse. Gentium Plus is embedded for the
Greek.

```powershell
python tools\build_epub.py                 # epub-build/iliad.epub
python tools\check_epub.py epub-build\iliad.epub
ebook-convert epub-build\iliad.epub epub-build\iliad.azw3
ebook-convert epub-build\iliad.epub epub-build\iliad.pdf --paper-size a5 --pdf-page-numbers
```

The built files are attached to each
[release](https://github.com/spinchange/iliad/releases), which is where the
site's download buttons point.

## Web edition

`tools/build_web.py` regenerates the reading edition in `docs/` (served by
GitHub Pages at wrath-sing-goddess.com): one page per book with line
anchors, the translator's note collapsed under the argument, and endnotes; a
contents page with site search; the introduction and the further-reading
guide; and `names.html` — the index rendered with category, letter, and
text filtering, every `book.line` citation deep-linked into the text
(`book-06.html#L146`).

Site search is [Pagefind](https://pagefind.app), fully static (the bundle
lives in `docs/pagefind/`; `pagefind.yml` disables stemming so name searches
stay exact).

The build also emits `docs/api/` — a machine-readable mirror for scripts and
language models, served at `wrath-sing-goddess.com/api/` with its own landing
page: `manifest.json`, `registry.json`, `book-NN.txt` (each book's
translation source, verbatim), and `aligned-NN.jsonl` — the Greek↔English
parallel corpus, one JSON object per verse line (`{book, line, greek, en}`).
The build fails if the aligned corpus doesn't come out to exactly 15,687
lines. `docs/llms.txt`, `robots.txt`, and `sitemap.xml` point crawlers at it.

Every generated page carries canonical, Open Graph, and Twitter-card
metadata pointing at `docs/social.jpg` (the 1200×630 shield card from
`art/`); `docs/cover.jpg` is the cover for the landing page. In the reading
edition every verse line's gutter number is a copyable permalink.

After any rebuild:

```powershell
python tools\build_web.py
npx -y pagefind --site docs
```

## Artwork

`art/` carries the cover and social artwork — the Shield of Achilles, the
poem's own ekphrasis at 18.478–608, drawn as concentric registers in the
same visual system as the Odyssey's ship — and twenty-four per-book plates.
See `art/README.md`.

## Audiobook

`AUDIOBOOK_WORKFLOW.md` and `tools/build_audiobook.py` are the pilot
pipeline: every TTS response is a candidate take, transcribed independently
and aligned against the exact input before it is accepted. `audiobook/`
holds the pinned configuration and pronunciation registry; the generated
candidates in `audiobook-build/` are not tracked.

## Licensing

**The English translation** (the 15,687 verse lines in
`translation/book_*.txt`) is dedicated to the public domain under
[CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/). Copy it,
print it, teach it, set it to music, remix it; no permission or credit is
required, for any purpose including commercial use.

**The apparatus** — the notes and the translator's commentary in those same
files, the introduction, *For Further Reading*, the index of names and places
(`index/`), and the register of fixed renderings (`translation/CONVENTIONS.md`)
— is © 2026 Chris Duffy, licensed
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/): use it freely
with attribution.

**The Greek**: Monro and Allen's 1920 text is in the public domain.

The EPUB embeds Gentium Plus under the SIL Open Font License; the license text
travels with the font in `epub-build/assets/GentiumPlus-OFL.txt`.
