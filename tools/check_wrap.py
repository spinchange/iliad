#!/usr/bin/env python3
"""Validate a case-wrap PDF against a print supplier's requirements.

Ported from the Odyssey project's tools/check_wrap.py. Checks, in the
supplier's own terms:

  File Type    a readable PDF
  Page Count   exactly 1
  Dimensions   the given trim, to within a rounding tolerance
  Spine Width  the given spine (reported; geometry is checked against it)
  Fonts        every font that draws a glyph is embedded
  Layers       flattened: no optional content groups, no annotations,
               no form fields

and two things the spec implies but does not say:

  Bleed        the artwork reaches all four edges (no white border)
  Safe area    nothing light-coloured sits inside the bleed, where a
               trim would cut it

The spine defaults to the built interior's page count (like build_wrap).

Usage:
    python tools/check_wrap.py art/iliad-wrap.pdf
    python tools/check_wrap.py <pdf> --pages 812
    python tools/check_wrap.py <pdf> --spine 1.889
"""
from __future__ import annotations
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_wrap import (PANEL_IN, WRAP_H_IN, spine_for,  # noqa: E402
                        interior_pages, INTERIOR)

SIZE_TOL_PT = 0.1


def check(pdf: Path, width_in: float, height_in: float, spine_in: float) -> int:
    try:
        from pypdf import PdfReader
    except ImportError:
        sys.exit("check_wrap.py needs pypdf:  pip install pypdf")

    problems: list[str] = []
    notes: list[str] = []
    reader = PdfReader(str(pdf))

    n = len(reader.pages)
    if n != 1:
        problems.append(f"page count is {n}, must be exactly 1")
    page = reader.pages[0]

    box = page.mediabox
    w_pt, h_pt = float(box.width), float(box.height)
    want_w, want_h = width_in * 72, height_in * 72
    if abs(w_pt - want_w) > SIZE_TOL_PT or abs(h_pt - want_h) > SIZE_TOL_PT:
        problems.append(f"page is {w_pt / 72:.4f} x {h_pt / 72:.4f} in, "
                        f"required {width_in:.3f} x {height_in:.3f} in")
    else:
        notes.append(f"page {w_pt / 72:.4f} x {h_pt / 72:.4f} in "
                     f"({w_pt / 72 * 25.4:.2f} x {h_pt / 72 * 25.4:.2f} mm)")
    for name in ("/CropBox", "/TrimBox", "/BleedBox", "/ArtBox"):
        b = page.get(name)
        if b is None:
            continue
        b = b.get_object()
        if (abs(float(b.width) - w_pt) > SIZE_TOL_PT
                or abs(float(b.height) - h_pt) > SIZE_TOL_PT):
            problems.append(f"{name} is {float(b.width) / 72:.4f} x "
                            f"{float(b.height) / 72:.4f} in, smaller than the page — "
                            "this crops the bleed")

    panel_in = (width_in - spine_in) / 2
    notes.append(f"spine {spine_in:.3f} in, panels {panel_in:.4f} in each")

    def deref(x):
        return x.get_object() if hasattr(x, "get_object") else x

    def fonts_of(pg) -> dict[str, bool]:
        out: dict[str, bool] = {}
        stack = [deref(pg.get("/Resources"))]
        seen_ids: set[int] = set()
        while stack:
            r = deref(stack.pop())
            if not isinstance(r, dict) or id(r) in seen_ids:
                continue
            seen_ids.add(id(r))
            fd = deref(r.get("/Font"))
            for _k, ref in (fd.items() if isinstance(fd, dict) else []):
                f = deref(ref)
                if not isinstance(f, dict):
                    continue
                base = str(f.get("/BaseFont", "?")).lstrip("/")
                desc = deref(f.get("/FontDescriptor"))
                if not isinstance(desc, dict):
                    df = deref(f.get("/DescendantFonts"))
                    if isinstance(df, list) and df:
                        desc = deref(deref(df[0]).get("/FontDescriptor"))
                emb = isinstance(desc, dict) and any(
                    k in desc for k in ("/FontFile", "/FontFile2", "/FontFile3"))
                out[base] = out.get(base, False) or emb
            xo = deref(r.get("/XObject"))
            for _k, ref in (xo.items() if isinstance(xo, dict) else []):
                x = deref(ref)
                if isinstance(x, dict) and "/Resources" in x:
                    stack.append(x["/Resources"])
        return out

    fonts = fonts_of(page)
    not_emb = sorted(k for k, v in fonts.items() if not v)
    if not_emb:
        problems.append("fonts not embedded: " + ", ".join(not_emb))
    elif fonts:
        notes.append(f"{len(fonts)} font(s), all embedded: " + ", ".join(sorted(fonts)))
    else:
        notes.append("no text fonts (artwork is paths only)")

    root = reader.trailer["/Root"].get_object()
    if "/OCProperties" in root:
        problems.append("the PDF has optional content groups (layers) — must be flattened")
    annots = page.get("/Annots")
    if annots and len(annots.get_object()):
        problems.append(f"{len(annots.get_object())} annotation(s) present")
    if "/AcroForm" in root:
        problems.append("form fields present — must be flattened")

    res = page.get("/Resources")
    res = res.get_object() if hasattr(res, "get_object") else (res or {})
    if isinstance(res, dict):
        if "/Group" in page:
            grp = deref(page["/Group"])
            if isinstance(grp, dict) and str(grp.get("/S")) == "/Transparency":
                notes.append("page has a transparency group (usually fine; "
                             "flatten if the supplier rejects it)")
        egs = deref(res.get("/ExtGState")) or {}
        soft = [str(k) for k, ref in (egs.items() if isinstance(egs, dict) else [])
                if isinstance(deref(ref), dict) and deref(ref).get("/SMask") not in (None, "/None")]
        if soft:
            notes.append(f"{len(soft)} soft mask(s) in ExtGState — transparency is "
                         "present but rasterizes cleanly")

    imgs = []
    seen: set[int] = set()

    def scan_images(r) -> None:
        r = deref(r)
        if not isinstance(r, dict) or id(r) in seen:
            return
        seen.add(id(r))
        xo = deref(r.get("/XObject"))
        for _k, ref in (xo.items() if isinstance(xo, dict) else []):
            o = deref(ref)
            if not isinstance(o, dict):
                continue
            if str(o.get("/Subtype")) == "/Image":
                iw, ih = int(o.get("/Width", 0)), int(o.get("/Height", 0))
                imgs.append((iw, ih, iw / (w_pt / 72) if w_pt else 0))
            else:
                scan_images(o.get("/Resources"))
        pats = deref(r.get("/Pattern"))
        for _k, ref in (pats.items() if isinstance(pats, dict) else []):
            o = deref(ref)
            if isinstance(o, dict):
                scan_images(o.get("/Resources"))
        gs = deref(r.get("/ExtGState"))
        for _k, ref in (gs.items() if isinstance(gs, dict) else []):
            o = deref(ref)
            sm = deref(o.get("/SMask")) if isinstance(o, dict) else None
            if isinstance(sm, dict) and sm.get("/G") is not None:
                scan_images(deref(sm["/G"]).get("/Resources"))

    scan_images(res)
    # Effective resolution: the image's pixels over the width it is actually
    # printed at, which pdfplumber reports per placement. The pypdf scan
    # above only says the image exists; a 1024 px shield printed 2.46 in
    # wide is 416 ppi, not 1024 over the whole page.
    placed: list[tuple[int, int, float]] = []
    try:
        import pdfplumber
        with pdfplumber.open(str(pdf)) as pl:
            for im in pl.pages[0].images:
                sw, sh = im.get("srcsize", (0, 0))
                wid_in = (im["x1"] - im["x0"]) / 72
                if sw and wid_in:
                    placed.append((sw, sh, sw / wid_in))
    except ImportError:
        pass
    if placed:
        for sw, sh, ppi in placed:
            if ppi < 300:
                problems.append(f"embedded image {sw}x{sh} prints at {ppi:.0f} ppi — "
                                "print needs 300 ppi or better")
            else:
                notes.append(f"embedded image {sw}x{sh} prints at {ppi:.0f} ppi")
    elif imgs:
        notes.append(f"{len(imgs)} raster image(s) present (install pdfplumber to "
                     "measure their printed resolution)")
    else:
        notes.append("no raster images — fully vector")

    try:
        import pypdfium2 as pdfium
    except ImportError:
        notes.append("(install pypdfium2 to check bleed and safe area)")
    else:
        doc = pdfium.PdfDocument(str(pdf))
        img = doc[0].render(scale=2.0).to_pil().convert("RGB")
        pw, ph = img.size
        px = img.load()

        def white(pts):
            return sum(1 for x, y in pts if min(px[x, y]) > 235)

        sx, sy = max(1, pw // 300), max(1, ph // 300)
        for name, pts in (
            ("top", [(x, 0) for x in range(0, pw, sx)]),
            ("bottom", [(x, ph - 1) for x in range(0, pw, sx)]),
            ("left", [(0, y) for y in range(0, ph, sy)]),
            ("right", [(pw - 1, y) for y in range(0, ph, sy)]),
        ):
            k = white(pts)
            if k:
                problems.append(f"{name} edge has {k}/{len(pts)} near-white samples — "
                                "the artwork does not bleed to that edge")

        ppi_x = pw / (w_pt / 72)
        ppi_y = ph / (h_pt / 72)
        margin_x = int(0.125 * ppi_x)
        margin_y = int(0.125 * ppi_y)

        def light_in(x0, x1, y0, y1):
            n = 0
            for x in range(max(0, x0), min(pw, x1), max(1, (x1 - x0) // 120)):
                for y in range(max(0, y0), min(ph, y1), max(1, (y1 - y0) // 120)):
                    r, g, b = px[x, y]
                    if r > 150 and g > 130:
                        n += 1
            return n

        for name, (x0, x1, y0, y1) in {
            "top": (0, pw, 0, margin_y),
            "bottom": (0, pw, ph - margin_y, ph),
            "left": (0, margin_x, 0, ph),
            "right": (pw - margin_x, pw, 0, ph),
        }.items():
            k = light_in(x0, x1, y0, y1)
            if k:
                problems.append(f"{k} light pixel(s) inside the {name} bleed area — "
                                "artwork that must survive trimming is too close to the edge")
        notes.append(f"spine folds at x={panel_in:.4f} and {panel_in + spine_in:.4f} in")

    print(f"{pdf.name}")
    for s in notes:
        print(f"  - {s}")
    if problems:
        print("\nFAIL")
        for p in problems:
            print(f"  * {p}")
        return 1
    print("\nOK — meets the supplier requirements")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf", type=Path)
    ap.add_argument("--pages", type=int, default=None,
                    help="interior page count (default: the built interior's)")
    ap.add_argument("--spine", type=float, default=None, help="spine width in inches")
    ap.add_argument("--width", type=float, default=None,
                    help="overall width in inches (default: two panels plus the spine)")
    ap.add_argument("--height", type=float, default=WRAP_H_IN)
    args = ap.parse_args()
    if args.spine is not None:
        spine = args.spine
    else:
        pages = args.pages if args.pages is not None else interior_pages()
        if pages is None:
            sys.exit(f"no built interior at {INTERIOR}; give --pages or --spine")
        spine = spine_for(pages)
    width = args.width if args.width is not None else round(2 * PANEL_IN + spine, 3)
    sys.exit(check(args.pdf, width, args.height, spine))
