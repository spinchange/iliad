#!/usr/bin/env python3
"""Generate the 24 per-book plates for the Iliad.

Each plate is a 600x800 SVG in the same Geometric vocabulary as the cover:
wine-dark ground, pale-bone (#ead9b4) line work, meander bands, and a single
emblem drawn from that book's own action. Run from the art/ directory:

    python make_plates.py

Writes book_01.svg .. book_24.svg alongside this script.
"""

import os
import re

BONE = "#ead9b4"
GOLD = "#c99b3f"

W, H = 600, 800
CX, CY = 300, 430          # emblem center
R = 150                    # emblem tondo radius

ROMAN = {
    1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI", 7: "VII", 8: "VIII",
    9: "IX", 10: "X", 11: "XI", 12: "XII", 13: "XIII", 14: "XIV", 15: "XV",
    16: "XVI", 17: "XVII", 18: "XVIII", 19: "XIX", 20: "XX", 21: "XXI",
    22: "XXII", 23: "XXIII", 24: "XXIV",
}

# Short title + the emblem each book carries.
BOOKS = {
    1:  ("THE WRATH",            "plague-arrows"),
    2:  ("THE CATALOGUE",        "ships-row"),
    3:  ("THE DUEL FOR HELEN",   "duel-pair"),
    4:  ("THE TRUCE BROKEN",     "bow-arrow"),
    5:  ("THE ARISTEIA",         "wounded-god"),
    6:  ("HECTOR IN TROY",       "helmet-child"),
    7:  ("THE WALL",             "wall-course"),
    8:  ("THE GOLDEN SCALES",    "scales"),
    9:  ("THE EMBASSY",          "three-tripods"),
    10: ("THE DOLONEIA",         "night-wolf"),
    11: ("THE LONG DAY",         "sun-spears"),
    12: ("THE GATE GOES DOWN",   "gate-stone"),
    13: ("THE SEA-GOD",          "trident-wave"),
    14: ("THE DECEPTION",        "girdle"),
    15: ("ZEUS WAKES",           "ship-stern"),
    16: ("THE PATROCLEIA",       "borrowed-armor"),
    17: ("THE BODY",             "weeping-horses"),
    18: ("THE SHIELD",           "shield-rings"),
    19: ("THE ARMING",           "spear-horse"),
    20: ("THE GODS GO DOWN",     "gods-descend"),
    21: ("THE RIVER FIGHTS",     "river-flood"),
    22: ("HECTOR ALONE",         "walls-chase"),
    23: ("THE GAMES",            "chariot-turn"),
    24: ("THE RANSOM",           "kneeling-king"),
}


def head(n):
    """Shared defs, ground, frame and meander band."""
    return f'''<svg viewBox="0 0 {W} {H}" width="{W}" height="{H}" xmlns="http://www.w3.org/2000/svg" role="img"
     aria-label="Plate for Iliad Book {n}: {BOOKS[n][0].title()} — a Geometric emblem in pale bone on a wine-dark ground.">
  <defs>
    <linearGradient id="wine" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#46192b"/>
      <stop offset="0.55" stop-color="#331323"/>
      <stop offset="1" stop-color="#1e0b15"/>
    </linearGradient>
    <radialGradient id="vig" cx="0.5" cy="0.44" r="0.85">
      <stop offset="0.6" stop-color="#000000" stop-opacity="0"/>
      <stop offset="1" stop-color="#0c0408" stop-opacity="0.5"/>
    </radialGradient>
    <pattern id="meander" width="40" height="40" patternUnits="userSpaceOnUse">
      <g fill="none" stroke="{BONE}" stroke-width="3.6">
        <path d="M0 5 H40"/><path d="M0 34 H40"/><path d="M28 34 V11 H11 V26 H19"/>
      </g>
    </pattern>
    <filter id="grain">
      <feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves="2" stitchTiles="stitch"/>
      <feColorMatrix type="saturate" values="0"/>
      <feComponentTransfer><feFuncA type="linear" slope="0.06"/></feComponentTransfer>
      <feComposite operator="in" in2="SourceGraphic"/>
    </filter>
  </defs>

  <rect width="{W}" height="{H}" fill="url(#wine)"/>
  <rect width="{W}" height="{H}" fill="{BONE}" filter="url(#grain)"/>
  <rect width="{W}" height="{H}" fill="url(#vig)"/>

  <rect x="28" y="28" width="{W-56}" height="{H-56}" fill="none" stroke="{BONE}" stroke-width="2.2" opacity="0.9"/>
  <rect x="38" y="38" width="{W-76}" height="{H-76}" fill="none" stroke="{BONE}" stroke-width="1" opacity="0.38"/>
  <rect x="70" y="58" width="{W-140}" height="34" fill="url(#meander)"/>
'''


def foot(n):
    title, _ = BOOKS[n]
    return f'''
  <!-- the tondo that holds the emblem -->
  <circle cx="{CX}" cy="{CY}" r="{R}" fill="none" stroke="{BONE}" stroke-width="2.4" opacity="0.85"/>
  <circle cx="{CX}" cy="{CY}" r="{R-8}" fill="none" stroke="{BONE}" stroke-width="1" opacity="0.35"/>

  <g font-family="'Palatino Linotype','Book Antiqua',Palatino,Georgia,serif" text-anchor="middle" fill="{BONE}">
    <text x="{CX}" y="176" font-size="17" letter-spacing="7" opacity="0.62">BOOK</text>
    <text x="{CX}" y="238" font-size="62" fill="{GOLD}">{ROMAN[n]}</text>
    <line x1="{CX-70}" y1="640" x2="{CX+70}" y2="640" stroke="{GOLD}" stroke-width="1.2" opacity="0.85"/>
    <text x="{CX}" y="686" font-size="25" letter-spacing="2">{title}</text>
    <text x="{CX}" y="726" font-size="13" font-style="italic" opacity="0.5">HOMER&#8217;S ILIAD</text>
  </g>

  <rect x="70" y="{H-92}" width="{W-140}" height="34" fill="url(#meander)"/>
</svg>
'''


# ---------------------------------------------------------------- emblems --
# Each returns SVG drawn around (CX, CY), fitting inside radius R-20.

def plague_arrows():
    """Book 1: Apollo's arrows fall for nine days; the god's silver bow, drawn."""
    out = [f'<g stroke="{BONE}" fill="none" stroke-linecap="round">']
    # the great bow across the top of the tondo, bent and strung
    out.append(f'  <path d="M{CX-94} {CY-96} Q{CX} {CY-22} {CX+94} {CY-96}" stroke-width="5"/>')
    out.append(f'  <line x1="{CX-94}" y1="{CY-96}" x2="{CX+94}" y2="{CY-96}" '
               f'stroke-width="2.2" opacity="0.8"/>')
    out.append(f'  <path d="M{CX-94} {CY-96} l9 -11 M{CX+94} {CY-96} l-9 -11" stroke-width="3"/>')
    # arrows raining down, at slight angles, with barbed heads
    for dx, lean, ln in ((-76, -7, 96), (-26, 3, 116), (26, -4, 104), (76, 8, 90)):
        top = CY - 22
        bot = top + ln
        out.append(f'  <line x1="{CX+dx}" y1="{top}" x2="{CX+dx+lean}" y2="{bot}" stroke-width="3.4"/>')
        # the barbed head, at the falling end (bottom), pointing down
        out.append(f'  <path d="M{CX+dx+lean-10} {bot-22} L{CX+dx+lean} {bot} '
                   f'L{CX+dx+lean+10} {bot-22} Z" fill="{BONE}" stroke="none"/>')
        # the fletching, at the trailing end (top), opening upward
        out.append(f'  <path d="M{CX+dx-10} {top-2} L{CX+dx} {top+18} L{CX+dx+10} {top-2}" '
                   f'stroke-width="2.6"/>')
    out.append('</g>')
    return "\n".join(out)


def ships_row():
    """Book 2: the Catalogue — beached ships, prow after prow."""
    out = [f'<g stroke="{BONE}" fill="none" stroke-linecap="round">']
    for row, (n, y, sc) in enumerate(((3, CY - 52, 1.0), (4, CY + 6, 0.86), (5, CY + 62, 0.72))):
        span = 108 * sc
        for i in range(n):
            x = CX + (i - (n - 1) / 2) * (span * 0.78)
            w, h = 40 * sc, 15 * sc
            out.append(
                f'  <path d="M{x-w} {y} q{w} {h*1.5} {2*w} 0" stroke-width="{2.8*sc:.1f}" fill="{BONE}"/>')
            out.append(f'  <line x1="{x}" y1="{y}" x2="{x}" y2="{y-34*sc:.0f}" stroke-width="{2.6*sc:.1f}"/>')
            out.append(f'  <line x1="{x-13*sc:.0f}" y1="{y-26*sc:.0f}" x2="{x+13*sc:.0f}" '
                       f'y2="{y-26*sc:.0f}" stroke-width="{2.2*sc:.1f}"/>')
    out.append('</g>')
    return "\n".join(out)


def _fighter(x, y, face=1, sc=1.0, spear=True, shield=True):
    """A Geometric warrior; face=1 looks right, -1 looks left."""
    g = [f'<g transform="translate({x},{y}) scale({face*sc},{sc})">']
    g.append(f'  <path d="M-11 0 L11 0 L0 -18 Z" fill="{BONE}"/>')
    g.append(f'  <path d="M0 -18 L10 -36 L-10 -36 Z" fill="{BONE}"/>')
    g.append(f'  <circle cx="0" cy="-43" r="6" fill="{BONE}"/>')
    g.append(f'  <path d="M-5 0 L-11 15 M5 0 L11 15" stroke="{BONE}" stroke-width="3.4" '
             f'stroke-linecap="round" fill="none"/>')
    if spear:
        g.append(f'  <line x1="14" y1="-30" x2="52" y2="-52" stroke="{BONE}" stroke-width="3" '
                 f'stroke-linecap="round"/>')
        g.append(f'  <path d="M52 -52 L42 -50 L46 -43 Z" fill="{BONE}"/>')
    if shield:
        g.append(f'  <path d="M-16 -30 a8 8 0 1 1 0 -0.1 M-16 -14 a8 8 0 1 1 0 -0.1" '
                 f'fill="none" stroke="{BONE}" stroke-width="3"/>')
    g.append('</g>')
    return "\n".join(g)


def duel_pair():
    """Book 3: Paris and Menelaus, spear to spear."""
    return (_fighter(CX - 74, CY + 46, face=1) + "\n" +
            _fighter(CX + 74, CY + 46, face=-1))


def bow_arrow():
    """Book 4: Pandarus's arrow — the truce broken."""
    return f'''<g stroke="{BONE}" fill="none" stroke-linecap="round">
  <path d="M{CX-30} {CY-96} Q{CX-92} {CY} {CX-30} {CY+96}" stroke-width="4.5"/>
  <line x1="{CX-30}" y1="{CY-96}" x2="{CX-30}" y2="{CY+96}" stroke-width="1.8" opacity="0.8"/>
  <line x1="{CX-58}" y1="{CY}" x2="{CX+96}" y2="{CY}" stroke-width="3.2"/>
  <path d="M{CX+96} {CY} L{CX+74} {CY-9} L{CX+80} {CY} L{CX+74} {CY+9} Z" fill="{BONE}" stroke="none"/>
  <path d="M{CX-58} {CY} L{CX-44} {CY-9} M{CX-58} {CY} L{CX-44} {CY+9}" stroke-width="2.4"/>
</g>'''


def wounded_god():
    """Book 5: a mortal's spear reaches a god — the ichor falls."""
    out = [_fighter(CX - 74, CY + 74, face=1, sc=1.45)]
    out.append(f'''<g stroke="{BONE}" fill="none">
  <g transform="translate({CX+62},{CY+26}) scale(1.45)">
    <path d="M-13 0 L13 0 L0 -22 Z" fill="{BONE}"/>
    <path d="M0 -22 L11 -42 L-11 -42 Z" fill="{BONE}"/>
    <circle cx="0" cy="-50" r="7" fill="{BONE}"/>
    <g stroke="{BONE}" stroke-width="2.2" opacity="0.9">
      <line x1="0" y1="-64" x2="0" y2="-72"/>
      <line x1="-10" y1="-61" x2="-15" y2="-68"/>
      <line x1="10" y1="-61" x2="15" y2="-68"/>
    </g>
    <path d="M-6 0 L-12 20 M6 0 L12 20" stroke-width="3.4" stroke-linecap="round"/>
  </g>
  <g stroke="{BONE}" stroke-width="2.6" stroke-linecap="round" opacity="0.8">
    <path d="M{CX+30} {CY+44} q-6 18 3 32"/>
    <path d="M{CX+46} {CY+52} q-5 16 2 28"/>
  </g>
</g>''')
    return "\n".join(out)


def helmet_child():
    """Book 6: Hector lifts off the terrifying helmet for Astyanax."""
    return f'''<g stroke="{BONE}" fill="none">
  <!-- the helmet, held aside -->
  <g transform="translate({CX-58},{CY-26})">
    <path d="M-30 20 a30 34 0 0 1 60 0 Z" fill="{BONE}" stroke="{BONE}" stroke-width="2"/>
    <path d="M-30 20 L-30 34 M30 20 L30 34" stroke="{BONE}" stroke-width="3.4" stroke-linecap="round"/>
    <path d="M-26 -12 q26 -30 52 -2 q-8 -22 -26 -22 q-18 0 -26 24 Z" fill="{BONE}" stroke="none"/>
  </g>
  <!-- father and child -->
  <g transform="translate({CX+56},{CY+34})">
    <path d="M-13 0 L13 0 L0 -22 Z" fill="{BONE}"/>
    <path d="M0 -22 L11 -42 L-11 -42 Z" fill="{BONE}"/>
    <circle cx="0" cy="-50" r="7" fill="{BONE}"/>
    <path d="M-6 0 L-12 22 M6 0 L12 22" stroke="{BONE}" stroke-width="3.4" stroke-linecap="round"/>
    <path d="M-9 -38 L-34 -46" stroke="{BONE}" stroke-width="3" stroke-linecap="round"/>
    <g transform="translate(-48,-56) scale(0.5)">
      <path d="M-11 0 L11 0 L0 -18 Z" fill="{BONE}"/>
      <circle cx="0" cy="-26" r="8" fill="{BONE}"/>
      <path d="M8 -14 L26 -6" stroke="{BONE}" stroke-width="4" stroke-linecap="round"/>
    </g>
  </g>
</g>'''


def wall_course():
    """Book 7: the Achaean wall goes up, course on course, with its ditch."""
    out = [f'<g stroke="{BONE}" fill="none">']
    y0 = CY - 62
    for row in range(4):
        y = y0 + row * 30
        half = 108 - row * 6
        out.append(f'  <line x1="{CX-half}" y1="{y}" x2="{CX+half}" y2="{y}" stroke-width="2.6"/>')
        n = 6 - (row % 2)
        for i in range(n + 1):
            x = CX - half + i * (2 * half / n)
            out.append(f'  <line x1="{x:.0f}" y1="{y}" x2="{x:.0f}" y2="{y+30}" stroke-width="2.2"/>')
    y = y0 + 4 * 30
    out.append(f'  <line x1="{CX-84}" y1="{y}" x2="{CX+84}" y2="{y}" stroke-width="2.6"/>')
    # the ditch below, with its stakes
    out.append(f'  <path d="M{CX-104} {y+22} L{CX-58} {y+50} L{CX+58} {y+50} L{CX+104} {y+22}" '
               f'stroke-width="2.6"/>')
    for dx in (-40, -14, 14, 40):
        out.append(f'  <line x1="{CX+dx}" y1="{y+50}" x2="{CX+dx-6}" y2="{y+30}" stroke-width="2.2"/>')
    out.append('</g>')
    return "\n".join(out)


def scales():
    """Book 8: Zeus lifts the golden scales and the Achaean day sinks."""
    return f'''<g stroke="{BONE}" fill="none" stroke-linecap="round">
  <line x1="{CX}" y1="{CY-104}" x2="{CX}" y2="{CY-62}" stroke-width="3"/>
  <circle cx="{CX}" cy="{CY-110}" r="7" stroke-width="3"/>
  <!-- the beam, tipped -->
  <line x1="{CX-96}" y1="{CY-40}" x2="{CX+96}" y2="{CY-76}" stroke-width="4"/>
  <line x1="{CX}" y1="{CY-62}" x2="{CX}" y2="{CY-58}" stroke-width="3"/>
  <!-- the sinking pan -->
  <line x1="{CX-96}" y1="{CY-40}" x2="{CX-96}" y2="{CY+26}" stroke-width="2.2"/>
  <path d="M{CX-134} {CY+26} q38 40 76 0 Z" fill="{BONE}" stroke="{BONE}" stroke-width="2.4"/>
  <!-- the rising pan -->
  <line x1="{CX+96}" y1="{CY-76}" x2="{CX+96}" y2="{CY-22}" stroke-width="2.2"/>
  <path d="M{CX+62} {CY-22} q34 34 68 0 Z" fill="none" stroke="{BONE}" stroke-width="2.4"/>
</g>'''


def three_tripods():
    """Book 9: Agamemnon's gifts — and three refusals, each smaller."""
    out = [f'<g stroke="{BONE}" fill="none" stroke-linecap="round">']
    for i, (dx, sc) in enumerate(((-92, 1.0), (0, 0.82), (92, 0.64))):
        x, y = CX + dx, CY + 46
        b, h = 30 * sc, 40 * sc
        out.append(f'  <g transform="translate({x},{y})">')
        out.append(f'    <path d="M{-b} {-h} q{b} {-22*sc:.0f} {2*b} 0 Z" fill="{BONE}" '
                   f'stroke="{BONE}" stroke-width="{2.4*sc:.1f}"/>')
        out.append(f'    <path d="M{-b} {-h} L{-b*1.28:.0f} {18*sc:.0f} M0 {-h} L0 {18*sc:.0f} '
                   f'M{b} {-h} L{b*1.28:.0f} {18*sc:.0f}" stroke-width="{3*sc:.1f}"/>')
        out.append(f'    <path d="M{-b*0.7:.0f} {-h-12*sc:.0f} a{7*sc:.0f} {7*sc:.0f} 0 0 1 0 {-2*sc:.0f} '
                   f'M{b*0.7:.0f} {-h-12*sc:.0f} a{7*sc:.0f} {7*sc:.0f} 0 0 0 0 {-2*sc:.0f}" '
                   f'stroke-width="{2.2*sc:.1f}"/>')
        out.append('  </g>')
    out.append('</g>')
    return "\n".join(out)


def night_wolf():
    """Book 10: the night raid — a wolf in profile under the stars."""
    return f'''<g stroke="{BONE}" fill="none" stroke-linecap="round">
  <g transform="translate({CX-6},{CY+26})">
    <!-- wolf, walking, in profile: body -->
    <path d="M-62 -14 L34 -14 L34 -46 L-62 -46 Z" fill="{BONE}" stroke="{BONE}" stroke-width="2"/>
    <!-- legs -->
    <path d="M-54 -14 L-58 34 M-28 -14 L-30 34 M8 -14 L6 34 M28 -14 L32 34"
          stroke="{BONE}" stroke-width="4.2"/>
    <!-- neck, head and muzzle, carried low -->
    <path d="M34 -46 L64 -40 L92 -18 L92 -6 L62 -8 L38 -16 Z"
          fill="{BONE}" stroke="{BONE}" stroke-width="2"/>
    <!-- pricked ears -->
    <path d="M56 -40 L52 -66 L70 -48 Z" fill="{BONE}" stroke="none"/>
    <path d="M72 -36 L76 -60 L86 -38 Z" fill="{BONE}" stroke="none"/>
    <circle cx="72" cy="-22" r="3.6" fill="#331323" stroke="none"/>
    <!-- the low brush of the tail -->
    <path d="M-62 -40 q-34 4 -40 38" stroke="{BONE}" stroke-width="5"/>
  </g>
  <!-- night stars over the raid -->
  <g stroke="{BONE}" stroke-width="2.6" opacity="0.9">
    <g transform="translate({CX-88},{CY-94})">
      <line x1="-12" y1="0" x2="12" y2="0"/><line x1="0" y1="-12" x2="0" y2="12"/>
      <line x1="-8.5" y1="-8.5" x2="8.5" y2="8.5"/><line x1="-8.5" y1="8.5" x2="8.5" y2="-8.5"/>
    </g>
    <g transform="translate({CX+14},{CY-116})">
      <line x1="-9" y1="0" x2="9" y2="0"/><line x1="0" y1="-9" x2="0" y2="9"/>
      <line x1="-6.4" y1="-6.4" x2="6.4" y2="6.4"/><line x1="-6.4" y1="6.4" x2="6.4" y2="-6.4"/>
    </g>
    <g transform="translate({CX+96},{CY-86})">
      <line x1="-12" y1="0" x2="12" y2="0"/><line x1="0" y1="-12" x2="0" y2="12"/>
      <line x1="-8.5" y1="-8.5" x2="8.5" y2="8.5"/><line x1="-8.5" y1="8.5" x2="8.5" y2="-8.5"/>
    </g>
  </g>
</g>'''


def sun_spears():
    """Book 11: the long day — the sun above a hedge of spears."""
    out = [f'<g stroke="{BONE}" fill="none" stroke-linecap="round">']
    out.append(f'  <circle cx="{CX}" cy="{CY-72}" r="30" fill="{BONE}" stroke="{BONE}" stroke-width="2"/>')
    for k in range(12):
        import math
        a = math.radians(k * 30)
        x1, y1 = CX + 38 * math.sin(a), CY - 72 - 38 * math.cos(a)
        x2, y2 = CX + 50 * math.sin(a), CY - 72 - 50 * math.cos(a)
        out.append(f'  <line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke-width="2.6"/>')
    for i, dx in enumerate((-90, -60, -30, 0, 30, 60, 90)):
        top = CY + 6 + (i % 2) * 10
        out.append(f'  <line x1="{CX+dx}" y1="{top}" x2="{CX+dx}" y2="{CY+104}" stroke-width="3"/>')
        out.append(f'  <path d="M{CX+dx-6} {top+13} L{CX+dx} {top} L{CX+dx+6} {top+13} Z" '
                   f'fill="{BONE}" stroke="none"/>')
    out.append('</g>')
    return "\n".join(out)


def gate_stone():
    """Book 12: Hector's stone bursts the gate — the doors fly inward."""
    return f'''<g stroke="{BONE}" fill="none" stroke-linecap="round">
  <!-- the two towers flanking the gateway -->
  <path d="M{CX-116} {CY+96} L{CX-116} {CY-58} L{CX-62} {CY-58} L{CX-62} {CY+96}" stroke-width="3.4"/>
  <path d="M{CX+62} {CY+96} L{CX+62} {CY-58} L{CX+116} {CY-58} L{CX+116} {CY+96}" stroke-width="3.4"/>
  <g stroke-width="2.6">
    <path d="M{CX-116} {CY-58} L{CX-116} {CY-78} L{CX-94} {CY-78} L{CX-94} {CY-58}"/>
    <path d="M{CX-84} {CY-58} L{CX-84} {CY-78} L{CX-62} {CY-78} L{CX-62} {CY-58}"/>
    <path d="M{CX+62} {CY-58} L{CX+62} {CY-78} L{CX+84} {CY-78} L{CX+84} {CY-58}"/>
    <path d="M{CX+94} {CY-58} L{CX+94} {CY-78} L{CX+116} {CY-78} L{CX+116} {CY-58}"/>
  </g>
  <g stroke-width="1.8" opacity="0.7">
    <line x1="{CX-116}" y1="{CY-16}" x2="{CX-62}" y2="{CY-16}"/>
    <line x1="{CX-116}" y1="{CY+28}" x2="{CX-62}" y2="{CY+28}"/>
    <line x1="{CX+62}" y1="{CY-16}" x2="{CX+116}" y2="{CY-16}"/>
    <line x1="{CX+62}" y1="{CY+28}" x2="{CX+116}" y2="{CY+28}"/>
  </g>
  <!-- the doors, burst off their hinges and swinging in -->
  <g stroke-width="3.2">
    <path d="M{CX-62} {CY-34} L{CX-26} {CY-16} L{CX-26} {CY+96} L{CX-62} {CY+96} Z"/>
    <path d="M{CX+62} {CY-34} L{CX+26} {CY-16} L{CX+26} {CY+96} L{CX+62} {CY+96} Z"/>
    <line x1="{CX-54}" y1="{CY+4}" x2="{CX-34}" y2="{CY+14}"/>
    <line x1="{CX+54}" y1="{CY+4}" x2="{CX+34}" y2="{CY+14}"/>
  </g>
  <!-- the stone in the air, and the shock of it -->
  <path d="M{CX-30} {CY-104} L{CX+8} {CY-124} L{CX+38} {CY-100} L{CX+26} {CY-68} L{CX-16} {CY-70} Z"
        fill="{BONE}" stroke="{BONE}" stroke-width="2.4" stroke-linejoin="round"/>
  <g stroke-width="2.4" opacity="0.75">
    <path d="M{CX-44} {CY-52} l-14 -10 M{CX+50} {CY-50} l14 -10 M{CX+2} {CY-46} l0 -14"/>
  </g>
</g>'''


def trident_wave():
    """Book 13: Poseidon's trident over the running sea."""
    out = [f'<g stroke="{BONE}" fill="none" stroke-linecap="round">']
    # the haft, running down into the water
    out.append(f'  <line x1="{CX}" y1="{CY-116}" x2="{CX}" y2="{CY+44}" stroke-width="5"/>')
    # the crossbar the outer prongs spring from
    out.append(f'  <line x1="{CX-46}" y1="{CY-72}" x2="{CX+46}" y2="{CY-72}" stroke-width="4.5"/>')
    # the three prongs, rising from the bar
    for dx in (-46, 0, 46):
        out.append(f'  <line x1="{CX+dx}" y1="{CY-72}" x2="{CX+dx}" y2="{CY-112}" stroke-width="4.5"/>')
        out.append(f'  <path d="M{CX+dx-9} {CY-112} L{CX+dx} {CY-136} L{CX+dx+9} {CY-112} Z" '
                   f'fill="{BONE}" stroke="none"/>')
    # a collar where haft meets bar
    out.append(f'  <line x1="{CX-12}" y1="{CY-56}" x2="{CX+12}" y2="{CY-56}" stroke-width="3.4"/>')
    for i, y in enumerate((CY + 60, CY + 92)):
        d = [f'M{CX-116} {y}']
        for k in range(4):
            x = CX - 116 + k * 58
            d.append(f'q14 -18 29 0 q15 18 29 0')
        out.append(f'  <path d="{" ".join(d)}" stroke-width="3.2" opacity="{0.95 - i*0.25}"/>')
    out.append('</g>')
    return "\n".join(out)


def girdle():
    """Book 14: Hera adorned, and winged Sleep waiting in the branch above."""
    return f'''<g stroke="{BONE}" fill="none" stroke-linecap="round">
  <!-- Hera, in the long belted robe, the borrowed girdle at her waist -->
  <g transform="translate({CX-22},{CY+70})">
    <path d="M-44 0 L44 0 L20 -74 L-20 -74 Z" fill="{BONE}" stroke="{BONE}" stroke-width="2"/>
    <path d="M-20 -74 L-14 -104 L14 -104 L20 -74 Z" fill="{BONE}" stroke="{BONE}" stroke-width="2"/>
    <circle cx="0" cy="-116" r="11" fill="{BONE}"/>
    <!-- the veil -->
    <path d="M-11 -120 q11 -16 22 0 q4 20 -4 30" stroke="{BONE}" stroke-width="2.4" opacity="0.85"/>
    <!-- the girdle of Aphrodite, worn at the breast -->
    <path d="M-21 -78 q21 16 42 0" stroke="{BONE}" stroke-width="3.4"/>
    <g stroke-width="2" opacity="0.85">
      <path d="M-12 -70 l0 8 M0 -66 l0 8 M12 -70 l0 8"/>
    </g>
    <!-- the arms -->
    <path d="M-19 -92 L-42 -74 M19 -92 L42 -74" stroke="{BONE}" stroke-width="3.2"/>
    <!-- hem pattern -->
    <g stroke-width="1.8" opacity="0.7">
      <line x1="-38" y1="-16" x2="38" y2="-16"/>
      <line x1="-33" y1="-32" x2="33" y2="-32"/>
    </g>
  </g>
  <!-- Sleep, winged, perched in the fir above -->
  <g transform="translate({CX+80},{CY-64})">
    <path d="M-8 20 L8 20 L0 2 Z" fill="{BONE}"/>
    <circle cx="0" cy="-8" r="7" fill="{BONE}"/>
    <path d="M-6 6 q-34 -14 -44 -34 q30 6 44 20 Z" fill="{BONE}" stroke="{BONE}" stroke-width="1.6"/>
    <path d="M6 6 q34 -14 44 -34 q-30 6 -44 20 Z" fill="{BONE}" stroke="{BONE}" stroke-width="1.6"/>
  </g>
  <!-- the branch he sits in -->
  <path d="M{CX+16} {CY-30} q54 -22 104 -12" stroke-width="3" opacity="0.8"/>
</g>'''


def ship_stern():
    """Book 15: a man's hand closes on the stern-post of the beached ship."""
    return f'''<g stroke="{BONE}" fill="none" stroke-linecap="round">
  <!-- the hull, drawn up on the beach -->
  <path d="M{CX-118} {CY+6} C{CX-104} {CY+70} {CX-30} {CY+92} {CX+40} {CY+86}"
        stroke-width="4"/>
  <path d="M{CX-118} {CY+6} C{CX-96} {CY+52} {CX-24} {CY+70} {CX+44} {CY+64}"
        stroke-width="3" opacity="0.75"/>
  <!-- the high stern-post, curling over -->
  <path d="M{CX+40} {CY+86} C{CX+96} {CY+80} {CX+112} {CY+30} {CX+96} {CY-30}
           C{CX+88} {CY-66} {CX+60} {CY-84} {CX+34} {CY-74}"
        stroke-width="5"/>
  <circle cx="{CX+30}" cy="{CY-70}" r="9" stroke-width="3.4"/>
  <!-- the mast and yard -->
  <line x1="{CX-46}" y1="{CY+46}" x2="{CX-46}" y2="{CY-96}" stroke-width="4.5"/>
  <line x1="{CX-88}" y1="{CY-74}" x2="{CX-4}" y2="{CY-74}" stroke-width="3.4"/>
  <!-- the hand that has taken hold of the stern -->
  <g transform="translate({CX+62},{CY-16})">
    <path d="M0 34 L0 -2 q0 -13 9 -13 q9 0 9 13 L18 6" fill="{BONE}" stroke="{BONE}" stroke-width="2.4"/>
    <path d="M18 -2 q0 -15 9 -15 q9 0 9 15 L36 10" fill="{BONE}" stroke="{BONE}" stroke-width="2.4"/>
    <path d="M0 12 q-18 -8 -21 6 q-3 15 13 20 L4 36" fill="{BONE}" stroke="{BONE}" stroke-width="2.4"/>
  </g>
</g>'''


def borrowed_armor():
    """Book 16: Patroclus in another man's armor — the empty helmet falls."""
    return f'''<g stroke="{BONE}" fill="none" stroke-linecap="round">
  <!-- the man, armored -->
  {_fighter(CX - 40, CY + 76, face=1, sc=1.7)}
  <!-- the helmet, struck off and falling -->
  <g transform="translate({CX+82},{CY-62}) rotate(28) scale(1.5)">
    <path d="M-24 16 a24 27 0 0 1 48 0 Z" fill="{BONE}" stroke="{BONE}" stroke-width="2"/>
    <path d="M-24 16 L-24 27 M24 16 L24 27" stroke="{BONE}" stroke-width="3"/>
    <path d="M-21 -10 q21 -24 42 -2 q-7 -18 -21 -18 q-14 0 -21 20 Z" fill="{BONE}" stroke="none"/>
  </g>
  <g stroke="{BONE}" stroke-width="2" opacity="0.6">
    <path d="M{CX+50} {CY+2} q12 20 26 32" />
  </g>
</g>'''


def _horse(x, y, sc=1.0, head_down=True, tears=False):
    """A Geometric horse in profile, facing right; head lowered if head_down."""
    if head_down:
        neck = ('<path d="M40 -46 L66 -26 L86 8 L64 14 L44 -18 Z" '
                f'fill="{BONE}" stroke="{BONE}" stroke-width="2"/>')
        ears = f'<path d="M56 -34 L52 -56 M70 -26 L72 -48" stroke="{BONE}" stroke-width="2.6"/>'
        mane = ('<path d="M40 -46 q14 -6 24 4 M24 -48 q14 -8 24 2 M8 -48 q14 -8 24 2" '
                f'stroke="{BONE}" stroke-width="2.4" opacity="0.9" fill="none"/>')
        tear = ('<g opacity="0.95">'
                f'<path d="M74 16 q-4 14 2 24" stroke="{BONE}" stroke-width="2.6" fill="none"/>'
                f'<path d="M85 12 q-3 12 2 20" stroke="{BONE}" stroke-width="2.6" fill="none"/></g>'
                ) if tears else ''
    else:
        neck = ('<path d="M40 -46 L62 -78 L88 -92 L94 -76 L70 -56 L52 -20 Z" '
                f'fill="{BONE}" stroke="{BONE}" stroke-width="2"/>')
        ears = f'<path d="M80 -92 L78 -114 M92 -88 L96 -108" stroke="{BONE}" stroke-width="2.6"/>'
        mane = ('<path d="M44 -50 q16 -14 22 -30 M28 -48 q18 -16 24 -32 M12 -46 q18 -16 24 -32" '
                f'stroke="{BONE}" stroke-width="2.4" opacity="0.9" fill="none"/>')
        tear = ''
    return f'''<g transform="translate({x},{y}) scale({sc})">
    <path d="M-66 -18 L40 -18 L40 -46 L-66 -46 Z" fill="{BONE}" stroke="{BONE}" stroke-width="2"/>
    <path d="M-58 -18 L-62 36 M-32 -18 L-34 36 M10 -18 L8 36 M34 -18 L38 36"
          stroke="{BONE}" stroke-width="4.4" fill="none"/>
    {neck}
    {ears}
    {mane}
    <circle cx="{74 if head_down else 84}" cy="{-8 if head_down else -84}" r="3.8"
            fill="#331323" stroke="none"/>
    <path d="M-66 -42 q-30 8 -34 42" stroke="{BONE}" stroke-width="4" fill="none"/>
    {tear}
  </g>'''


def weeping_horses():
    """Book 17: the immortal horses stand still, heads down, and weep."""
    return (f'<g stroke="{BONE}" fill="none" stroke-linecap="round">\n'
            f'  {_horse(CX - 16, CY + 14, sc=1.05, head_down=True, tears=True)}\n'
            f'  <line x1="{CX-118}" y1="{CY+96}" x2="{CX+118}" y2="{CY+96}" '
            f'stroke-width="2.4" opacity="0.75"/>\n'
            '</g>')


def _ocean_ring(cx, cy, r_mid, amp, n, width=2.6):
    """The river Ocean as one continuous wave that truly follows the circle.

    Flat wave stamps rotated around a ring don't meet — each is a chord, not an
    arc — so the band is drawn as a single closed path instead.
    """
    import math

    def pt(a, r):
        return (cx + r * math.cos(a), cy + r * math.sin(a))

    steps = n * 2
    a0 = -math.pi / 2
    d = []
    x0, y0 = pt(a0, r_mid)
    d.append(f"M{x0:.2f} {y0:.2f}")
    for i in range(steps):
        a1 = a0 + 2 * math.pi * (i + 1) / steps
        am = a0 + 2 * math.pi * (i + 0.5) / steps
        # a quadratic reaches about half its control offset, so double it
        off = amp * 2.0 if i % 2 == 0 else -amp * 2.0
        cxp, cyp = pt(am, r_mid + off)
        x1, y1 = pt(a1, r_mid)
        d.append(f"Q{cxp:.2f} {cyp:.2f} {x1:.2f} {y1:.2f}")
    d.append("Z")
    return (f'  <path d="{" ".join(d)}" fill="none" stroke="{BONE}" '
            f'stroke-width="{width}" stroke-linejoin="round"/>')


def shield_rings():
    """Book 18: the shield itself, in little — the same registers as the cover."""
    import math
    out = [f'<g stroke="{BONE}" fill="none">']
    # rim, then the ring lines that divide the registers
    out.append(f'  <circle cx="{CX}" cy="{CY}" r="128" stroke-width="3"/>')
    out.append(f'  <circle cx="{CX}" cy="{CY}" r="123" stroke-width="1.3" opacity="0.55"/>')
    for r in (103, 75, 42, 24):
        out.append(f'  <circle cx="{CX}" cy="{CY}" r="{r}" stroke-width="2.4"/>')

    # Ring 1: Ocean, band 103..123, centered on 113
    out.append(_ocean_ring(CX, CY, 113, 6.0, 14, width=2.6))

    # Ring 2: the dance, band 75..103 — figures upright, centered on the band
    for k in range(10):
        a = math.radians(k * 36)
        x, y = CX + 89 * math.sin(a), CY - 89 * math.cos(a)
        out.append(f'  <g transform="translate({x:.1f},{y:.1f}) scale(0.46)">'
                   f'<path d="M-9 14 L9 14 L0 -3 Z" fill="{BONE}"/>'
                   f'<path d="M0 -3 L7 -16 L-7 -16 Z" fill="{BONE}"/>'
                   f'<circle cx="0" cy="-22" r="5" fill="{BONE}"/>'
                   f'<path d="M-7 -14 L-19 -6 M7 -14 L19 -6" stroke="{BONE}" '
                   f'stroke-width="2.8" stroke-linecap="round" fill="none"/></g>')

    # Ring 3: the two cities, band 42..75 — spearmen above, oxen below
    for k in (-56, -19, 19, 56):
        a = math.radians(k)
        x, y = CX + 58 * math.sin(a), CY - 58 * math.cos(a)
        out.append(f'  <g transform="translate({x:.1f},{y:.1f}) scale(0.4)">'
                   f'<line x1="16" y1="12" x2="16" y2="-46" stroke="{BONE}" stroke-width="5" '
                   f'stroke-linecap="round"/>'
                   f'<path d="M-10 14 L10 14 L0 -2 Z" fill="{BONE}"/>'
                   f'<path d="M0 -2 L9 -18 L-9 -18 Z" fill="{BONE}"/>'
                   f'<circle cx="0" cy="-25" r="5.4" fill="{BONE}"/></g>')
    for k in (124, 161, 199, 236):
        a = math.radians(k)
        x, y = CX + 58 * math.sin(a), CY - 58 * math.cos(a)
        out.append(f'  <g transform="translate({x:.1f},{y:.1f}) scale(0.42)">'
                   f'<path d="M-17 -4 L13 -4 L13 -18 L-17 -18 Z" fill="{BONE}"/>'
                   f'<path d="M-14 -4 L-14 10 M-5 -4 L-5 10 M5 -4 L5 10 M11 -4 L11 10" '
                   f'stroke="{BONE}" stroke-width="2.8" fill="none"/>'
                   f'<path d="M13 -18 L24 -12 L24 -4 L15 -6 Z" fill="{BONE}"/></g>')

    # Ring 4: the constellations, band 24..42
    for k in range(6):
        a = math.radians(k * 60)
        x, y = CX + 33 * math.sin(a), CY - 33 * math.cos(a)
        out.append(f'  <g transform="translate({x:.1f},{y:.1f})" stroke="{BONE}" stroke-width="2">'
                   f'<line x1="-6" y1="0" x2="6" y2="0"/><line x1="0" y1="-6" x2="0" y2="6"/>'
                   f'<line x1="-4.2" y1="-4.2" x2="4.2" y2="4.2"/>'
                   f'<line x1="-4.2" y1="4.2" x2="4.2" y2="-4.2"/></g>')

    # the boss: the sun, with the moon left in reserve
    rays = "".join(
        f'<line x1="{16*math.cos(math.radians(k*45)):.1f}" y1="{16*math.sin(math.radians(k*45)):.1f}"'
        f' x2="{21*math.cos(math.radians(k*45)):.1f}" y2="{21*math.sin(math.radians(k*45)):.1f}"/>'
        for k in range(8))
    out.append(f'  <g transform="translate({CX},{CY})">'
               f'<circle cx="0" cy="0" r="13" fill="{BONE}" stroke="none"/>'
               f'<g stroke="{BONE}" stroke-width="2.2" stroke-linecap="round">{rays}</g></g>')
    out.append('</g>')
    return "\n".join(out)


def spear_horse():
    """Book 19: the great spear of Peleus, and Xanthus lifting his head to speak."""
    return f'''<g stroke="{BONE}" fill="none" stroke-linecap="round">
  <!-- the spear from Pelion, that no other man could wield -->
  <line x1="{CX-104}" y1="{CY-118}" x2="{CX-104}" y2="{CY+108}" stroke-width="5.5"/>
  <path d="M{CX-104} {CY-140} L{CX-118} {CY-108} L{CX-90} {CY-108} Z" fill="{BONE}" stroke="none"/>
  <path d="M{CX-118} {CY+108} L{CX-90} {CY+108}" stroke-width="4.5"/>
  <g stroke-width="2.2" opacity="0.7">
    <line x1="{CX-116}" y1="{CY-92}" x2="{CX-92}" y2="{CY-92}"/>
    <line x1="{CX-116}" y1="{CY-78}" x2="{CX-92}" y2="{CY-78}"/>
  </g>
  <!-- the horse, head up, foretelling -->
  {_horse(CX + 22, CY + 20, sc=0.92, head_down=False)}
</g>'''


def gods_descend():
    """Book 20: the gods come down, and then sit and watch."""
    out = [f'<g stroke="{BONE}" fill="none" stroke-linecap="round">']
    # the line of heaven, opening
    out.append(f'  <path d="M{CX-116} {CY-96} L{CX+116} {CY-96}" stroke-width="3"/>')
    out.append(f'  <path d="M{CX-70} {CY-96} L{CX-70} {CY-124} M{CX+70} {CY-96} L{CX+70} {CY-124}" '
               f'stroke-width="2.4" opacity="0.7"/>')
    # descending figures, dwindling
    for dx, dy, sc in ((-72, -30, 0.85), (0, 6, 1.0), (72, -30, 0.85)):
        out.append(f'  <g transform="translate({CX+dx},{CY+dy+40}) scale({sc})">')
        out.append(f'    <path d="M-12 0 L12 0 L0 -20 Z" fill="{BONE}"/>')
        out.append(f'    <path d="M0 -20 L10 -40 L-10 -40 Z" fill="{BONE}"/>')
        out.append(f'    <circle cx="0" cy="-48" r="6.5" fill="{BONE}"/>')
        out.append(f'    <path d="M-10 -36 L-30 -50 M10 -36 L30 -50" stroke="{BONE}" stroke-width="3"/>')
        out.append(f'    <path d="M-5 0 L-11 18 M5 0 L11 18" stroke="{BONE}" stroke-width="3.2"/>')
        out.append('  </g>')
    # the plain below
    out.append(f'  <line x1="{CX-110}" y1="{CY+92}" x2="{CX+110}" y2="{CY+92}" stroke-width="2.6"/>')
    out.append('</g>')
    return "\n".join(out)


def river_flood():
    """Book 21: Scamander rises against the man who choked him."""
    out = [f'<g stroke="{BONE}" fill="none" stroke-linecap="round">']
    # the river, rearing in a great curl
    out.append(f'  <path d="M{CX-124} {CY+92} C{CX-96} {CY-10} {CX-40} {CY-96} {CX+34} {CY-92} '
               f'C{CX+92} {CY-88} {CX+108} {CY-40} {CX+78} {CY-16} '
               f'C{CX+56} {CY+2} {CX+28} {CY-12} {CX+34} {CY-40}" stroke-width="4.5"/>')
    for i, o in enumerate((0.75, 0.5)):
        d = 18 + i * 16
        out.append(f'  <path d="M{CX-124+d} {CY+92} C{CX-96+d} {CY-4} {CX-40+d} {CY-80+d//2} '
                   f'{CX+34} {CY-76+d//2}" stroke-width="2.6" opacity="{o}"/>')
    # the man, breast-deep, holding on
    out.append(f'  <g transform="translate({CX-52},{CY+66})">')
    out.append(f'    <path d="M-13 0 L13 0 L0 -22 Z" fill="{BONE}"/>')
    out.append(f'    <path d="M0 -22 L11 -42 L-11 -42 Z" fill="{BONE}"/>')
    out.append(f'    <circle cx="0" cy="-50" r="7" fill="{BONE}"/>')
    out.append(f'    <path d="M-10 -38 L-32 -56 M10 -38 L30 -58" stroke="{BONE}" stroke-width="3.2"/>')
    out.append('  </g>')
    out.append(f'  <path d="M{CX-124} {CY+92} q60 22 124 8 q60 -14 124 6" stroke-width="3.2" opacity="0.9"/>')
    out.append('</g>')
    return "\n".join(out)


def walls_chase():
    """Book 22: one man outside the wall, run down beneath the tower."""
    out = [f'<g stroke="{BONE}" fill="none" stroke-linecap="round">']
    # the wall and tower on the left
    out.append(f'  <path d="M{CX-124} {CY+96} L{CX-124} {CY-56} L{CX-46} {CY-56} L{CX-46} {CY+96}" '
               f'stroke-width="3.4"/>')
    for i in range(4):
        x = CX - 124 + i * 26
        out.append(f'  <path d="M{x} {CY-56} L{x} {CY-74} L{x+13} {CY-74} L{x+13} {CY-56}" stroke-width="2.6"/>')
    for r in range(3):
        y = CY - 26 + r * 38
        out.append(f'  <line x1="{CX-124}" y1="{y}" x2="{CX-46}" y2="{y}" stroke-width="2"/>')
    # the two runners on the right, one close behind the other
    out.append(_fighter(CX + 10, CY + 80, face=1, sc=1.3, shield=False))
    out.append(_fighter(CX + 96, CY + 80, face=1, sc=1.4))
    out.append(f'  <line x1="{CX-40}" y1="{CY+96}" x2="{CX+124}" y2="{CY+96}" stroke-width="2.4" opacity="0.8"/>')
    out.append('</g>')
    return "\n".join(out)


def chariot_turn():
    """Book 23: the funeral games — the chariot at the turning-post."""
    return f'''<g stroke="{BONE}" fill="none" stroke-linecap="round">
  <!-- the turning post -->
  <line x1="{CX+96}" y1="{CY-84}" x2="{CX+96}" y2="{CY+80}" stroke-width="5"/>
  <path d="M{CX+96} {CY-84} l-12 16 l24 0 Z" fill="{BONE}" stroke="none"/>
  <!-- the horses -->
  <g transform="translate({CX-58},{CY-6})">
    <path d="M-46 -6 L34 -6 L34 -30 L-46 -30 Z" fill="{BONE}" stroke="{BONE}" stroke-width="2"/>
    <path d="M-40 -6 L-46 30 M-16 -6 L-20 30 M10 -6 L8 30 M30 -6 L34 30" stroke="{BONE}" stroke-width="3.4"/>
    <path d="M34 -30 L62 -14 L70 4 L52 8 L38 -8 Z" fill="{BONE}" stroke="{BONE}" stroke-width="2"/>
    <path d="M52 -20 L48 -40 M62 -16 L64 -36" stroke="{BONE}" stroke-width="2.4"/>
    <path d="M-46 -26 q-24 8 -26 30" stroke="{BONE}" stroke-width="2.8"/>
  </g>
  <!-- the car and its wheel -->
  <g transform="translate({CX-104},{CY+34})">
    <path d="M-30 0 L26 0 L26 -34 q-28 -12 -56 0 Z" fill="none" stroke="{BONE}" stroke-width="3"/>
    <circle cx="-2" cy="20" r="22" stroke="{BONE}" stroke-width="3"/>
    <g stroke="{BONE}" stroke-width="2.2">
      <line x1="-24" y1="20" x2="20" y2="20"/><line x1="-2" y1="-2" x2="-2" y2="42"/>
      <line x1="-17" y1="5" x2="13" y2="35"/><line x1="-17" y1="35" x2="13" y2="5"/>
    </g>
    <path d="M26 -20 L74 -26" stroke="{BONE}" stroke-width="2.6"/>
  </g>
</g>'''


def kneeling_king():
    """Book 24: the old king kneels and kisses the hands that killed his sons."""
    return f'''<g stroke="{BONE}" fill="none" stroke-linecap="round">
  <!-- Achilles, seated on the chair, leaning toward the old man -->
  <g transform="translate({CX+56},{CY+58})">
    <!-- the chair -->
    <path d="M34 4 L34 -86 M34 -86 L6 -86" stroke="{BONE}" stroke-width="3.4"/>
    <path d="M-14 4 L38 4" stroke="{BONE}" stroke-width="3.4"/>
    <path d="M-10 4 L-12 40 M32 4 L36 40" stroke="{BONE}" stroke-width="3.4"/>
    <!-- seated body: thigh, then torso rising -->
    <path d="M-16 -6 L26 -6 L26 -22 L-16 -22 Z" fill="{BONE}" stroke="{BONE}" stroke-width="2"/>
    <path d="M6 -22 L22 -74 L2 -74 L-6 -22 Z" fill="{BONE}" stroke="{BONE}" stroke-width="2"/>
    <circle cx="8" cy="-86" r="10" fill="{BONE}"/>
    <!-- the shin, dropped to the floor -->
    <path d="M-16 -12 L-30 30 L-14 34" stroke="{BONE}" stroke-width="4.5"/>
    <!-- the arm reaching down: the hand that is being kissed -->
    <path d="M2 -66 L-42 -34" stroke="{BONE}" stroke-width="4"/>
    <path d="M-42 -34 q-12 4 -16 12" stroke="{BONE}" stroke-width="4"/>
  </g>
  <!-- Priam, on his knees, bent to those hands -->
  <g transform="translate({CX-52},{CY+62})">
    <!-- the knees and the long robe -->
    <path d="M-46 34 L34 34 L26 -12 L-30 -12 Z" fill="{BONE}" stroke="{BONE}" stroke-width="2"/>
    <!-- the bowed back and shoulders -->
    <path d="M-30 -12 L-18 -58 L14 -50 L26 -12 Z" fill="{BONE}" stroke="{BONE}" stroke-width="2"/>
    <!-- the head, bowed forward, and the old man's beard -->
    <circle cx="16" cy="-64" r="10" fill="{BONE}"/>
    <path d="M22 -56 q-6 20 4 30" stroke="{BONE}" stroke-width="3" opacity="0.95"/>
    <!-- both arms lifted to the hand above -->
    <path d="M10 -52 L48 -40 M6 -42 L44 -30" stroke="{BONE}" stroke-width="3.6"/>
  </g>
  <line x1="{CX-118}" y1="{CY+98}" x2="{CX+118}" y2="{CY+98}" stroke-width="2.4" opacity="0.8"/>
</g>'''


EMBLEMS = {
    "plague-arrows": plague_arrows, "ships-row": ships_row, "duel-pair": duel_pair,
    "bow-arrow": bow_arrow, "wounded-god": wounded_god, "helmet-child": helmet_child,
    "wall-course": wall_course, "scales": scales, "three-tripods": three_tripods,
    "night-wolf": night_wolf, "sun-spears": sun_spears, "gate-stone": gate_stone,
    "trident-wave": trident_wave, "girdle": girdle, "ship-stern": ship_stern,
    "borrowed-armor": borrowed_armor, "weeping-horses": weeping_horses,
    "shield-rings": shield_rings, "spear-horse": spear_horse,
    "gods-descend": gods_descend, "river-flood": river_flood,
    "walls-chase": walls_chase, "chariot-turn": chariot_turn,
    "kneeling-king": kneeling_king,
}


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    for n in range(1, 25):
        _, emblem = BOOKS[n]
        svg = head(n) + "\n  " + EMBLEMS[emblem]() + "\n" + foot(n)
        path = os.path.join(here, f"book_{n:02d}.svg")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(svg)
    print(f"wrote 24 plates to {here}")


if __name__ == "__main__":
    main()
