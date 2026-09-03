# Iliad audiobook pilot

The audiobook pipeline treats every TTS response as a candidate take. No
candidate is concatenated until textual-fidelity QA has run and the candidate
has been accepted.

The source of truth remains `translation/book_01.txt`. The preparation stage
copies canonical narration text into generated build artifacts; it never
edits the translation.

## Fixed production configuration

`audiobook/config.json` pins:

- model snapshot `gpt-4o-mini-tts-2025-12-15`;
- built-in voice `fable`;
- lossless WAV candidate output;
- a verbatim-fidelity and stable-narrator instruction;
- target/max chunk sizes of 1,400/1,800 characters;
- the representative Book 1 line ranges used by the pilot.

`audiobook/pronunciations.tsv` is the house pronunciation registry. Only
entries actually present in a chunk are added to that chunk's instruction.
Rows marked `review` should be auditioned and settled before full production.

## Pilot sequence

The environment must contain `OPENAI_API_KEY`. The key is read only at request
time and is never written to the manifest.

```powershell
python tools\build_audiobook.py prepare
python tools\build_audiobook.py synthesize
python tools\build_audiobook.py qa
python tools\build_audiobook.py report
```

`qa` transcribes each candidate with `gpt-4o-transcribe` without supplying the
expected passage as a prompt. It then aligns that independent transcript
against the exact TTS input. This reduces the risk that a source-aware
transcriber will silently fill in omitted words.

Candidates receive one of three suggested states:

- `pass`: no detected insertions or deletions and substitution rate within the
  configured bound;
- `review`: likely ASR spelling differences or isolated word discrepancies;
- `fail`: a deletion run, transcript length, or deletion rate exceeds the
  configured bound.

The rating is screening evidence, not a substitute for listening.

Generate another take for selected chunks with:

```powershell
python tools\build_audiobook.py synthesize --chunks 003 005 --attempts 1
python tools\build_audiobook.py qa --chunks 003 005
python tools\build_audiobook.py report
```

If the same request-final clause is omitted twice, identify that exact sentence
as passage text in a candidate-specific instruction:

```powershell
python tools\build_audiobook.py synthesize --chunks 004 `
  --extra-instructions "The final quoted sentence, Hold back and obey us, is part of the passage and must be spoken in full."
```

The extra instruction is recorded with the candidate. The two failed takes
remain in the manifest rather than being overwritten.

Accept the sole strict-pass candidate for each chunk:

```powershell
python tools\build_audiobook.py accept --auto
```

Manually accepting a `review` or `fail` candidate requires an audit reason:

```powershell
python tools\build_audiobook.py accept --chunk 003 --candidate 002 `
  --reason "Listened against the canonical text; ASR only misspelled Briseis."
```

When every chunk is accepted:

```powershell
python tools\build_audiobook.py verify
python tools\build_audiobook.py concat
python tools\build_audiobook.py captions
python tools\build_audiobook.py video
```

`captions` asks `whisper-1` for word timestamps, aligns those timestamps to the
canonical source, and writes an SRT containing the canonical Iliad text—not
the ASR transcript.

Without `--background`, `video` renders a restrained wine-black background
with embedded canonical captions. Supply a final still image with:

```powershell
python tools\build_audiobook.py video --background art\iliad-book-01.jpg --force
```

## Full Book 1

After the pilot settings and pronunciations are approved:

```powershell
python tools\build_audiobook.py prepare --full `
  --build-dir audiobook-build-book01
```

Use the same staged synthesis, QA, acceptance, concatenation, and caption
commands with `--build-dir audiobook-build-book01`.

## Required human listening

Listen to:

1. every candidate marked `review`;
2. both sides of every chunk boundary;
3. the beginning, middle, and end of every accepted chunk;
4. every house-pronunciation occurrence during the qualification pilot.

The report's speaking-rate, loudness, and silence values identify coarse
outliers. They do not prove narrator identity. A later production enhancement
may add a speaker-embedding comparison against a selected golden Fable clip.
