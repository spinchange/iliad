#!/usr/bin/env python3
"""Build the paperback case wrap — back cover, spine, and front cover as a
single flat landscape PDF, to a print-on-demand supplier's spec.

Ported from the Odyssey project's tools/build_wrap.py; the geometry and
the checks are the same, the artwork is the Iliad's (the Shield of
Achilles from art/iliad-cover.svg, redrawn to the front panel).

Lulu's spec for a 6x9 paperback:

    panels           6.125 in each     = 6 in trim + 0.125 in bleed
    height           9.25 in           = 9 in trim + bleed top and bottom
    spine (in)       pages / 444 + 0.06      (every paper stock)
    overall width    2 x 6.125 + spine

    +---------------------------+-------+---------------------------+
    |        back cover         | spine |       front cover         |
    +---------------------------+-------+---------------------------+

The page count is read from the built interior
(print-build/iliad-print-6x9.pdf) unless --pages or --spine is given.

Print requirements this targets, all verified by tools/check_wrap.py:
  * exactly 1 page at the given size
  * all fonts embedded and subsetted
  * flattened — no optional content groups, no annotations
  * full bleed to all four edges
  * no raster anywhere: pattern fills are expanded into explicit tiles
    before rendering (calibre's renderer would rasterize them at 72 ppi).

Usage:
    python tools/build_wrap.py                   # spine from the built interior
    python tools/build_wrap.py --pages 812       # spine from a page count
    python tools/build_wrap.py --spine 1.89      # Lulu's figure, if it differs
    python tools/build_wrap.py --no-url          # omit the site URL
"""
from __future__ import annotations
import argparse
import math
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ART = ROOT / "art"
WORK = ROOT / "print-build" / "wrap-work"
INTERIOR = ROOT / "print-build" / "iliad-print-6x9.pdf"

EBOOK_CONVERT = (
    os.environ.get("EBOOK_CONVERT")
    or shutil.which("ebook-convert")
    or r"C:\Program Files\Calibre2\ebook-convert.exe"
)

# ---- spec ---------------------------------------------------------------
WRAP_H_IN = 9.25
BLEED_IN = 0.125
PANEL_IN = 6.125
PAGES_PER_INCH = 444      # Lulu's bulk for every paperback stock
SPINE_ADD_IN = 0.06       # Lulu's fixed allowance on top of the page block


def spine_for(pages: int) -> float:
    """Lulu's paperback spine width for a page count, to their precision."""
    return round(pages / PAGES_PER_INCH + SPINE_ADD_IN, 3)


def wrap_width(spine_in: float) -> float:
    return round(2 * PANEL_IN + spine_in, 3)


def interior_pages() -> int | None:
    """The page count of the built interior, if it exists."""
    if not INTERIOR.exists():
        return None
    try:
        from pypdf import PdfReader
    except ImportError:
        return None
    return len(PdfReader(str(INTERIOR)).pages)


UPI = 100.0   # SVG user units per inch

# Palette, from art/iliad-cover.svg.
WINE_TOP = "#46192b"
WINE_MID = "#331323"
WINE_BOT = "#1e0b15"
BONE = "#ead9b4"
GOLD = "#c99b3f"

SERIF = ("'Palatino Linotype','Book Antiqua',Palatino,Georgia,serif")

SITE_URL = "wrath-sing-goddess.com"

BLURB = (
    "A complete line-for-line English translation of Homer\u2019s "
    "<tspan font-style=\"italic\">Iliad</tspan> \u2014 all 24 books, "
    "15,687 lines, with one English line for every line of the Greek and "
    "the same line numbering throughout, so any passage can be cited as "
    "book.line and found in either language."
)

BLURB2 = (
    "The edition carries a scholarly apparatus of 829 line notes, the "
    "translator\u2019s commentary on every book, a guide to the poem\u2019s "
    "ancient company, and an index of its principal persons, gods, "
    "peoples, and places."
)

BLURB3 = (
    "Translated by Claude (Fable 5), a large language model, under the "
    "editorial direction of Chris Duffy. The translation is dedicated to "
    "the public domain under CC0 1.0: no permission or attribution is "
    "required for any use."
)

EPIGRAPH_GRC = ("\u03bc\u1fc6\u03bd\u03b9\u03bd \u1f04\u03b5\u03b9\u03b4\u03b5 "
                "\u03b8\u03b5\u1f70 \u03a0\u03b7\u03bb\u03b7\u03ca\u03ac\u03b4\u03b5\u03c9 "
                "\u1f08\u03c7\u03b9\u03bb\u1fc6\u03bf\u03c2")


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def strip_markup(s: str) -> str:
    out, depth = [], 0
    for ch in s:
        if ch == "<":
            depth += 1
        elif ch == ">":
            depth = max(0, depth - 1)
        elif depth == 0:
            out.append(ch)
    return "".join(out)


# Mean glyph advance as a fraction of the font size for this Palatino text,
# measured on the Odyssey wrap's rendered PDF.
ADVANCE_RATIO = 0.50


def wrap_text(text: str, width_units: float, size: float) -> list[str]:
    """Greedy wrap to a pixel width, not a character count."""
    limit = width_units / (size * ADVANCE_RATIO)
    words, lines, cur = text.split(" "), [], ""
    for w in words:
        probe = (cur + " " + w).strip()
        if len(strip_markup(probe)) > limit and cur:
            lines.append(cur)
            cur = w
        else:
            cur = probe
    if cur:
        lines.append(cur)
    return lines


def build_svg(spine_in: float, with_url: bool) -> str:
    W = wrap_width(spine_in) * UPI
    H = WRAP_H_IN * UPI
    P = PANEL_IN * UPI
    S = spine_in * UPI
    B = BLEED_IN * UPI

    back_x = 0.0
    spine_x = P
    front_x = P + S
    safe = 0.375 * UPI          # 3/8in from every trimmed edge

    o: list[str] = []
    add = o.append

    add(f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {W:.2f} {H:.2f}" width="{W:.2f}" height="{H:.2f}" '
        f'role="img" aria-label="Paperback case wrap for Homer\u2019s Iliad: '
        f'back cover, spine, and front cover.">')

    add('<defs>')
    add(f'<linearGradient id="wine" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{WINE_TOP}"/>'
        f'<stop offset="0.55" stop-color="{WINE_MID}"/>'
        f'<stop offset="1" stop-color="{WINE_BOT}"/></linearGradient>')
    add('<radialGradient id="vigF" cx="0.5" cy="0.42" r="0.85">'
        '<stop offset="0.6" stop-color="#000000" stop-opacity="0"/>'
        '<stop offset="1" stop-color="#0c0408" stop-opacity="0.5"/>'
        '</radialGradient>')
    # the back and spine bands, at the wrap's scale (1in = 100u)
    add(f'<pattern id="meander" width="50" height="50" patternUnits="userSpaceOnUse">'
        f'<g fill="none" stroke="{BONE}" stroke-width="4.5">'
        f'<path d="M0 6.25 H50"/><path d="M0 42.5 H50"/>'
        f'<path d="M35 42.5 V13.75 H13.75 V32.5 H23.75"/></g></pattern>')
    add(f'<pattern id="dots" width="18.75" height="15" patternUnits="userSpaceOnUse">'
        f'<circle cx="7.5" cy="7.5" r="3.25" fill="{BONE}"/></pattern>')
    add('</defs>')

    # ground across the whole wrap, so the fold has no seam
    add(f'<rect x="0" y="0" width="{W:.2f}" height="{H:.2f}" fill="url(#wine)"/>')
    add(f'<rect x="{front_x:.2f}" y="0" width="{P:.2f}" height="{H:.2f}" fill="url(#vigF)"/>')

    # ---- FRONT COVER: the cover design at 800x1200 for a 6x9 trim, scaled
    # by the trim and placed inside the bleed so it bleeds on the outer edges.
    fs = (6.0 * UPI) / 800.0
    fx = front_x + B
    fy = B
    add(f'<g transform="translate({fx:.3f},{fy:.3f}) scale({fs:.6f})">')
    add(front_panel_svg())
    add('</g>')

    # ---- SPINE
    cx = spine_x + S / 2
    add('<g>')
    for xx in (spine_x + 9, spine_x + S - 9):
        add(f'<line x1="{xx:.2f}" y1="{safe:.2f}" x2="{xx:.2f}" y2="{H - safe:.2f}" '
            f'stroke="{BONE}" stroke-width="1" opacity="0.30"/>')
    add(f'<g transform="translate({cx:.2f},{H / 2:.2f}) rotate(90)" '
        f'text-anchor="middle" font-family="{SERIF}">')
    add(f'<text x="0" y="-13" font-size="46" fill="{BONE}" letter-spacing="2">'
        f'HOMER\u2019S ILIAD</text>')
    add(f'<text x="0" y="26" font-size="22" fill="{GOLD}" letter-spacing="3" '
        f'opacity="0.95">TRANSLATED BY CLAUDE</text>')
    add('</g>')
    # the spine caps: one whole tile row each, on the tile grid (see TILE
    # below), inside the safe area at either end
    for yy in (math.ceil((safe + 8) / 50) * 50, math.floor((H - safe - 8 - 50) / 50) * 50):
        add(f'<rect x="{spine_x + 13:.2f}" y="{yy:.2f}" width="{S - 26:.2f}" '
            f'height="50" fill="url(#meander)" opacity="0.85"/>')
    add('</g>')

    # ---- BACK COVER
    fr_x = back_x + B + 24
    fr_y = B + 24
    fr_w = P - 2 * B - 48
    fr_h = H - 2 * B - 48
    pad = 46
    bx0 = fr_x + pad
    bx1 = fr_x + fr_w - pad
    bw = bx1 - bx0
    add('<g>')
    add(f'<rect x="{fr_x:.2f}" y="{fr_y:.2f}" width="{fr_w:.2f}" height="{fr_h:.2f}" '
        f'fill="none" stroke="{BONE}" stroke-width="2.5" opacity="0.55"/>')

    # The meander tile is 50u square and is laid from the user-space origin,
    # so a band shows exactly one whole row of it only when it is 50u tall
    # and starts on a multiple of 50; anything else cuts the pattern.
    TILE = 50
    band_h = TILE
    top_band_y = round((fr_y + 30) / TILE) * TILE
    imprint_h = 70 if with_url else 34
    imprint_y = fr_y + fr_h - 30 - imprint_h
    low_band_h = TILE
    low_band_y = math.floor((imprint_y - 34 - low_band_h) / TILE) * TILE
    rule_y = low_band_y - 30
    epi_y = top_band_y + band_h + 62
    rule2_y = epi_y + 30
    text_top = rule2_y + 46
    text_bottom = rule_y - 30
    avail = text_bottom - text_top

    add(f'<rect x="{bx0:.2f}" y="{top_band_y:.2f}" width="{bw:.2f}" '
        f'height="{band_h}" fill="url(#meander)" opacity="0.9"/>')
    add(f'<g font-family="{SERIF}" fill="{BONE}">')
    add(f'<text x="{bx0 + bw / 2:.2f}" y="{epi_y:.2f}" font-size="26" '
        f'font-style="italic" text-anchor="middle" opacity="0.72">{EPIGRAPH_GRC}</text>')
    add(f'<line x1="{bx0 + bw / 2 - 90:.2f}" y1="{rule2_y:.2f}" '
        f'x2="{bx0 + bw / 2 + 90:.2f}" y2="{rule2_y:.2f}" '
        f'stroke="{GOLD}" stroke-width="1.2" opacity="0.85"/>')

    # fit the three paragraphs by stepping the type down until they do
    for scale in (1.0, 0.94, 0.88, 0.82, 0.76, 0.70):
        sizes = [22 * scale, 20 * scale, 19 * scale]
        leads = [s * 1.34 for s in sizes]
        gaps = [s * 0.75 for s in sizes]
        blocks = [wrap_text(t, bw, s) for t, s in zip((BLURB, BLURB2, BLURB3), sizes)]
        total = sum(len(b) * l for b, l in zip(blocks, leads)) + sum(gaps[:-1])
        if total <= avail:
            break
    y = text_top
    for lines, size, lead, gap, op in zip(blocks, sizes, leads, gaps, (0.92, 0.80, 0.72)):
        for line in lines:
            add(f'<text x="{bx0:.2f}" y="{y:.2f}" font-size="{size:.2f}" '
                f'opacity="{op}">{line}</text>')
            y += lead
        y += gap
    add('</g>')

    # the shield register's rules and dots, echoing the front
    add(f'<line x1="{bx0:.2f}" y1="{rule_y:.2f}" x2="{bx1:.2f}" y2="{rule_y:.2f}" '
        f'stroke="{BONE}" stroke-width="2" opacity="0.75"/>')
    add(f'<rect x="{bx0 + 10:.2f}" y="{rule_y + 8:.2f}" width="{bw - 20:.2f}" '
        f'height="13" fill="url(#dots)" opacity="0.75"/>')
    add(f'<rect x="{bx0:.2f}" y="{low_band_y:.2f}" width="{bw:.2f}" '
        f'height="{low_band_h}" fill="url(#meander)" opacity="0.75"/>')

    add(f'<g font-family="{SERIF}" fill="{BONE}" text-anchor="middle">')
    add(f'<text x="{bx0 + bw / 2:.2f}" y="{imprint_y + 20:.2f}" font-size="18" '
        f'opacity="0.62" letter-spacing="3">TRANSLATION CC0 \u00b7 APPARATUS CC BY 4.0</text>')
    if with_url:
        add(f'<text x="{bx0 + bw / 2:.2f}" y="{imprint_y + 60:.2f}" font-size="26" '
            f'fill="{GOLD}" letter-spacing="2">{esc(SITE_URL)}</text>')
    add('</g>')
    add('</g>')
    add('</svg>')
    return "\n".join(o)


def front_panel_svg() -> str:
    """The front cover artwork in its own 800x1200 space: art/iliad-cover.svg
    minus its background rects and grain filter (the wrap paints one ground
    across all three panels, and feTurbulence has no vector form)."""
    return f'''
  <rect x="36" y="36" width="728" height="1128" fill="none" stroke="{BONE}" stroke-width="2.5" opacity="0.9"/>
  <rect x="48" y="48" width="704" height="1104" fill="none" stroke="{BONE}" stroke-width="1" opacity="0.4"/>
  <rect x="80" y="72" width="640" height="40" fill="url(#meanderF)"/>
  <g font-family="{SERIF}" text-anchor="middle">
    <text x="400" y="208" font-size="27" font-style="italic" fill="{BONE}" opacity="0.8">{EPIGRAPH_GRC}</text>
    <text x="400" y="246" font-size="19" fill="{BONE}" opacity="0.55">Sing, goddess, the wrath of Peleus\u2019 son Achilles</text>
  </g>
  <g font-family="{SERIF}" text-anchor="middle" fill="{BONE}">
    <text x="400" y="356" font-size="44" textLength="320" lengthAdjust="spacingAndGlyphs">HOMER\u2019S</text>
    <text x="400" y="454" font-size="86" textLength="440" lengthAdjust="spacingAndGlyphs">ILIAD</text>
    <line x1="280" y1="486" x2="520" y2="486" stroke="{GOLD}" stroke-width="1.3" opacity="0.9"/>
    <text x="400" y="526" font-size="30" fill="{GOLD}" textLength="220" lengthAdjust="spacingAndGlyphs">\u0399\u039b\u0399\u0391\u03a3</text>
    <text x="400" y="568" font-size="18" letter-spacing="2" fill-opacity="0.78">LINE FOR LINE TRANSLATION BY FABLE 5</text>
  </g>
  <line x1="90" y1="600" x2="710" y2="600" stroke="{BONE}" stroke-width="2"/>
  <rect x="100" y="606" width="600" height="12" fill="url(#dotsF)"/>
  <line x1="90" y1="626" x2="710" y2="626" stroke="{BONE}" stroke-width="2"/>
  <g>
    <circle cx="400" cy="808" r="164" fill="none" stroke="{BONE}" stroke-width="3.4"/>
    <circle cx="400" cy="808" r="158" fill="none" stroke="{BONE}" stroke-width="1.4" opacity="0.55"/>
    <circle cx="400" cy="808" r="132" fill="none" stroke="{BONE}" stroke-width="2.8"/>
    <path d="M400.00 663.00 Q415.68 648.77 428.29 665.79 Q437.74 683.60 455.49 674.04 Q475.42 666.89 480.56 687.44 Q482.47 707.51 502.53 705.47 Q523.68 706.50 520.56 727.44 Q514.65 746.72 533.96 752.51 Q553.11 761.55 542.21 779.71 Q529.37 795.26 545.00 808.00 Q559.23 823.68 542.21 836.29 Q524.40 845.74 533.96 863.49 Q541.11 883.42 520.56 888.56 Q500.49 890.47 502.53 910.53 Q501.50 931.68 480.56 928.56 Q461.28 922.65 455.49 941.96 Q446.45 961.11 428.29 950.21 Q412.74 937.37 400.00 953.00 Q384.32 967.23 371.71 950.21 Q362.26 932.40 344.51 941.96 Q324.58 949.11 319.44 928.56 Q317.53 908.49 297.47 910.53 Q276.32 909.50 279.44 888.56 Q285.35 869.28 266.04 863.49 Q246.89 854.45 257.79 836.29 Q270.63 820.74 255.00 808.00 Q240.77 792.32 257.79 779.71 Q275.60 770.26 266.04 752.51 Q258.89 732.58 279.44 727.44 Q299.51 725.53 297.47 705.47 Q298.50 684.32 319.44 687.44 Q338.72 693.35 344.51 674.04 Q353.55 654.89 371.71 665.79 Q387.26 678.63 400.00 663.00 Z" fill="none" stroke="{BONE}" stroke-width="3.2" stroke-linejoin="round"/>
    <circle cx="400" cy="808" r="96" fill="none" stroke="{BONE}" stroke-width="2.6"/>
    <g transform="translate(400,808)">
      <g transform="translate(0.0,-130.4) scale(0.8)"><use href="#dancer"/></g>
      <g transform="translate(76.6,-105.5) scale(0.8)"><use href="#dancer"/></g>
      <g transform="translate(124.0,-40.3) scale(0.8)"><use href="#dancer"/></g>
      <g transform="translate(124.0,40.3) scale(0.8)"><use href="#dancer"/></g>
      <g transform="translate(76.6,105.5) scale(0.8)"><use href="#dancer"/></g>
      <g transform="translate(0.0,130.4) scale(0.8)"><use href="#dancer"/></g>
      <g transform="translate(-76.6,105.5) scale(0.8)"><use href="#dancer"/></g>
      <g transform="translate(-124.0,40.3) scale(0.8)"><use href="#dancer"/></g>
      <g transform="translate(-124.0,-40.3) scale(0.8)"><use href="#dancer"/></g>
      <g transform="translate(-76.6,-105.5) scale(0.8)"><use href="#dancer"/></g>
    </g>
    <circle cx="400" cy="808" r="54" fill="none" stroke="{BONE}" stroke-width="2.6"/>
    <g transform="translate(400,808)">
      <g transform="translate(-77.2,-41.0) scale(0.62)"><use href="#warrior"/></g>
      <g transform="translate(-31.3,-81.6) scale(0.62)"><use href="#warrior"/></g>
      <g transform="translate(31.3,-81.6) scale(0.62)"><use href="#warrior"/></g>
      <g transform="translate(77.2,-41.0) scale(0.62)"><use href="#warrior"/></g>
    </g>
    <g transform="translate(400,808)">
      <g transform="translate(74.7,39.7) scale(0.8)"><use href="#ox"/></g>
      <g transform="translate(30.3,79.0) scale(0.8)"><use href="#ox"/></g>
      <g transform="translate(-30.3,79.0) scale(0.8)"><use href="#ox"/></g>
      <g transform="translate(-74.7,39.7) scale(0.8)"><use href="#ox"/></g>
    </g>
    <circle cx="400" cy="808" r="31" fill="none" stroke="{BONE}" stroke-width="2.6"/>
    <g transform="translate(400,808)">
      <g transform="translate(0.0,-42.5) scale(0.72)"><use href="#star"/></g>
      <g transform="translate(36.8,-21.3) scale(0.72)"><use href="#star"/></g>
      <g transform="translate(36.8,21.2) scale(0.72)"><use href="#star"/></g>
      <g transform="translate(0.0,42.5) scale(0.72)"><use href="#star"/></g>
      <g transform="translate(-36.8,21.3) scale(0.72)"><use href="#star"/></g>
      <g transform="translate(-36.8,-21.3) scale(0.72)"><use href="#star"/></g>
    </g>
    <g transform="translate(400,808)">
      <g stroke="{BONE}" stroke-width="2.6" stroke-linecap="round">
        <line x1="0" y1="-22" x2="0" y2="-28"/>
        <line x1="15.6" y1="-15.6" x2="19.8" y2="-19.8"/>
        <line x1="22" y1="0" x2="28" y2="0"/>
        <line x1="15.6" y1="15.6" x2="19.8" y2="19.8"/>
        <line x1="0" y1="22" x2="0" y2="28"/>
        <line x1="-15.6" y1="15.6" x2="-19.8" y2="19.8"/>
        <line x1="-22" y1="0" x2="-28" y2="0"/>
        <line x1="-15.6" y1="-15.6" x2="-19.8" y2="-19.8"/>
      </g>
      <path d="M0 -19 A19 19 0 1 1 0 19 A13 13 0 1 0 0 -19 Z" fill="{BONE}"/>
      <circle cx="0" cy="0" r="19" fill="none" stroke="{BONE}" stroke-width="2.2"/>
    </g>
  </g>
  <line x1="90" y1="990" x2="710" y2="990" stroke="{BONE}" stroke-width="2"/>
  <rect x="100" y="996" width="600" height="12" fill="url(#dotsF)"/>
  <line x1="90" y1="1016" x2="710" y2="1016" stroke="{BONE}" stroke-width="2"/>
  <g font-family="{SERIF}" text-anchor="middle" fill="{BONE}">
    <text x="400" y="1050" font-size="15" opacity="0.7" letter-spacing="6">TRANSLATED BY</text>
    <text x="400" y="1082" font-size="36" textLength="220" lengthAdjust="spacingAndGlyphs">CLAUDE</text>
    <text x="400" y="1110" font-size="15" font-style="italic" opacity="0.6">24 books \u00b7 15,687 lines rendered from the Greek</text>
  </g>
  <rect x="80" y="1128" width="640" height="34" fill="url(#meanderF)"/>
'''


def front_defs() -> str:
    """Patterns and the shield's figures for the front panel, at its own
    800x1200 scale (from art/iliad-cover.svg)."""
    return (
        f'<pattern id="meanderF" width="40" height="40" patternUnits="userSpaceOnUse">'
        f'<g fill="none" stroke="{BONE}" stroke-width="3.6">'
        f'<path d="M0 5 H40"/><path d="M0 34 H40"/>'
        f'<path d="M28 34 V11 H11 V26 H19"/></g></pattern>'
        f'<pattern id="dotsF" width="15" height="12" patternUnits="userSpaceOnUse">'
        f'<circle cx="6" cy="6" r="2.6" fill="{BONE}"/></pattern>'
        f'<g id="warrior">'
        f'<line x1="17" y1="10" x2="17" y2="-52" stroke="{BONE}" stroke-width="2.6" stroke-linecap="round"/>'
        f'<path d="M17 -52 L13 -44 L21 -44 Z" fill="{BONE}"/>'
        f'<path d="M-10 0 L10 0 L0 -16 Z" fill="{BONE}"/>'
        f'<path d="M0 -16 L9 -32 L-9 -32 Z" fill="{BONE}"/>'
        f'<circle cx="0" cy="-38" r="5.4" fill="{BONE}"/>'
        f'<path d="M-4 0 L-9 12 M4 0 L9 12" stroke="{BONE}" stroke-width="3" stroke-linecap="round"/>'
        f'<path d="M-13 -26 a7 7 0 1 1 0 -0.1 M-13 -12 a7 7 0 1 1 0 -0.1" fill="none" stroke="{BONE}" stroke-width="2.8"/>'
        f'<line x1="-9" y1="-32" x2="-2" y2="-26" stroke="{BONE}" stroke-width="2.6" stroke-linecap="round"/>'
        f'</g>'
        f'<g id="dancer">'
        f'<path d="M-9 0 L9 0 L0 -17 Z" fill="{BONE}"/>'
        f'<path d="M0 -17 L7 -30 L-7 -30 Z" fill="{BONE}"/>'
        f'<circle cx="0" cy="-36" r="5" fill="{BONE}"/>'
        f'<path d="M-7 -28 L-19 -20 M7 -28 L19 -20" fill="none" stroke="{BONE}" stroke-width="2.8" stroke-linecap="round"/>'
        f'<path d="M-4 0 L-9 11 M4 0 L9 11" stroke="{BONE}" stroke-width="2.8" stroke-linecap="round"/>'
        f'</g>'
        f'<g id="ox">'
        f'<path d="M-17 -8 L13 -8 L13 -20 L-17 -20 Z" fill="{BONE}"/>'
        f'<path d="M-14 -8 L-14 6 M-6 -8 L-6 6 M4 -8 L4 6 M11 -8 L11 6" stroke="{BONE}" stroke-width="2.8" stroke-linecap="round"/>'
        f'<path d="M13 -20 L24 -14 L24 -6 L15 -8 Z" fill="{BONE}"/>'
        f'<path d="M17 -21 L14 -30 M22 -19 L25 -28" fill="none" stroke="{BONE}" stroke-width="2.4" stroke-linecap="round"/>'
        f'<path d="M-17 -19 L-24 -26" stroke="{BONE}" stroke-width="2.4" stroke-linecap="round"/>'
        f'</g>'
        f'<g id="star">'
        f'<line x1="-10" y1="0" x2="10" y2="0" stroke="{BONE}" stroke-width="2.4"/>'
        f'<line x1="0" y1="-10" x2="0" y2="10" stroke="{BONE}" stroke-width="2.4"/>'
        f'<line x1="-7.1" y1="-7.1" x2="7.1" y2="7.1" stroke="{BONE}" stroke-width="2.4"/>'
        f'<line x1="-7.1" y1="7.1" x2="7.1" y2="-7.1" stroke="{BONE}" stroke-width="2.4"/>'
        f'<circle cx="0" cy="0" r="2.8" fill="{BONE}"/>'
        f'</g>'
    )


_PATTERN_RE = re.compile(
    r'<pattern id="(?P<id>[^"]+)" width="(?P<w>[\d.]+)" '
    r'height="(?P<h>[\d.]+)" patternUnits="userSpaceOnUse">'
    r'(?P<body>.*?)</pattern>', re.S)
_PATTERN_RECT_RE = re.compile(r'<rect\s+(?P<attrs>[^>]*?)/>')
_ATTR_RE = re.compile(r'([\w-]+)="([^"]*)"')


def expand_patterns(svg: str) -> str:
    """Replace every <pattern> fill with explicit, clipped <use> tiles, so
    the bands stay vector in the PDF (see the Odyssey builder)."""
    tiles: dict[str, tuple[float, float]] = {}

    def _def(m: re.Match) -> str:
        tiles[m.group("id")] = (float(m.group("w")), float(m.group("h")))
        return f'<g id="{m.group("id")}">{m.group("body")}</g>'

    svg = _PATTERN_RE.sub(_def, svg)
    n = 0

    def _rect(m: re.Match) -> str:
        nonlocal n
        attrs = dict(_ATTR_RE.findall(m.group("attrs")))
        fill = attrs.get("fill", "")
        if not (fill.startswith("url(#") and fill[5:-1] in tiles):
            return m.group(0)
        tile = fill[5:-1]
        tw, th = tiles[tile]
        x, y = float(attrs["x"]), float(attrs["y"])
        w, h = float(attrs["width"]), float(attrs["height"])
        n += 1
        clip = f"tile-clip-{n}"
        extra = "".join(f' {k}="{v}"' for k, v in attrs.items()
                        if k not in ("x", "y", "width", "height", "fill"))
        out = [f'<clipPath id="{clip}"><rect x="{x:g}" y="{y:g}" '
               f'width="{w:g}" height="{h:g}"/></clipPath>',
               f'<g clip-path="url(#{clip})"{extra}>']
        for j in range(math.floor(y / th), math.ceil((y + h) / th)):
            for k in range(math.floor(x / tw), math.ceil((x + w) / tw)):
                out.append(f'<use href="#{tile}" x="{k * tw:g}" y="{j * th:g}"/>')
        out.append("</g>")
        return "".join(out)

    svg = _PATTERN_RECT_RE.sub(_rect, svg)
    if 'fill="url(#' in svg:
        left = [t for t in tiles if f'url(#{t})' in svg]
        if left:
            raise RuntimeError(f"pattern fill(s) not expanded: {left}")
    return svg


def build(spine_in: float, with_url: bool, out: Path) -> Path:
    svg = build_svg(spine_in, with_url)
    svg = svg.replace('</defs>', front_defs() + '</defs>', 1)
    svg = expand_patterns(svg)

    svg_path = ART / "iliad-wrap.svg"
    svg_path.write_text(svg, encoding="utf-8")
    print(f"wrote {svg_path}  ({len(svg):,} bytes)")

    if WORK.exists():
        shutil.rmtree(WORK)
    WORK.mkdir(parents=True)
    shutil.copy(svg_path, WORK / svg_path.name)

    w, h = wrap_width(spine_in), WRAP_H_IN
    # calibre quantizes the page size to a 1.2pt grid; request it oversize
    # and cut the boxes to the exact figure afterwards (see the Odyssey
    # builder for the full reasoning).
    OVERSCAN_IN = 0.125
    ow, oh = w + OVERSCAN_IN, h + OVERSCAN_IN
    (WORK / "wrap.html").write_text(
        "<!DOCTYPE html>\n"
        '<html><head><meta charset="utf-8"/><title>Wrap</title>\n'
        "<style>\n"
        f"  @page {{ size: {ow:.4f}in {oh:.4f}in; margin: 0; }}\n"
        "  html, body { margin:0; padding:0; border:0; }\n"
        "  img { display:block; margin:0; padding:0; border:0;"
        f" width:{w:.4f}in; height:{h:.4f}in; }}\n"
        "</style></head><body>\n"
        f'<img src="{svg_path.name}" alt=""/>\n'
        "</body></html>\n",
        encoding="utf-8")

    cmd = [
        EBOOK_CONVERT, str(WORK / "wrap.html"), str(out),
        "--custom-size", f"{ow:.4f}x{oh:.4f}",
        "--unit", "inch",
        "--margin-left", "0", "--margin-right", "0",
        "--margin-top", "0", "--margin-bottom", "0",
        "--pdf-page-margin-left", "0", "--pdf-page-margin-right", "0",
        "--pdf-page-margin-top", "0", "--pdf-page-margin-bottom", "0",
        "--pdf-no-cover",
        "--disable-font-rescaling",
        "--embed-all-fonts",
        "--subset-embedded-fonts",
    ]
    print(f"rendering wrap -> {w:.3f}x{h:.3f}in (spine {spine_in:.3f}in, "
          f"panels {(w - spine_in) / 2:.3f}in)")
    subprocess.run(cmd, check=True, cwd=WORK, stdout=subprocess.DEVNULL)
    shutil.rmtree(WORK, ignore_errors=True)
    _set_exact_page_size(out, w, h)
    print(f"wrote {out}  ({out.stat().st_size:,} bytes)")
    return out


def _set_exact_page_size(pdf: Path, w_in: float, h_in: float) -> None:
    """Cut the page boxes to the exact required size from the top-left
    (calibre's 1.2pt grid cannot express most widths)."""
    from pypdf import PdfReader, PdfWriter
    from pypdf.generic import ArrayObject, FloatObject, NameObject

    want_w, want_h = w_in * 72.0, h_in * 72.0
    reader = PdfReader(str(pdf))
    writer = PdfWriter()
    page = reader.pages[0]
    got_h = float(page.mediabox.height)
    x0, y0 = 0.0, got_h - want_h
    for name in ("/MediaBox", "/CropBox", "/TrimBox", "/BleedBox", "/ArtBox"):
        if name == "/MediaBox" or name in page:
            page[NameObject(name)] = ArrayObject([
                FloatObject(round(x0, 4)), FloatObject(round(y0, 4)),
                FloatObject(round(x0 + want_w, 4)), FloatObject(round(y0 + want_h, 4)),
            ])
    writer.add_page(page)
    with open(pdf, "wb") as fh:
        writer.write(fh)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--pages", type=int, default=None,
                    help="interior page count; the spine follows by Lulu's "
                         "formula (default: the built interior's count)")
    ap.add_argument("--spine", type=float, default=None,
                    help="spine width in inches, overriding --pages")
    ap.add_argument("--no-url", action="store_true",
                    help="omit the site URL from the back cover")
    ap.add_argument("-o", "--out", type=Path, default=ART / "iliad-wrap.pdf")
    args = ap.parse_args()
    if args.spine is not None and args.pages is not None:
        sys.exit("give --pages or --spine, not both")
    if args.spine is not None:
        spine = args.spine
    else:
        pages = args.pages if args.pages is not None else interior_pages()
        if pages is None:
            sys.exit(f"no built interior at {INTERIOR}; give --pages or --spine")
        spine = spine_for(pages)
        print(f"{pages} pages -> spine {spine:.3f} in")
    build(spine, not args.no_url, args.out)
