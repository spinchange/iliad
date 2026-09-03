"""Build and quality-control a staged Iliad audiobook pilot.

The source translation is never modified.  The pipeline is deliberately
gated:

    prepare -> synthesize -> qa -> accept -> concat -> captions

Audio returned by the speech endpoint remains a candidate until it is
accepted.  Captions are generated from canonical source text and aligned to
accepted audio; ASR text is evidence, never publication copy.
"""

from __future__ import annotations

import argparse
import array
import contextlib
import dataclasses
import difflib
import hashlib
import http.client
import json
import math
import os
import re
import shutil
import ssl
import statistics
import subprocess
import sys
import textwrap
import time
import urllib.error
import urllib.request
import uuid
import wave
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Sequence


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG = ROOT / "audiobook" / "config.json"
DEFAULT_PRONUNCIATIONS = ROOT / "audiobook" / "pronunciations.tsv"
DEFAULT_BUILD = ROOT / "audiobook-build"
SPEECH_URL = "https://api.openai.com/v1/audio/speech"
TRANSCRIPTION_URL = "https://api.openai.com/v1/audio/transcriptions"
SSL_CONTEXT = ssl.create_default_context()

VERSE_RE = re.compile(r"^\s*(\d+)\s{2,}(.+?)\s*$")
NOTE_MARK_RE = re.compile(r"\[(\d+)\]")
WORD_RE = re.compile(r"[^\W\d_]+(?:[’'][^\W\d_]+)?|\d+", re.UNICODE)
SENTENCE_END_RE = re.compile(r"[.!?][^A-Za-z0-9]*$")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def relative_to_root(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def resolve_stored_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


@dataclasses.dataclass(frozen=True)
class Verse:
    number: int
    text: str
    section: int


@dataclasses.dataclass(frozen=True)
class Unit:
    verses: tuple[Verse, ...]
    paragraph: int = 0

    @property
    def text(self) -> str:
        return " ".join(v.text for v in self.verses)

    @property
    def line_start(self) -> int:
        return self.verses[0].number

    @property
    def line_end(self) -> int:
        return self.verses[-1].number

    @property
    def section(self) -> int:
        return self.verses[0].section


def parse_translation(path: Path) -> list[Unit]:
    """Extract numbered translation verses and join stanza-like paragraphs."""
    units: list[Unit] = []
    current: list[Verse] = []
    section = 0
    previous_number: int | None = None

    def flush() -> None:
        nonlocal current
        if current:
            units.append(Unit(tuple(current), paragraph=len(units)))
            current = []

    for raw in path.read_text(encoding="utf-8").splitlines():
        match = VERSE_RE.match(raw)
        if not match:
            if current and not raw.strip():
                flush()
            continue

        number = int(match.group(1))
        text = NOTE_MARK_RE.sub("", match.group(2)).strip()
        text = re.sub(r"\s+", " ", text)
        if previous_number is not None and number != previous_number + 1:
            flush()
            section += 1
        current.append(Verse(number, text, section))
        previous_number = number

    flush()
    if not units:
        raise SystemExit(f"No numbered translation lines found in {path}")
    return units


def in_ranges(number: int, ranges: Sequence[Sequence[int]]) -> bool:
    return any(start <= number <= end for start, end in ranges)


def select_ranges(units: Sequence[Unit], ranges: Sequence[Sequence[int]]) -> list[Unit]:
    """Select verses while ensuring gaps force chunk boundaries."""
    selected: list[Unit] = []
    last_number: int | None = None
    section_offset = 0
    for unit in units:
        verses = tuple(v for v in unit.verses if in_ranges(v.number, ranges))
        if not verses:
            continue
        if last_number is not None and verses[0].number != last_number + 1:
            section_offset += 1
        adjusted = tuple(
            Verse(v.number, v.text, v.section + section_offset) for v in verses
        )
        selected.append(Unit(adjusted, paragraph=unit.paragraph))
        last_number = verses[-1].number
    return selected


def ends_sentence(text: str) -> bool:
    return bool(SENTENCE_END_RE.search(text))


def split_at_sentence_boundaries(unit: Unit) -> list[Unit]:
    """Split a paragraph only after terminal punctuation at a verse ending."""
    pieces: list[Unit] = []
    current: list[Verse] = []
    for verse in unit.verses:
        current.append(verse)
        if ends_sentence(verse.text):
            pieces.append(Unit(tuple(current), paragraph=unit.paragraph))
            current = []
    if current:
        pieces.append(Unit(tuple(current), paragraph=unit.paragraph))
    return pieces


def split_oversized_unit(unit: Unit, max_chars: int) -> list[Unit]:
    if len(unit.text) <= max_chars:
        return [unit]
    pieces: list[Unit] = []
    current: list[Verse] = []
    for verse in unit.verses:
        candidate = " ".join(v.text for v in [*current, verse])
        if current and len(candidate) > max_chars:
            pieces.append(Unit(tuple(current), paragraph=unit.paragraph))
            current = [verse]
        else:
            current.append(verse)
    if current:
        pieces.append(Unit(tuple(current), paragraph=unit.paragraph))
    return pieces


def make_chunks(
    units: Sequence[Unit], target_chars: int, max_chars: int
) -> list[list[Unit]]:
    expanded: list[Unit] = []
    for unit in units:
        for sentence in split_at_sentence_boundaries(unit):
            expanded.extend(split_oversized_unit(sentence, max_chars))

    chunks: list[list[Unit]] = []
    current: list[Unit] = []
    current_chars = 0
    for unit in expanded:
        separator = 0
        if current:
            separator = 2 if unit.paragraph != current[-1].paragraph else 1
        would_be = current_chars + separator + len(unit.text)
        section_changed = bool(current and unit.section != current[-1].section)
        target_reached = current_chars >= target_chars
        if current and (section_changed or would_be > max_chars or target_reached):
            chunks.append(current)
            current = []
            current_chars = 0
            separator = 0
        current.append(unit)
        current_chars += separator + len(unit.text)
    if current:
        chunks.append(current)
    return chunks


def chunk_text(units: Sequence[Unit]) -> str:
    if not units:
        return ""
    rendered = units[0].text
    for previous, unit in zip(units, units[1:]):
        separator = "\n\n" if unit.paragraph != previous.paragraph else " "
        rendered += separator + unit.text
    return rendered.strip()


def load_pronunciations(path: Path) -> dict[str, dict[str, str]]:
    entries: dict[str, dict[str, str]] = {}
    if not path.exists():
        return entries
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        columns = line.split("\t")
        if len(columns) < 2:
            raise SystemExit(f"Malformed pronunciation row: {line!r}")
        headword, say = columns[0].strip(), columns[1].strip()
        status = columns[2].strip() if len(columns) > 2 else ""
        entries[headword] = {"say": say, "status": status}
    return entries


def pronunciations_for_text(
    text: str, entries: dict[str, dict[str, str]]
) -> dict[str, dict[str, str]]:
    found: dict[str, dict[str, str]] = {}
    for headword, item in entries.items():
        if re.search(rf"\b{re.escape(headword)}\b", text, re.IGNORECASE):
            found[headword] = item
    return found


def apply_tts_replacements(text: str, replacements: dict[str, str]) -> str:
    rendered = text
    for canonical in sorted(replacements, key=len, reverse=True):
        spoken = replacements[canonical]
        rendered = re.sub(
            rf"\b{re.escape(canonical)}\b",
            lambda _match, value=spoken: value,
            rendered,
            flags=re.IGNORECASE,
        )
    return rendered


def apply_candidate_text_replacement(
    text: str,
    replacement: Sequence[str] | None,
) -> tuple[str, dict[str, str] | None]:
    if not replacement:
        return text, None
    old, new = replacement
    occurrences = text.count(old)
    if occurrences != 1:
        raise SystemExit(
            "Candidate text replacement must match exactly once; "
            f"found {occurrences} occurrence(s) of {old!r}."
        )
    return text.replace(old, new, 1), {"old": old, "new": new}


def full_instructions(
    base: str,
    pronunciations: dict[str, dict[str, str]],
    extra: str | None = None,
) -> str:
    rendered_base = f"{base} {extra.strip()}".strip() if extra else base
    if not pronunciations:
        return rendered_base
    explicit = [
        item["instruction"].strip()
        for item in pronunciations.values()
        if item.get("instruction")
    ]
    respellings = "; ".join(
        f"{name}={item['say']}"
        for name, item in pronunciations.items()
        if item.get("say")
    )
    additions = [*explicit]
    if respellings:
        additions.append(
            f"Use these pronunciations consistently: {respellings}."
        )
    return f"{rendered_base} {' '.join(additions)}".strip()


def manifest_path(build_dir: Path) -> Path:
    return build_dir / "manifest.json"


def load_manifest(build_dir: Path) -> dict:
    path = manifest_path(build_dir)
    if not path.exists():
        raise SystemExit(f"Missing {path}. Run prepare first.")
    return read_json(path)


def next_candidate_id(chunk: dict) -> str:
    existing = [int(candidate["id"]) for candidate in chunk["candidates"]]
    floor = int(chunk.get("candidate_id_floor", 0))
    return f"{max([floor, *existing]) + 1:03d}"


def save_manifest(build_dir: Path, manifest: dict) -> None:
    manifest["updated_at"] = utc_now()
    write_json(manifest_path(build_dir), manifest)


def source_path_for_book(book: int) -> Path:
    return ROOT / "translation" / f"book_{book:02d}.txt"


def prepare(args: argparse.Namespace) -> None:
    config_path = Path(args.config)
    config = read_json(config_path)
    source = Path(args.source) if args.source else source_path_for_book(args.book)
    build_dir = Path(args.build_dir)
    chunks_dir = build_dir / "chunks"
    chunks_dir.mkdir(parents=True, exist_ok=True)
    for stale_path in chunks_dir.glob("chunk-*.txt"):
        stale_path.unlink()

    units = parse_translation(source)
    mode = "full" if args.full else "pilot"
    ranges = [] if args.full else config["pilot_ranges"]
    if ranges:
        units = select_ranges(units, ranges)

    chunks = make_chunks(
        units,
        target_chars=int(config["target_chars"]),
        max_chars=int(config["max_chars"]),
    )
    use_pronunciation_instructions = bool(
        config.get("use_pronunciation_instructions", True)
    )
    tts_replacements = config.get("tts_replacements", {})
    pronunciations = (
        load_pronunciations(Path(args.pronunciations))
        if use_pronunciation_instructions
        else {}
    )
    for headword, instruction in config.get(
        "pronunciation_notes", {}
    ).items():
        pronunciations[headword] = {
            "instruction": instruction,
            "status": "confirmed",
        }
    if pronunciations and tts_replacements:
        raise SystemExit(
            "Invalid pronunciation policy: use either pronunciation instructions "
            "or tts_replacements, never both."
        )
    chunk_items: list[dict] = []

    for index, chunk_units in enumerate(chunks, 1):
        text = chunk_text(chunk_units)
        tts_text = apply_tts_replacements(text, tts_replacements)
        selected_pron = pronunciations_for_text(text, pronunciations)
        chunk_id = f"{index:03d}"
        text_path = chunks_dir / f"chunk-{chunk_id}.txt"
        text_path.write_text(text + "\n", encoding="utf-8", newline="\n")
        chunk_items.append(
            {
                "id": chunk_id,
                "line_start": chunk_units[0].line_start,
                "line_end": chunk_units[-1].line_end,
                "canonical_text": text,
                "tts_text": tts_text,
                "canonical_sha256": sha256_text(text),
                "tts_sha256": sha256_text(tts_text),
                "characters": len(text),
                "words": len(normalize_words(text)),
                "ends_on_sentence_boundary": ends_sentence(
                    chunk_units[-1].verses[-1].text
                ),
                "text_path": relative_to_root(text_path),
                "pronunciations": selected_pron,
                "candidates": [],
                "accepted_candidate": None,
            }
        )

    source_bytes = source.read_bytes()
    manifest = {
        "schema_version": 1,
        "created_at": utc_now(),
        "updated_at": utc_now(),
        "mode": mode,
        "book": args.book,
        "source_path": relative_to_root(source),
        "source_sha256": sha256_bytes(source_bytes),
        "config_path": relative_to_root(config_path),
        "config_sha256": sha256_text(
            json.dumps(config, sort_keys=True, ensure_ascii=False)
        ),
        "pronunciations_path": relative_to_root(Path(args.pronunciations)),
        "model": config["model"],
        "voice": args.voice or config["voice"],
        "response_format": config["response_format"],
        "speed": config["speed"],
        "instructions": config["instructions"],
        "use_pronunciation_instructions": use_pronunciation_instructions,
        "pronunciation_notes": config.get("pronunciation_notes", {}),
        "tts_replacements": tts_replacements,
        "target_chars": config["target_chars"],
        "max_chars": config["max_chars"],
        "ranges": ranges,
        "chunks": chunk_items,
    }
    save_manifest(build_dir, manifest)
    print(
        f"Prepared Book {args.book} {mode}: {len(chunk_items)} chunks, "
        f"{sum(c['characters'] for c in chunk_items):,} characters, "
        f"lines {chunk_items[0]['line_start']}-{chunk_items[-1]['line_end']}."
    )
    for chunk in chunk_items:
        print(
            f"  {chunk['id']}: lines {chunk['line_start']}-{chunk['line_end']}, "
            f"{chunk['characters']} chars, sentence_end="
            f"{chunk['ends_on_sentence_boundary']}, "
            f"{len(chunk['pronunciations'])} pronunciations"
        )
    print(f"Manifest: {manifest_path(build_dir)}")


def require_api_key() -> str:
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        raise SystemExit("OPENAI_API_KEY is not set.")
    return key


def post_json(url: str, payload: dict, api_key: str, timeout: int) -> bytes:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(
        request, timeout=timeout, context=SSL_CONTEXT
    ) as response:
        return response.read()


def multipart_body(
    fields: Sequence[tuple[str, str]],
    file_field: str,
    file_path: Path,
) -> tuple[bytes, str]:
    boundary = f"----iliad-{uuid.uuid4().hex}"
    body = bytearray()
    for name, value in fields:
        body.extend(f"--{boundary}\r\n".encode())
        body.extend(
            f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode()
        )
        body.extend(value.encode("utf-8"))
        body.extend(b"\r\n")
    body.extend(f"--{boundary}\r\n".encode())
    body.extend(
        (
            f'Content-Disposition: form-data; name="{file_field}"; '
            f'filename="{file_path.name}"\r\n'
        ).encode()
    )
    body.extend(b"Content-Type: audio/wav\r\n\r\n")
    body.extend(file_path.read_bytes())
    body.extend(b"\r\n")
    body.extend(f"--{boundary}--\r\n".encode())
    return bytes(body), boundary


def post_multipart(
    url: str,
    fields: Sequence[tuple[str, str]],
    file_path: Path,
    api_key: str,
    timeout: int,
) -> bytes:
    body, boundary = multipart_body(fields, "file", file_path)
    request = urllib.request.Request(
        url,
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        },
        method="POST",
    )
    with urllib.request.urlopen(
        request, timeout=timeout, context=SSL_CONTEXT
    ) as response:
        return response.read()


def selected_chunks(manifest: dict, ids: Sequence[str] | None) -> list[dict]:
    if not ids:
        return manifest["chunks"]
    wanted = {value.zfill(3) for value in ids}
    selected = [chunk for chunk in manifest["chunks"] if chunk["id"] in wanted]
    missing = wanted - {chunk["id"] for chunk in selected}
    if missing:
        raise SystemExit(f"Unknown chunk ids: {', '.join(sorted(missing))}")
    return selected


def retry_call(operation, retries: int):
    for attempt in range(retries + 1):
        try:
            return operation()
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            retryable = exc.code in {408, 409, 429, 500, 502, 503, 504}
            if attempt < retries and retryable:
                wait = min(30, 2 ** (attempt + 1))
                print(f"HTTP {exc.code}; retrying in {wait}s.")
                time.sleep(wait)
                continue
            raise RuntimeError(f"HTTP {exc.code}: {body}") from exc
        except (
            urllib.error.URLError,
            TimeoutError,
            ConnectionError,
            http.client.RemoteDisconnected,
            ssl.SSLError,
        ) as exc:
            if attempt < retries:
                wait = min(30, 2 ** (attempt + 1))
                print(f"{type(exc).__name__}; retrying in {wait}s.")
                time.sleep(wait)
                continue
            raise
    raise AssertionError("retry loop exhausted")


def synthesize(args: argparse.Namespace) -> None:
    api_key = require_api_key()
    build_dir = Path(args.build_dir)
    manifest = load_manifest(build_dir)
    candidates_dir = build_dir / "candidates"
    generated = 0

    for chunk in selected_chunks(manifest, args.chunks):
        for _ in range(args.attempts):
            candidate_id = next_candidate_id(chunk)
            out_dir = candidates_dir / f"chunk-{chunk['id']}"
            out_dir.mkdir(parents=True, exist_ok=True)
            out_path = out_dir / f"candidate-{candidate_id}.wav"
            instructions = full_instructions(
                manifest["instructions"],
                chunk["pronunciations"],
                args.extra_instructions,
            )
            candidate_tts_text, text_replacement = apply_candidate_text_replacement(
                chunk["tts_text"],
                args.tts_text_replace,
            )
            payload = {
                "model": manifest["model"],
                "voice": manifest["voice"],
                "input": candidate_tts_text,
                "instructions": instructions,
                "response_format": manifest["response_format"],
                "speed": manifest["speed"],
            }
            print(
                f"Synthesizing chunk {chunk['id']} lines "
                f"{chunk['line_start']}-{chunk['line_end']}, candidate {candidate_id}..."
            )
            audio = retry_call(
                lambda: post_json(SPEECH_URL, payload, api_key, args.timeout),
                args.retries,
            )
            out_path.write_bytes(audio)
            features = analyze_wav(out_path, expected_words=chunk["words"])
            candidate = {
                "id": candidate_id,
                "path": relative_to_root(out_path),
                "created_at": utc_now(),
                "audio_sha256": sha256_bytes(audio),
                "model": manifest["model"],
                "voice": manifest["voice"],
                "instructions_sha256": sha256_text(instructions),
                "extra_instructions": args.extra_instructions,
                "tts_text_sha256": sha256_text(candidate_tts_text),
                "tts_text_replacement": text_replacement,
                "features": features,
                "qa": None,
                "status": "unreviewed",
                "acceptance": None,
            }
            chunk["candidates"].append(candidate)
            save_manifest(build_dir, manifest)
            generated += 1
    print(f"Generated {generated} candidate(s).")


def rebalance_boundary(args: argparse.Namespace) -> None:
    build_dir = Path(args.build_dir)
    manifest = load_manifest(build_dir)
    if (manifest.get("human_review") or {}).get("status") == "approved":
        raise SystemExit("Cannot rebalance a human-approved book.")

    left_index = next(
        (
            index
            for index, chunk in enumerate(manifest["chunks"])
            if chunk["id"] == args.left_chunk
        ),
        None,
    )
    if left_index is None or left_index + 1 >= len(manifest["chunks"]):
        raise SystemExit("Left chunk must exist and have an immediate right chunk.")
    left = manifest["chunks"][left_index]
    right = manifest["chunks"][left_index + 1]
    new_end = int(args.new_left_end)
    if not left["line_start"] <= new_end < right["line_end"]:
        raise SystemExit(
            f"New boundary must be within lines {left['line_start']}-"
            f"{right['line_end'] - 1}."
        )
    if new_end == left["line_end"]:
        raise SystemExit("New boundary is unchanged.")

    source = resolve_stored_path(manifest["source_path"])
    all_units = parse_translation(source)
    pronunciation_entries: dict[str, dict[str, str]] = {}
    if manifest.get("use_pronunciation_instructions"):
        pronunciation_entries.update(
            load_pronunciations(
                resolve_stored_path(manifest["pronunciations_path"])
            )
        )
    for headword, instruction in manifest.get("pronunciation_notes", {}).items():
        pronunciation_entries[headword] = {
            "instruction": instruction,
            "status": "confirmed",
        }

    archived_chunks = json.loads(json.dumps([left, right], ensure_ascii=False))
    manifest.setdefault("superseded_chunk_versions", []).append(
        {
            "superseded_at": utc_now(),
            "reason": args.reason,
            "chunks": archived_chunks,
        }
    )

    new_ranges = [
        (left["line_start"], new_end),
        (new_end + 1, right["line_end"]),
    ]
    for old_chunk, (line_start, line_end) in zip(
        (left, right), new_ranges
    ):
        selected = select_ranges(all_units, [[line_start, line_end]])
        text = chunk_text(selected)
        tts_text = apply_tts_replacements(
            text, manifest.get("tts_replacements", {})
        )
        candidate_floor = max(
            (int(candidate["id"]) for candidate in old_chunk["candidates"]),
            default=int(old_chunk.get("candidate_id_floor", 0)),
        )
        text_path = resolve_stored_path(old_chunk["text_path"])
        text_path.write_text(text + "\n", encoding="utf-8", newline="\n")
        old_chunk.update(
            {
                "line_start": line_start,
                "line_end": line_end,
                "canonical_text": text,
                "tts_text": tts_text,
                "canonical_sha256": sha256_text(text),
                "tts_sha256": sha256_text(tts_text),
                "characters": len(text),
                "words": len(normalize_words(text)),
                "ends_on_sentence_boundary": ends_sentence(
                    selected[-1].verses[-1].text
                ),
                "pronunciations": pronunciations_for_text(
                    text, pronunciation_entries
                ),
                "candidates": [],
                "candidate_id_floor": candidate_floor,
                "accepted_candidate": None,
            }
        )

    manifest.setdefault("boundary_adjustments", []).append(
        {
            "adjusted_at": utc_now(),
            "left_chunk": left["id"],
            "right_chunk": right["id"],
            "old_left_end": archived_chunks[0]["line_end"],
            "new_left_end": new_end,
            "reason": args.reason,
        }
    )
    save_manifest(build_dir, manifest)
    print(
        f"Rebalanced {left['id']}/{right['id']}: "
        f"{left['line_start']}-{left['line_end']} and "
        f"{right['line_start']}-{right['line_end']}."
    )


def normalize_word(value: str) -> str:
    normalized = value.lower().replace("’", "'")
    british_to_house = {
        "honour": "honor",
        "honoured": "honored",
        "honouring": "honoring",
        "dishonour": "dishonor",
        "dishonoured": "dishonored",
        "dishonouring": "dishonoring",
        "judgement": "judgment",
    }
    return british_to_house.get(normalized, normalized)


def normalize_words(text: str) -> list[str]:
    return [normalize_word(word) for word in WORD_RE.findall(text)]


def alignment_metrics(expected_text: str, observed_text: str) -> dict:
    expected = normalize_words(expected_text)
    observed = normalize_words(observed_text)
    matcher = difflib.SequenceMatcher(a=expected, b=observed, autojunk=False)
    deletions = insertions = substitutions = 0
    deletion_runs: list[int] = []
    differences: list[dict] = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue
        expected_part = expected[i1:i2]
        observed_part = observed[j1:j2]
        compound_adjustment: tuple[int, int, int] | None = None
        if tag == "replace" and abs(len(expected_part) - len(observed_part)) == 1:
            longer = expected_part if len(expected_part) > len(observed_part) else observed_part
            shorter = observed_part if len(expected_part) > len(observed_part) else expected_part
            for merge_at in range(len(longer) - 1):
                collapsed = [
                    *longer[:merge_at],
                    longer[merge_at] + longer[merge_at + 1],
                    *longer[merge_at + 2 :],
                ]
                if len(collapsed) == len(shorter):
                    mismatches = sum(
                        left != right for left, right in zip(collapsed, shorter)
                    )
                    if mismatches < len(shorter):
                        compound_adjustment = (mismatches, 0, 0)
                        break
        # ASR commonly joins or separates transparent compounds ("wine sack"
        # / "winesack"). That is orthography, not an audio omission.
        if (
            tag == "replace"
            and expected_part
            and observed_part
            and (
                "".join(expected_part) == "".join(observed_part)
                or (expected_part, observed_part)
                == (["all", "together"], ["altogether"])
            )
        ):
            continue
        if compound_adjustment is not None:
            substitutions += compound_adjustment[0]
            if len(differences) < 30:
                differences.append(
                    {
                        "type": tag,
                        "expected_index": i1,
                        "expected": " ".join(expected_part),
                        "observed": " ".join(observed_part),
                    }
                )
            continue
        if tag == "delete":
            deletions += i2 - i1
            deletion_runs.append(i2 - i1)
        elif tag == "insert":
            insertions += j2 - j1
        else:
            common = min(i2 - i1, j2 - j1)
            substitutions += common
            if i2 - i1 > common:
                missing = i2 - i1 - common
                deletions += missing
                deletion_runs.append(missing)
            if j2 - j1 > common:
                insertions += j2 - j1 - common
        if len(differences) < 30:
            differences.append(
                {
                    "type": tag,
                    "expected_index": i1,
                    "expected": " ".join(expected_part),
                    "observed": " ".join(observed_part),
                }
            )
    denominator = max(1, len(expected))
    return {
        "expected_words": len(expected),
        "observed_words": len(observed),
        "length_ratio": round(len(observed) / denominator, 5),
        "deletions": deletions,
        "deletion_ratio": round(deletions / denominator, 5),
        "max_deletion_run": max(deletion_runs, default=0),
        "insertions": insertions,
        "insertion_ratio": round(insertions / denominator, 5),
        "substitutions": substitutions,
        "substitution_ratio": round(substitutions / denominator, 5),
        "differences": differences,
    }


def suggest_status(metrics: dict, thresholds: dict) -> tuple[str, list[str]]:
    failures: list[str] = []
    reviews: list[str] = []
    if metrics["deletion_ratio"] > thresholds["max_deletion_ratio"]:
        failures.append("deletion ratio")
    if metrics["max_deletion_run"] > thresholds["max_deletion_run"]:
        failures.append("consecutive deletion")
    if metrics["length_ratio"] < thresholds["min_length_ratio"]:
        failures.append("short transcript")
    if metrics["length_ratio"] > thresholds["max_length_ratio"]:
        failures.append("long transcript")
    if metrics["substitution_ratio"] > thresholds["max_substitution_ratio"]:
        reviews.append("substitution ratio")
    if metrics["deletions"]:
        reviews.append("one or more deletions")
    if metrics["insertions"]:
        reviews.append("one or more insertions")
    if failures:
        return "fail", failures + reviews
    if reviews:
        return "review", reviews
    return "pass", []


def analyze_wav(path: Path, expected_words: int) -> dict:
    with contextlib.closing(wave.open(str(path), "rb")) as handle:
        channels = handle.getnchannels()
        width = handle.getsampwidth()
        rate = handle.getframerate()
        frames = handle.getnframes()
        if width != 2:
            raise RuntimeError(f"Expected 16-bit WAV, got sample width {width}: {path}")
        raw = handle.readframes(frames)
    samples = array.array("h")
    samples.frombytes(raw)
    if sys.byteorder != "little":
        samples.byteswap()
    if channels > 1:
        samples = array.array("h", samples[::channels])
    # Streaming WAV responses may use 0xFFFFFFFF as a placeholder data length.
    # The wave module exposes that placeholder as nframes, so derive duration
    # from the samples actually read instead of trusting the header count.
    duration = len(samples) / rate if rate else 0.0
    if not samples:
        rms = peak = 0.0
    else:
        rms = math.sqrt(sum(sample * sample for sample in samples) / len(samples))
        peak = max(abs(sample) for sample in samples)
    rms_dbfs = 20 * math.log10(rms / 32768) if rms else -120.0
    peak_dbfs = 20 * math.log10(peak / 32768) if peak else -120.0

    window = max(1, int(rate * 0.02))
    silent = total = 0
    silence_threshold = 32768 * (10 ** (-45 / 20))
    for start in range(0, len(samples), window):
        part = samples[start : start + window]
        if not part:
            continue
        part_rms = math.sqrt(sum(v * v for v in part) / len(part))
        silent += int(part_rms < silence_threshold)
        total += 1
    return {
        "duration_seconds": round(duration, 3),
        "sample_rate": rate,
        "channels": channels,
        "rms_dbfs": round(rms_dbfs, 3),
        "peak_dbfs": round(peak_dbfs, 3),
        "silence_ratio": round(silent / total, 5) if total else 0.0,
        "speaking_rate_wpm": round(expected_words / duration * 60, 2)
        if duration
        else 0.0,
    }


def candidate_by_id(chunk: dict, candidate_id: str) -> dict:
    candidate_id = candidate_id.zfill(3)
    for candidate in chunk["candidates"]:
        if candidate["id"] == candidate_id:
            return candidate
    raise SystemExit(f"Chunk {chunk['id']} has no candidate {candidate_id}.")


def transcribe_quality(path: Path, api_key: str, timeout: int, retries: int) -> str:
    fields = [
        ("model", "gpt-4o-transcribe"),
        ("response_format", "json"),
        ("language", "en"),
    ]
    response = retry_call(
        lambda: post_multipart(
            TRANSCRIPTION_URL, fields, path, api_key, timeout
        ),
        retries,
    )
    payload = json.loads(response.decode("utf-8"))
    return payload["text"]


def qa(args: argparse.Namespace) -> None:
    api_key = require_api_key()
    build_dir = Path(args.build_dir)
    manifest = load_manifest(build_dir)
    config = read_json(resolve_stored_path(manifest["config_path"]))
    qa_dir = build_dir / "qa"
    checked = 0

    for chunk in selected_chunks(manifest, args.chunks):
        candidates = chunk["candidates"]
        if args.candidate:
            candidates = [candidate_by_id(chunk, args.candidate)]
        for candidate in candidates:
            if candidate.get("qa") and not args.force:
                continue
            audio_path = resolve_stored_path(candidate["path"])
            candidate["features"] = analyze_wav(
                audio_path, expected_words=chunk["words"]
            )
            if (
                args.recalculate
                and candidate.get("qa")
                and candidate["qa"].get("transcript_path")
            ):
                transcript = resolve_stored_path(
                    candidate["qa"]["transcript_path"]
                ).read_text(encoding="utf-8")
                print(
                    f"Recalculating chunk {chunk['id']} candidate "
                    f"{candidate['id']} from saved transcript..."
                )
            else:
                print(
                    f"Transcribing chunk {chunk['id']} candidate "
                    f"{candidate['id']}..."
                )
                transcript = transcribe_quality(
                    audio_path, api_key, args.timeout, args.retries
                )
            # High-quality ASR normally restores canonical spellings from
            # phonetic TTS request text ("Cry-seez" -> "Chryses"). Fidelity
            # therefore compares against publication text; pronunciation is a
            # separate human listening gate.
            metrics = alignment_metrics(chunk["canonical_text"], transcript)
            status, reasons = suggest_status(metrics, config["qa"])
            transcript_path = (
                qa_dir
                / f"chunk-{chunk['id']}"
                / f"candidate-{candidate['id']}-transcript.txt"
            )
            report_path = transcript_path.with_name(
                f"candidate-{candidate['id']}-report.json"
            )
            transcript_path.parent.mkdir(parents=True, exist_ok=True)
            transcript_path.write_text(
                transcript.strip() + "\n", encoding="utf-8", newline="\n"
            )
            report = {
                "created_at": utc_now(),
                "transcription_model": "gpt-4o-transcribe",
                "transcript_path": relative_to_root(transcript_path),
                "metrics": metrics,
                "suggested_status": status,
                "reasons": reasons,
            }
            write_json(report_path, report)
            candidate["qa"] = {
                **report,
                "report_path": relative_to_root(report_path),
            }
            candidate["status"] = status
            checked += 1
            print(
                f"  {status.upper()}: deletions={metrics['deletions']} "
                f"(max run {metrics['max_deletion_run']}), "
                f"substitutions={metrics['substitutions']}, "
                f"length={metrics['length_ratio']:.3f}"
            )
            save_manifest(build_dir, manifest)
    print(f"Quality-checked {checked} candidate(s).")


def report(args: argparse.Namespace) -> None:
    manifest = load_manifest(Path(args.build_dir))
    print(
        f"Iliad Book {manifest['book']} ({manifest['mode']}), "
        f"{manifest['model']} / {manifest['voice']}"
    )
    print(
        "chunk  lines       cand  status      duration   wpm    deletions  max-run  accepted"
    )
    features_for_medians: list[dict] = []
    for chunk in manifest["chunks"]:
        for candidate in chunk["candidates"]:
            features_for_medians.append(candidate["features"])
            qa_payload = candidate.get("qa") or {}
            metrics = qa_payload.get("metrics") or {}
            accepted = "*" if chunk["accepted_candidate"] == candidate["id"] else ""
            print(
                f"{chunk['id']:>5}  {chunk['line_start']:>3}-{chunk['line_end']:<3}  "
                f"{candidate['id']:>7}  {candidate['status']:<10} "
                f"{candidate['features']['duration_seconds']:>7.1f}s "
                f"{candidate['features']['speaking_rate_wpm']:>6.1f} "
                f"{str(metrics.get('deletions', '-')):>10} "
                f"{str(metrics.get('max_deletion_run', '-')):>8}  {accepted}"
            )
    if features_for_medians:
        print("\nAcoustic proxies across all candidates:")
        for key in ("speaking_rate_wpm", "rms_dbfs", "silence_ratio"):
            values = [float(item[key]) for item in features_for_medians]
            print(
                f"  {key}: median {statistics.median(values):.3f}, "
                f"range {min(values):.3f}–{max(values):.3f}"
            )
        print(
            "  These catch pacing/loudness outliers, not narrator identity; "
            "listen at every candidate boundary."
        )


def accept(args: argparse.Namespace) -> None:
    build_dir = Path(args.build_dir)
    manifest = load_manifest(build_dir)
    changed = 0
    if args.auto:
        for chunk in selected_chunks(manifest, args.chunks):
            passing = [
                c for c in chunk["candidates"] if c.get("status") == "pass"
            ]
            if len(passing) == 1:
                candidate = passing[0]
                chunk["accepted_candidate"] = candidate["id"]
                candidate["acceptance"] = {
                    "accepted_at": utc_now(),
                    "method": "automatic-pass",
                    "reason": "Only candidate with strict QA pass.",
                }
                changed += 1
    else:
        if not args.chunk or not args.candidate:
            raise SystemExit("Manual acceptance requires --chunk and --candidate.")
        chunks = selected_chunks(manifest, [args.chunk])
        chunk = chunks[0]
        candidate = candidate_by_id(chunk, args.candidate)
        if candidate["status"] != "pass" and not args.reason:
            raise SystemExit(
                "A non-passing candidate requires --reason for the audit trail."
            )
        chunk["accepted_candidate"] = candidate["id"]
        candidate["acceptance"] = {
            "accepted_at": utc_now(),
            "method": "manual",
            "reason": args.reason or "Reviewed and accepted.",
        }
        changed = 1
    save_manifest(build_dir, manifest)
    print(f"Accepted {changed} candidate(s).")


def accepted_pairs(manifest: dict) -> list[tuple[dict, dict]]:
    pairs: list[tuple[dict, dict]] = []
    missing: list[str] = []
    for chunk in manifest["chunks"]:
        candidate_id = chunk.get("accepted_candidate")
        if not candidate_id:
            missing.append(chunk["id"])
            continue
        pairs.append((chunk, candidate_by_id(chunk, candidate_id)))
    if missing:
        raise SystemExit(
            "Every chunk must be accepted first. Missing: " + ", ".join(missing)
        )
    return pairs


def unaudited_approval_exceptions(
    pairs: Sequence[tuple[dict, dict]],
) -> list[str]:
    unaudited: list[str] = []
    for chunk, candidate in pairs:
        if candidate.get("status") == "pass":
            continue
        acceptance = candidate.get("acceptance") or {}
        reason = str(acceptance.get("reason") or "").strip()
        if acceptance.get("method") != "manual" or not reason:
            unaudited.append(f"{chunk['id']}/{candidate['id']}")
    return unaudited


def approve_book(args: argparse.Namespace) -> None:
    build_dir = Path(args.build_dir)
    manifest = load_manifest(build_dir)
    pairs = accepted_pairs(manifest)
    unaudited = unaudited_approval_exceptions(pairs)
    if unaudited:
        raise SystemExit(
            "Human approval requires each selected candidate to be either a "
            "strict pass or manually accepted with an audit reason. "
            "Unaudited: " + ", ".join(unaudited)
        )
    qa_exceptions = [
        {
            "chunk": chunk["id"],
            "candidate": candidate["id"],
            "qa_status": candidate.get("status"),
            "acceptance_reason": candidate["acceptance"]["reason"],
        }
        for chunk, candidate in pairs
        if candidate.get("status") != "pass"
    ]
    manifest["human_review"] = {
        "status": "approved",
        "approved_at": utc_now(),
        "reviewer": "user",
        "notes": args.notes,
        "qa_exceptions": qa_exceptions,
    }
    save_manifest(build_dir, manifest)
    print(
        f"Recorded human approval for Book {manifest['book']} "
        f"across {len(pairs)} selected chunks."
    )


def write_concat_list(
    manifest: dict,
    pairs: Sequence[tuple[dict, dict]],
    output_dir: Path,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    list_path = output_dir / f"book-{manifest['book']:02d}-concat.txt"
    lines = []
    for _, candidate in pairs:
        path = resolve_stored_path(candidate["path"]).resolve().as_posix()
        lines.append(f"file '{path.replace(chr(39), chr(39) + chr(92) + chr(39) + chr(39))}'")
    list_path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return list_path


def concat(args: argparse.Namespace) -> None:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise SystemExit("ffmpeg is required.")
    build_dir = Path(args.build_dir)
    manifest = load_manifest(build_dir)
    pairs = accepted_pairs(manifest)
    output_dir = build_dir / "books"
    list_path = write_concat_list(manifest, pairs, output_dir)
    out_path = output_dir / f"book-{manifest['book']:02d}-{manifest['mode']}.wav"
    command = [
        ffmpeg,
        "-y" if args.force else "-n",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(list_path),
        "-c",
        "copy",
        str(out_path),
    ]
    result = subprocess.run(
        command, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    if result.returncode:
        print(result.stdout)
        raise SystemExit(result.returncode)
    print(f"Wrote {out_path}")


def review_master(args: argparse.Namespace) -> None:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise SystemExit("ffmpeg is required.")
    build_dir = Path(args.build_dir)
    manifest = load_manifest(build_dir)
    pairs = accepted_pairs(manifest)
    output_dir = build_dir / "books"
    list_path = write_concat_list(manifest, pairs, output_dir)
    out_path = output_dir / f"book-{manifest['book']:02d}-review.m4a"
    command = [
        ffmpeg,
        "-y" if args.force else "-n",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(list_path),
        "-vn",
        "-c:a",
        "aac",
        "-b:a",
        args.bitrate,
        "-movflags",
        "+faststart",
        str(out_path),
    ]
    result = subprocess.run(
        command, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    if result.returncode:
        print(result.stdout)
        raise SystemExit(result.returncode)
    manifest["review_master"] = {
        "path": relative_to_root(out_path),
        "created_at": utc_now(),
        "format": "m4a/aac",
        "bitrate": args.bitrate,
        "sha256": sha256_bytes(out_path.read_bytes()),
    }
    save_manifest(build_dir, manifest)
    print(f"Wrote {out_path}")


def transcribe_timestamps(
    path: Path, api_key: str, timeout: int, retries: int
) -> dict:
    fields = [
        ("model", "whisper-1"),
        ("response_format", "verbose_json"),
        ("language", "en"),
        ("timestamp_granularities[]", "word"),
    ]
    response = retry_call(
        lambda: post_multipart(
            TRANSCRIPTION_URL, fields, path, api_key, timeout
        ),
        retries,
    )
    return json.loads(response.decode("utf-8"))


def map_expected_times(
    expected_text: str, timed_words: Sequence[dict], duration: float
) -> list[tuple[float, float]]:
    expected = normalize_words(expected_text)
    observed: list[str] = []
    observed_times: list[tuple[float, float]] = []
    for item in timed_words:
        tokens = normalize_words(item.get("word", ""))
        if not tokens:
            continue
        for token in tokens:
            observed.append(token)
            observed_times.append((float(item["start"]), float(item["end"])))

    mapping: dict[int, tuple[float, float]] = {}
    matcher = difflib.SequenceMatcher(a=expected, b=observed, autojunk=False)
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag != "equal":
            continue
        for offset in range(i2 - i1):
            mapping[i1 + offset] = observed_times[j1 + offset]

    result: list[tuple[float, float]] = []
    for index in range(len(expected)):
        if index in mapping:
            result.append(mapping[index])
            continue
        previous = next((mapping[i] for i in range(index - 1, -1, -1) if i in mapping), None)
        following = next(
            (mapping[i] for i in range(index + 1, len(expected)) if i in mapping),
            None,
        )
        start = previous[1] if previous else 0.0
        end = following[0] if following else duration
        if end < start:
            end = start + 0.12
        result.append((start, end))
    return result


def caption_units(text: str, max_chars: int = 84) -> list[tuple[str, int, int]]:
    """Return caption text plus normalized word-index bounds."""
    words = list(WORD_RE.finditer(text))
    if not words:
        return []
    units: list[tuple[str, int, int]] = []
    start_word = 0
    start_char = words[0].start()
    for index, match in enumerate(words):
        char_end = match.end()
        segment = text[start_char:char_end].strip()
        punctuation_break = bool(re.search(r"[.!?;:]$", segment))
        if index + 1 == len(words) or (
            len(segment) >= max_chars and (punctuation_break or len(segment) >= max_chars + 24)
        ):
            if index + 1 < len(words):
                char_end = words[index + 1].start()
            else:
                char_end = len(text)
            rendered = re.sub(r"\s+", " ", text[start_char:char_end].strip())
            units.append((rendered, start_word, index))
            start_word = index + 1
            if start_word < len(words):
                start_char = words[start_word].start()
    return units


def srt_time(seconds: float) -> str:
    milliseconds = max(0, round(seconds * 1000))
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    secs, millis = divmod(remainder, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def ass_time(seconds: float) -> str:
    centiseconds = max(0, round(seconds * 100))
    hours, remainder = divmod(centiseconds, 360_000)
    minutes, remainder = divmod(remainder, 6_000)
    secs, centis = divmod(remainder, 100)
    return f"{hours}:{minutes:02d}:{secs:02d}.{centis:02d}"


def roman_numeral(number: int) -> str:
    values = (
        (10, "X"),
        (9, "IX"),
        (5, "V"),
        (4, "IV"),
        (1, "I"),
    )
    rendered: list[str] = []
    remainder = number
    for value, numeral in values:
        while remainder >= value:
            rendered.append(numeral)
            remainder -= value
    return "".join(rendered)


def remove_caption_overlaps(
    cues: Sequence[tuple[float, float, str]]
) -> list[tuple[float, float, str]]:
    adjusted: list[tuple[float, float, str]] = []
    for start, end, text in cues:
        if adjusted and start < adjusted[-1][1]:
            previous_start, _, previous_text = adjusted[-1]
            previous_end = max(previous_start + 0.25, start - 0.03)
            adjusted[-1] = (previous_start, previous_end, previous_text)
        adjusted.append((start, max(start + 0.25, end), text))
    return adjusted


def captions(args: argparse.Namespace) -> None:
    api_key = require_api_key()
    build_dir = Path(args.build_dir)
    manifest = load_manifest(build_dir)
    pairs = accepted_pairs(manifest)
    timestamp_dir = build_dir / "timestamps"
    caption_dir = build_dir / "captions"
    caption_dir.mkdir(parents=True, exist_ok=True)
    cues: list[tuple[float, float, str]] = []
    offset = 0.0

    for chunk, candidate in pairs:
        audio_path = resolve_stored_path(candidate["path"])
        timestamp_path = (
            timestamp_dir
            / f"chunk-{chunk['id']}-candidate-{candidate['id']}.json"
        )
        if timestamp_path.exists() and not args.force:
            payload = read_json(timestamp_path)
        else:
            print(
                f"Timestamping chunk {chunk['id']} candidate {candidate['id']}..."
            )
            payload = transcribe_timestamps(
                audio_path, api_key, args.timeout, args.retries
            )
            write_json(timestamp_path, payload)
        duration = float(
            payload.get("duration")
            or candidate["features"]["duration_seconds"]
        )
        times = map_expected_times(
            chunk["canonical_text"], payload.get("words", []), duration
        )
        for text, first, last in caption_units(chunk["canonical_text"]):
            if first >= len(times):
                continue
            start = max(0.0, times[first][0] - 0.08) + offset
            end = min(duration, times[min(last, len(times) - 1)][1] + 0.15) + offset
            if end <= start:
                end = start + 0.8
            cues.append((start, end, text))
        offset += duration

    cues = remove_caption_overlaps(cues)
    out_path = caption_dir / f"book-{manifest['book']:02d}-{manifest['mode']}.srt"
    rendered: list[str] = []
    for index, (start, end, text) in enumerate(cues, 1):
        wrapped = "\n".join(
            textwrap.wrap(
                text,
                width=58,
                break_long_words=False,
                break_on_hyphens=False,
            )
        )
        rendered.extend(
            [str(index), f"{srt_time(start)} --> {srt_time(end)}", wrapped, ""]
        )
    out_path.write_text("\n".join(rendered), encoding="utf-8", newline="\n")
    print(f"Wrote {out_path} with {len(cues)} canonical-text cues.")

    ass_path = caption_dir / f"book-{manifest['book']:02d}-{manifest['mode']}.ass"
    roman = roman_numeral(int(manifest["book"]))
    ass_lines = [
        "[Script Info]",
        f"Title: ILIAD — BOOK {roman} — Living Manuscript Edition",
        "ScriptType: v4.00+",
        "PlayResX: 1920",
        "PlayResY: 1080",
        "WrapStyle: 0",
        "ScaledBorderAndShadow: yes",
        "YCbCr Matrix: TV.709",
        "",
        "[V4+ Styles]",
        (
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, "
            "OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, "
            "ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, "
            "Alignment, MarginL, MarginR, MarginV, Encoding"
        ),
        (
            "Style: Header,Georgia,23,&H005594B8,&H005594B8,&H80130D08,"
            "&H00000000,0,0,0,0,100,100,3,0,1,1.5,0,8,80,80,54,1"
        ),
        (
            "Style: Narration,Georgia,49,&H00D8E7EE,&H00D8E7EE,&HE0130D08,"
            "&H70000000,0,0,0,0,100,100,0.4,0,1,3,1,2,170,170,185,1"
        ),
        "",
        "[Events]",
        (
            "Format: Layer, Start, End, Style, Name, MarginL, MarginR, "
            "MarginV, Effect, Text"
        ),
        (
            f"Dialogue: 0,{ass_time(0)},{ass_time(offset)},Header,,0,0,0,,"
            f"{{\\fad(800,500)}}HOMER’S ILIAD  ·  BOOK {roman}"
        ),
    ]
    for start, end, text in cues:
        wrapped = r"\N".join(
            textwrap.wrap(
                text,
                width=58,
                break_long_words=False,
                break_on_hyphens=False,
            )
        )
        wrapped = wrapped.replace("{", r"\{").replace("}", r"\}")
        ass_lines.append(
            f"Dialogue: 1,{ass_time(start)},{ass_time(end)},Narration,,0,0,0,,"
            f"{{\\fad(60,120)}}{wrapped}"
        )
    ass_path.write_text(
        "\n".join(ass_lines) + "\n", encoding="utf-8", newline="\n"
    )
    print(f"Wrote {ass_path} with Odyssey-matched living-manuscript styles.")


def video(args: argparse.Namespace) -> None:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise SystemExit("ffmpeg is required.")
    build_dir = Path(args.build_dir)
    manifest = load_manifest(build_dir)
    wav_path = (
        build_dir
        / "books"
        / f"book-{manifest['book']:02d}-{manifest['mode']}.wav"
    )
    srt_path = (
        build_dir
        / "captions"
        / f"book-{manifest['book']:02d}-{manifest['mode']}.srt"
    )
    ass_path = srt_path.with_suffix(".ass")
    caption_path = ass_path if ass_path.exists() else srt_path
    if not caption_path.exists():
        raise SystemExit("Run captions before video.")

    if wav_path.exists():
        audio_input = ["-i", str(wav_path)]
    else:
        pairs = accepted_pairs(manifest)
        list_path = write_concat_list(manifest, pairs, build_dir / "books")
        audio_input = [
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(list_path),
        ]

    video_dir = build_dir / "videos"
    video_dir.mkdir(parents=True, exist_ok=True)
    out_path = video_dir / f"iliad-book-{manifest['book']:02d}-{manifest['mode']}.mp4"
    escaped_caption = (
        caption_path.resolve()
        .as_posix()
        .replace("\\", "\\\\")
        .replace(":", "\\:")
        .replace("'", "\\'")
    )
    if caption_path.suffix.lower() == ".ass":
        subtitle_filter = f"subtitles=filename='{escaped_caption}'"
    else:
        subtitle_filter = (
            f"subtitles=filename='{escaped_caption}':"
            "force_style='FontName=Georgia,FontSize=17,"
            "PrimaryColour=&H00F3E8D3,OutlineColour=&H00130B10,"
            "BorderStyle=1,Outline=1,Shadow=0.5,Alignment=2,MarginV=54'"
        )

    if args.background:
        background = Path(args.background)
        if not background.exists():
            raise SystemExit(f"Background image not found: {background}")
        command = [
            ffmpeg,
            "-y" if args.force else "-n",
            "-loop",
            "1",
            "-framerate",
            "24",
            "-i",
            str(background),
            *audio_input,
            "-vf",
            (
                f"scale={args.width}:{args.height}:"
                "force_original_aspect_ratio=decrease,"
                f"pad={args.width}:{args.height}:"
                "(ow-iw)/2:(oh-ih)/2:color=0x1b1015,"
                "vignette=PI/5,"
                f"{subtitle_filter}"
            ),
        ]
    else:
        command = [
            ffmpeg,
            "-y" if args.force else "-n",
            "-f",
            "lavfi",
            "-i",
            f"color=c=0x1b1015:s={args.width}x{args.height}:r=30",
            *audio_input,
            "-vf",
            subtitle_filter,
        ]
    command.extend(
        [
            "-c:v",
            "libx264",
            "-preset",
            args.preset,
            "-crf",
            str(args.crf),
            "-tune",
            "stillimage",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-pix_fmt",
            "yuv420p",
            "-r",
            "24",
            "-shortest",
            "-movflags",
            "+faststart",
            str(out_path),
        ]
    )
    result = subprocess.run(
        command, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    if result.returncode:
        print(result.stdout)
        raise SystemExit(result.returncode)
    print(f"Wrote {out_path}")


def verify(args: argparse.Namespace) -> None:
    build_dir = Path(args.build_dir)
    manifest = load_manifest(build_dir)
    errors: list[str] = []
    source = resolve_stored_path(manifest["source_path"])
    if sha256_bytes(source.read_bytes()) != manifest["source_sha256"]:
        errors.append("source translation changed since prepare")
    config = resolve_stored_path(manifest["config_path"])
    current_config_hash = sha256_text(
        json.dumps(read_json(config), sort_keys=True, ensure_ascii=False)
    )
    if current_config_hash != manifest["config_sha256"]:
        errors.append("configuration changed since prepare")
    for chunk in manifest["chunks"]:
        if sha256_text(chunk["canonical_text"]) != chunk["canonical_sha256"]:
            errors.append(f"chunk {chunk['id']} canonical text hash mismatch")
        for candidate in chunk["candidates"]:
            path = resolve_stored_path(candidate["path"])
            if not path.exists():
                errors.append(f"missing candidate file {candidate['path']}")
            elif sha256_bytes(path.read_bytes()) != candidate["audio_sha256"]:
                errors.append(f"candidate hash mismatch {candidate['path']}")
    if errors:
        print("Verification failed:")
        for error in errors:
            print(f"  - {error}")
        raise SystemExit(1)
    print(
        f"Verified source/config hashes and {sum(len(c['candidates']) for c in manifest['chunks'])} candidate file(s)."
    )


def add_common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--build-dir", default=str(DEFAULT_BUILD))


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    prepare_parser = subparsers.add_parser("prepare")
    add_common(prepare_parser)
    prepare_parser.add_argument("--book", type=int, default=1)
    prepare_parser.add_argument("--source")
    prepare_parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    prepare_parser.add_argument(
        "--voice",
        help="Override the config voice while preserving all other settings.",
    )
    prepare_parser.add_argument(
        "--pronunciations", default=str(DEFAULT_PRONUNCIATIONS)
    )
    prepare_parser.add_argument("--full", action="store_true")

    synth_parser = subparsers.add_parser("synthesize")
    add_common(synth_parser)
    synth_parser.add_argument("--chunks", nargs="*")
    synth_parser.add_argument("--attempts", type=int, default=1)
    synth_parser.add_argument("--extra-instructions")
    synth_parser.add_argument(
        "--tts-text-replace",
        nargs=2,
        metavar=("OLD", "NEW"),
        help=(
            "Apply one exact, candidate-specific text replacement while "
            "preserving the canonical source and recording the override."
        ),
    )
    synth_parser.add_argument("--timeout", type=int, default=180)
    synth_parser.add_argument("--retries", type=int, default=3)

    rebalance_parser = subparsers.add_parser("rebalance-boundary")
    add_common(rebalance_parser)
    rebalance_parser.add_argument("--left-chunk", required=True)
    rebalance_parser.add_argument("--new-left-end", type=int, required=True)
    rebalance_parser.add_argument("--reason", required=True)

    qa_parser = subparsers.add_parser("qa")
    add_common(qa_parser)
    qa_parser.add_argument("--chunks", nargs="*")
    qa_parser.add_argument("--candidate")
    qa_parser.add_argument("--force", action="store_true")
    qa_parser.add_argument(
        "--recalculate",
        action="store_true",
        help="Recompute QA from saved transcripts without another API call.",
    )
    qa_parser.add_argument("--timeout", type=int, default=180)
    qa_parser.add_argument("--retries", type=int, default=3)

    report_parser = subparsers.add_parser("report")
    add_common(report_parser)

    accept_parser = subparsers.add_parser("accept")
    add_common(accept_parser)
    accept_parser.add_argument("--auto", action="store_true")
    accept_parser.add_argument("--chunks", nargs="*")
    accept_parser.add_argument("--chunk")
    accept_parser.add_argument("--candidate")
    accept_parser.add_argument("--reason")

    approve_book_parser = subparsers.add_parser("approve-book")
    add_common(approve_book_parser)
    approve_book_parser.add_argument(
        "--notes",
        default="Listened to the complete review master and approved.",
    )

    concat_parser = subparsers.add_parser("concat")
    add_common(concat_parser)
    concat_parser.add_argument("--force", action="store_true")

    review_parser = subparsers.add_parser("review")
    add_common(review_parser)
    review_parser.add_argument("--bitrate", default="128k")
    review_parser.add_argument("--force", action="store_true")

    captions_parser = subparsers.add_parser("captions")
    add_common(captions_parser)
    captions_parser.add_argument("--force", action="store_true")
    captions_parser.add_argument("--timeout", type=int, default=180)
    captions_parser.add_argument("--retries", type=int, default=3)

    video_parser = subparsers.add_parser("video")
    add_common(video_parser)
    video_parser.add_argument("--background")
    video_parser.add_argument("--width", type=int, default=1920)
    video_parser.add_argument("--height", type=int, default=1080)
    video_parser.add_argument("--preset", default="medium")
    video_parser.add_argument("--crf", type=int, default=20)
    video_parser.add_argument("--force", action="store_true")

    verify_parser = subparsers.add_parser("verify")
    add_common(verify_parser)

    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    commands = {
        "prepare": prepare,
        "synthesize": synthesize,
        "rebalance-boundary": rebalance_boundary,
        "qa": qa,
        "report": report,
        "accept": accept,
        "approve-book": approve_book,
        "concat": concat,
        "review": review_master,
        "captions": captions,
        "video": video,
        "verify": verify,
    }
    commands[args.command](args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
