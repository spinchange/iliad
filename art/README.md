# Iliad artwork

Companion set to `odyssey/art/`. Same visual system: wine-dark ground
(`#46192b` → `#1e0b15`), pale-bone line work (`#ead9b4`), gold accents
(`#c99b3f`), Palatino display type, meander bands, and a fine noise grain.

Where the Odyssey art carries a Geometric-period ship, the Iliad art carries
the **Shield of Achilles** — the poem's own ekphrasis at 18.478–608, built as
concentric registers:

| ring | content | lines |
|---|---|---|
| rim | the triple rim, bright and glittering | 18.479 |
| 1 | the great strength of the river Ocean | 18.607–608 |
| 2 | the dancing floor Daedalus made at Knossos | 18.590–606 |
| 3 | the two cities: war above, plowland and herds below | 18.509–586 |
| 4 | the constellations with which heaven is crowned | 18.485–489 |
| boss | the unwearied sun and the moon at her full | 18.484 |

### Ring geometry

The shield sits centered in its register with equal clearance top and bottom
(cover: center `(400, 808)`, outer radius `164`, spanning `644..972` between
rules at `626` and `990`). Each figure is scaled and offset so its glyph is
centered on its band's midline rather than sitting on the ring line.

One constraint worth keeping: **the Ocean band is a single continuous path, not
repeated wave stamps.** A flat wave glyph rotated around a circle is a chord,
not an arc, so consecutive copies never meet — the band breaks into a chain of
loops. `_ocean_ring()` in `make_plates.py` draws it as one closed path of
alternating quadratic arcs whose control points are pushed out radially
(a quadratic reaches about half its control offset, hence the `* 2.0`).

## Files

| file | size | use |
|---|---|---|
| `iliad-cover.svg` | 800×1200 | book cover |
| `iliad-social.svg` | 1200×630 | social share card, with a slot for a URL |
| `iliad-social-nourl.svg` | 1200×630 | social share card, no URL |
| `iliad-social-shield-nourl.svg` | 1200×630 | social share card, photoreal shield, no URL |
| `iliad-social-shield-nourl.png` | 1200×630 | rendered PNG of the above (`@2x` = 2400×1260) |
| `book_01.svg` … `book_24.svg` | 600×800 | per-book plates |
| `make_plates.py` | — | regenerates the 24 plates |

Two shields are in play. The vector shield (`iliad-cover.svg`, `iliad-social*.svg`)
draws the ekphrasis as Geometric line work in the shared visual system. The
photoreal shield is a bronze relief rendering (`shield_of_achilles.jpg`), used by
`iliad-cover-hybrid.svg` and `iliad-social-shield-nourl.svg`.

The two embed it differently. The hybrid cover references the JPEG by relative
path, so it only renders with the file alongside it. The shield social card
**embeds the image as a base64 data URI**, so it is self-contained like the rest
of the set and can be posted or hotlinked on its own — at the cost of a ~200 KB
file. If you re-crop the source, the disc in `shield_of_achilles.jpg` is centered
at `(508, 506)` with a rim radius of about `492` in the 1024×1024 original; the
card crops to `(16, 14, 1000, 998)`, clips to `r=211` and rings it at `r=215` so
the pale-bone rim reads outside the bronze.

No domain is baked into any file. `iliad-social.svg` has a commented-out
`<text>` element near the end of its title block; uncomment it and fill in the
domain when one is chosen. (Until then it renders identically to the no-URL
variant — both are kept so the set stays parallel with the Odyssey's three.)

The line count in the byline — 24 books, 15,687 lines — matches the numbered
verse lines in `translation/book_*.txt`.

## Per-book plates

Each plate pairs a Roman numeral with a single emblem drawn from that book's
own action: Apollo's falling arrows (I), the beached ships of the Catalogue
(II), the golden scales (VIII), the three tripods of the Embassy (IX), the
wolf-skinned night raid (X), the gate bursting (XII), Poseidon's trident
(XIII), Hera and winged Sleep (XIV), the weeping immortal horses (XVII), the
shield itself in little (XVIII), the river rearing (XXI), and Priam at the
hands of Achilles (XXIV).

To change a title or emblem, edit the `BOOKS` table at the top of
`make_plates.py` and re-run it:

```
cd art && python make_plates.py
```

## Rendering to PNG

The SVGs are self-contained (no external fonts or assets) and use only
`Palatino Linotype`/`Book Antiqua`/`Palatino`/Georgia with a serif fallback,
so any renderer works. Headless Chrome:

```
chrome --headless --disable-gpu --screenshot=cover.png \
       --window-size=800,1200 iliad-cover.svg
```
