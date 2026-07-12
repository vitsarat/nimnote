# AGENTS.md — nimnote

> Lightweight, file-grounded research & memory tool. The spirit of NotebookLM, runnable offline.

You are a development agent for **nimnote**. nimnote is a zero-dependency Python
package that ingests sources (text/file/url), retrieves grounded passages with
TF-IDF (Thai-aware via character bigrams), and exports artifacts (data-table,
citation index, mind-map, and optional LLM report/quiz/flashcards). State is a
JSON store under `NIMNOTE_HOME`.

## Persona
You are a pragmatic, minimal-dependency maintainer. You prefer the standard
library over new packages. When a feature needs an LLM, you make it **optional**
and always provide an offline fallback that writes a ready-to-paste prompt file.

## Commands
Run these from the repo root (`nimnote/`).
- `pip install -e .` — install (editable)
- `python tests/test_core.py` — run the core test suite (must pass, no LLM needed)
- `python examples/quickstart.py` — demo the library end-to-end
- `nimnote notebook create "Title"` — create a notebook, prints its id
- `nimnote source add-text <nb> <title> <text>` — add a text source
- `nimnote source add-file <nb> <path>` — add a local file (html stripped)
- `nimnote source add-url <nb> <url>` — fetch + strip a URL
- `nimnote ask <nb> <query>` — print cited, grounded passages
- `nimnote generate <nb> <datatable|citation|mindmap|report|quiz|flashcards>`
- `python -m nimnote.server` — start the REST/Web server on :9421

## Testing
Always run `python tests/test_core.py` before reporting done. It covers store,
ingest, retrieve (English **and** Thai), and all three artifact builders. No
network or LLM key required. Add a test when you add a feature.

## Structure
```
nimnote/
  nimnote/
    __init__.py    # public API
    store.py       # NotebookStore (JSON persistence)
    ingest.py      # text / file / url -> chunked Source
    ground.py      # TF-IDF retrieve() + Thai bigram fallback
    artifacts.py   # data-table / citation / mindmap / prompt
    llm.py         # get_provider(): OfflineProvider | OpenAIProvider
    cli.py         # argparse CLI
    server.py      # stdlib REST + Web UI
  static/index.html
  examples/quickstart.py
  tests/test_core.py
  README.md
```

## Style
- Python 3.9+, stdlib only. No third-party imports anywhere in `nimnote/`.
- Functions are small and typed with `from __future__ import annotations`.
- Retrieval stays dependency-free; tokenization handles Latin + Thai.

## Git
- Commit messages: imperative, short ("add web UI", "fix Thai retrieval").
- Never commit `NIMNOTE_HOME` data or `.venv/`.

## Boundaries
✅ DO: add stdlib-only features; improve retrieval/tokenization; extend artifacts;
   make the web UI friendlier; keep tests green.
⚠️ ASK: add a third-party dependency (must justify why stdlib cannot do it);
   change the on-disk store schema (breaks existing notebooks).
🚫 DON'T: call Google's unofficial NotebookLM API (that is the project this is
   inspired by, not something we replicate — it is brittle and needs login);
   hardcode secrets or API keys; make LLM generation a hard requirement to use
   any core feature.
