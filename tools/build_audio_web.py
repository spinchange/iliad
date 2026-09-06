"""Publish the finished narration as web audio.

Reads the lossless per-book masters that tools/build_audiobook.py concatenates
(audiobook-build/production/book-NN/books/book-NN-full.wav), encodes each one
as a small AAC file with the cover embedded, records what was published in
audiobook/published.json (tracked in git, so the web build knows which books
have audio), writes the podcast feed, and uploads the files to the R2 bucket
that serves audio.wrath-sing-goddess.com.

    python tools/build_audio_web.py encode            # every book with a master
    python tools/build_audio_web.py encode --books 7 8
    python tools/build_audio_web.py feed              # docs/podcast.xml
    python tools/build_audio_web.py upload            # wrangler r2 object put
    python tools/build_audio_web.py status

`encode` skips a book whose master is unchanged since the last encode unless
--force is given. `upload` uses the OAuth login from `npx wrangler login`
(run it with CLOUDFLARE_API_TOKEN unset) and PUTs through the R2 REST API.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

import requests
from email.utils import format_datetime
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
PRODUCTION = ROOT / "audiobook-build" / "production"
OUT = ROOT / "audiobook-build" / "web"
PUBLISHED = ROOT / "audiobook" / "published.json"
FEED = ROOT / "docs" / "podcast.xml"
COVER = ROOT / "docs" / "cover.jpg"
SRC = ROOT / "translation"

SITE = "https://wrath-sing-goddess.com"
AUDIO_BASE = "https://audio.wrath-sing-goddess.com"
BUCKET = "wrath-sing-goddess-audio"
ACCOUNT_ID = "e71381d1cd8e6516fd5f2647d8d10ca6"
BITRATE = "96k"
AUTHOR = "Chris Duffy"
ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI",
         "XII", "XIII", "XIV", "XV", "XVI", "XVII", "XVIII", "XIX", "XX",
         "XXI", "XXII", "XXIII", "XXIV"]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def probe_duration(path: Path) -> float:
    out = subprocess.run(
        [shutil.which("ffprobe") or "ffprobe", "-v", "error", "-show_entries",
         "format=duration", "-of", "csv=p=0", str(path)],
        check=True, text=True, capture_output=True).stdout.strip()
    return float(out)


def argument_for(book: int) -> str:
    """The one-sentence argument printed under the book heading."""
    text = (SRC / f"book_{book:02d}.txt").read_text(encoding="utf-8")
    m = re.search(r"^BOOK \d+\s*\n+(.+?)\n\s*\n", text, re.M | re.S)
    return " ".join(m.group(1).split()) if m else ""


def load_published() -> dict:
    if PUBLISHED.exists():
        return json.loads(PUBLISHED.read_text(encoding="utf-8"))
    return {"audio_base": AUDIO_BASE, "bitrate": BITRATE, "books": {}}


def save_published(data: dict) -> None:
    data["audio_base"] = AUDIO_BASE
    data["bitrate"] = BITRATE
    data["books"] = dict(sorted(data["books"].items()))
    PUBLISHED.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                         encoding="utf-8", newline="\n")


def master_for(book: int) -> Path | None:
    path = PRODUCTION / f"book-{book:02d}" / "books" / f"book-{book:02d}-full.wav"
    return path if path.exists() else None


def human_review(book: int) -> str:
    manifest = PRODUCTION / f"book-{book:02d}" / "manifest.json"
    if not manifest.exists():
        return "missing"
    data = json.loads(manifest.read_text(encoding="utf-8"))
    return (data.get("human_review") or {}).get("status") or "unreviewed"


def encode(args: argparse.Namespace) -> None:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise SystemExit("ffmpeg is required.")
    OUT.mkdir(parents=True, exist_ok=True)
    published = load_published()
    books = [int(b) for b in args.books] if args.books else list(range(1, 25))
    done = 0
    for book in books:
        master = master_for(book)
        if master is None:
            print(f"book {book:02d}: no master yet")
            continue
        key = f"{book:02d}"
        master_hash = sha256_file(master)
        entry = published["books"].get(key)
        target = OUT / f"book-{key}.m4a"
        if (entry and not args.force and entry.get("master_sha256") == master_hash
                and target.exists() and sha256_file(target) == entry.get("sha256")):
            print(f"book {key}: unchanged")
            continue
        title = f"The Iliad, Book {ROMAN[book - 1]}"
        command = [
            ffmpeg, "-y", "-v", "error",
            "-i", str(master), "-i", str(COVER),
            "-map", "0:a", "-map", "1:v",
            "-c:a", "aac", "-b:a", BITRATE, "-ac", "1",
            "-c:v", "mjpeg", "-disposition:v", "attached_pic",
            "-metadata", f"title={title}",
            "-metadata", f"artist={AUTHOR}",
            "-metadata", "album=The Iliad — Wrath, Sing, Goddess",
            "-metadata", f"track={book}/24",
            "-metadata", "genre=Audiobook",
            "-metadata", f"comment={argument_for(book)}",
            "-movflags", "+faststart",
            str(target),
        ]
        subprocess.run(command, check=True)
        duration = probe_duration(target)
        published["books"][key] = {
            "book": book,
            "title": title,
            "argument": argument_for(book),
            "file": target.name,
            "url": f"{AUDIO_BASE}/{target.name}",
            "bytes": target.stat().st_size,
            "duration_seconds": round(duration, 3),
            "sha256": sha256_file(target),
            "master_sha256": master_hash,
            "human_review": human_review(book),
            "encoded_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
            "uploaded_sha256": (entry or {}).get("uploaded_sha256"),
        }
        save_published(published)
        minutes = duration / 60
        print(f"book {key}: {target.stat().st_size / 1e6:.1f} MB, {minutes:.1f} min")
        done += 1
    print(f"Encoded {done} book(s); {len(published['books'])} recorded in {PUBLISHED.relative_to(ROOT)}")


def feed(args: argparse.Namespace) -> None:
    published = load_published()
    items = []
    # Newest-first is the podcast convention, but a poem reads in order:
    # publish dates step forward by book so apps that sort by date keep it.
    base_date = dt.datetime(2026, 9, 5, 12, 0, tzinfo=dt.timezone.utc)
    preview = os.environ.get("AUDIO_PREVIEW") == "1"
    for key, e in sorted(published["books"].items(), reverse=True):
        if not preview and e.get("uploaded_sha256") != e["sha256"]:
            continue  # the feed must only point at files that are live
        when = base_date + dt.timedelta(minutes=int(key))
        secs = int(round(e["duration_seconds"]))
        hms = f"{secs // 3600}:{secs % 3600 // 60:02d}:{secs % 60:02d}"
        desc = escape(e["argument"] or e["title"])
        items.append(f"""    <item>
      <title>{escape(e["title"])}</title>
      <itunes:title>Book {ROMAN[e["book"] - 1]}</itunes:title>
      <itunes:episode>{e["book"]}</itunes:episode>
      <itunes:episodeType>full</itunes:episodeType>
      <description>{desc}</description>
      <link>{SITE}/read/book-{key}.html</link>
      <guid isPermaLink="false">wrath-sing-goddess-book-{key}</guid>
      <pubDate>{format_datetime(when)}</pubDate>
      <enclosure url="{e["url"]}" length="{e["bytes"]}" type="audio/mp4"/>
      <itunes:duration>{hms}</itunes:duration>
      <itunes:explicit>false</itunes:explicit>
    </item>""")
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd"
     xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>The Iliad — Wrath, Sing, Goddess</title>
    <link>{SITE}/</link>
    <atom:link href="{SITE}/podcast.xml" rel="self" type="application/rss+xml"/>
    <language>en</language>
    <description>Homer's Iliad, complete, in a line-for-line English translation from the Greek, read aloud one book at a time.</description>
    <itunes:author>{escape(AUTHOR)}</itunes:author>
    <itunes:summary>Homer's Iliad, complete, in a line-for-line English translation from the Greek, read aloud one book at a time.</itunes:summary>
    <itunes:type>serial</itunes:type>
    <itunes:explicit>false</itunes:explicit>
    <itunes:image href="{SITE}/cover.jpg"/>
    <image><url>{SITE}/cover.jpg</url><title>The Iliad — Wrath, Sing, Goddess</title><link>{SITE}/</link></image>
    <itunes:category text="Arts"><itunes:category text="Books"/></itunes:category>
    <itunes:owner><itunes:name>{escape(AUTHOR)}</itunes:name></itunes:owner>
{chr(10).join(items)}
  </channel>
</rss>
"""
    FEED.write_text(xml, encoding="utf-8", newline="\n")
    print(f"Wrote {FEED.relative_to(ROOT)} with {len(items)} episode(s)")


WRANGLER_CONFIG = Path(os.environ.get("APPDATA", "")) / "xdg.config" / ".wrangler" / "config" / "default.toml"
R2_API = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/r2/buckets/{BUCKET}/objects"


def oauth_token() -> str:
    """The token from `npx wrangler login`, refreshed first if it is stale.

    wrangler's own `r2 object put` fails intermittently on this machine with
    a bare "fetch failed", so uploads go straight to the R2 REST API with
    curl, which streams the file reliably."""
    npx = shutil.which("npx") or shutil.which("npx.cmd")
    env = dict(os.environ, CLOUDFLARE_API_TOKEN="", CLOUDFLARE_ACCOUNT_ID=ACCOUNT_ID)
    subprocess.run([npx, "-y", "wrangler", "whoami"], env=env, shell=(os.name == "nt"),
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    text = WRANGLER_CONFIG.read_text(encoding="utf-8")
    m = re.search(r'oauth_token\s*=\s*"([^"]+)"', text)
    if not m:
        raise SystemExit(f"No OAuth token in {WRANGLER_CONFIG}; run: npx wrangler login")
    return m.group(1)


def upload(args: argparse.Namespace) -> None:
    published = load_published()
    books = [f"{int(b):02d}" for b in args.books] if args.books else sorted(published["books"])
    token = oauth_token()
    sent = 0
    for key in books:
        e = published["books"].get(key)
        if not e:
            print(f"book {key}: not encoded")
            continue
        path = OUT / e["file"]
        if not path.exists() or sha256_file(path) != e["sha256"]:
            raise SystemExit(f"{path} is missing or differs from published.json; re-run encode.")
        if e.get("uploaded_sha256") == e["sha256"] and not args.force:
            print(f"book {key}: already uploaded")
            continue
        # Windows curl (schannel) and wrangler both drop large PUTs here;
        # requests streams over OpenSSL and has been reliable. Stage a local
        # copy first because reads from the synced H: drive stall.
        staged = Path(tempfile.gettempdir()) / e["file"]
        shutil.copyfile(path, staged)
        print(f"put {BUCKET}/{e['file']} ({e['bytes'] / 1e6:.1f} MB)", flush=True)
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "audio/mp4",
            "Content-Length": str(e["bytes"]),
            "cf-r2-metadata": json.dumps({
                "contentType": "audio/mp4",
                "cacheControl": "public, max-age=31536000, immutable"}),
        }
        reply: dict = {}
        for attempt in range(1, 5):
            try:
                with staged.open("rb") as fh:
                    response = requests.put(f"{R2_API}/{e['file']}", data=fh,
                                            headers=headers, timeout=(30, 600))
                reply = response.json() if response.content else {}
                if response.ok and reply.get("success"):
                    break
                print(f"  attempt {attempt}: HTTP {response.status_code} {response.text[:200]}", flush=True)
            except (requests.RequestException, ValueError) as exc:
                print(f"  attempt {attempt}: {exc}", flush=True)
            time.sleep(5 * attempt)
        staged.unlink(missing_ok=True)
        if not reply.get("success"):
            raise SystemExit(f"upload failed for {e['file']} after 4 attempts")
        size = int(reply["result"]["size"])
        if size != e["bytes"]:
            raise SystemExit(f"R2 stored {size} bytes for {e['file']}, expected {e['bytes']}")
        e["uploaded_sha256"] = e["sha256"]
        e["uploaded_at"] = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
        save_published(published)
        sent += 1
    print(f"Uploaded {sent} file(s) to {BUCKET}")


def status(args: argparse.Namespace) -> None:
    published = load_published()
    total = 0.0
    print("book  review      encoded  uploaded  minutes    MB")
    for book in range(1, 25):
        key = f"{book:02d}"
        e = published["books"].get(key)
        master = master_for(book)
        review = human_review(book)
        if e:
            up = "yes" if e.get("uploaded_sha256") == e["sha256"] else "no"
            total += e["duration_seconds"]
            print(f"{key:>4}  {review:<10}  yes      {up:<8}  {e['duration_seconds'] / 60:7.1f}  {e['bytes'] / 1e6:5.1f}")
        else:
            print(f"{key:>4}  {review:<10}  {'no' if master else 'no master':<8}")
    print(f"published total: {total / 3600:.2f} hours")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("encode"); p.add_argument("--books", nargs="*"); p.add_argument("--force", action="store_true")
    sub.add_parser("feed")
    p = sub.add_parser("upload"); p.add_argument("--books", nargs="*"); p.add_argument("--force", action="store_true")
    sub.add_parser("status")
    args = parser.parse_args(argv)
    {"encode": encode, "feed": feed, "upload": upload, "status": status}[args.command](args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
