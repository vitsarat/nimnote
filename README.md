# nimnote

**Local, file-grounded research & memory tool** — built in the *spirit* of
[`notebooklm-py`](https://github.com/teng-lin/notebooklm-py), but runnable
**offline on your own machine**.

`notebooklm-py` reverse-engineers Google's undocumented NotebookLM API so an AI
agent can offload expensive reading/synthesis and pull structured artifacts out
in bulk. That approach is powerful but brittle (unofficial endpoints, login
required, can break anytime).

`nimnote` takes the *winning pattern* and rebuilds it on solid ground:

| notebooklm-py idea | nimnote implementation |
| --- | --- |
| Grounded Q&A from *your* sources | TF-IDF retrieval over your ingested chunks, citation-aware |
| Persistent cross-session memory | JSON notebook store under `NIMNOTE_HOME` |
| Bulk, scriptable artifact export | `datatable` / `citation` / `mindmap` generators |
| LLM-driven report / quiz / flashcards | Optional OpenAI-compatible provider; offline fallback writes a ready prompt |
| Zero-token research offload | Retrieval works with **no LLM at all**; generation is opt-in |

## Install

```bash
cd nimnote
pip install -e .          # or: python -m venv .venv && source .venv/bin/activate && pip install -e .
```

Zero third-party dependencies. Python 3.9+.

## Quickstart

```bash
export NIMNOTE_HOME="$HOME/.nimnote"   # optional, defaults there

nimnote notebook create "My research"
# -> prints a notebook id, e.g. a1b2c3d4e5f6

nimnote source add-text a1b2c3d4e5f6 "Note A" "Gold recovers from PCB at 200-300 g/t."
nimnote source add-file  a1b2c3d4e5f6 ./report.pdf
nimnote source add-url   a1b2c3d4e5f6 https://example.com/article

nimnote ask a1b2c3d4e5f6 "gold recovery"        # grounded passages, cited
nimnote generate a1b2c3d4e5f6 datatable          # CSV of sources + term freq
nimnote generate a1b2c3d4e5f6 citation           # citation index (markdown)
nimnote generate a1b2c3d4e5f6 mindmap            # hierarchical JSON
nimnote generate a1b2c3d4e5f6 report --query "summarize"   # needs LLM (see below)
nimnote export   a1b2c3d4e5f6 datatable out.csv
```

Or use it as a library (see `examples/quickstart.py`):

```python
from nimnote import NotebookStore, ingest_text, retrieve, build_data_table
store = NotebookStore()
nb = store.create_notebook("Demo")
store.add_source(nb["id"], ingest_text("Doc", "your text here"))
print(retrieve(store.get(nb["id"]), "your"))
```

## LLM generation (optional)

The `report` / `quiz` / `flashcards` generators call an LLM. Configure any
OpenAI-compatible endpoint:

```bash
export NIMNOTE_BASE_URL="https://api.openai.com/v1"
export NIMNOTE_API_KEY="sk-..."
export NIMNOTE_MODEL="gpt-4o-mini"
```

With no key set, `nimnote` writes a `nimnote_prompt.md` you can paste into any
chat model — so the tool is fully useful offline.

## Web UI + REST server

```bash
python -m nimnote.server        # http://127.0.0.1:9421
```

Opens a local web page where you can create notebooks, add text/url/file
sources, ask grounded questions, and generate artifacts — no CLI needed.
The same server exposes a JSON API:

| Method | Path | Body |
| --- | --- | --- |
| GET | `/` | serves the web UI |
| GET | `/api/notebooks` | list notebooks |
| POST | `/api/notebooks` | `{"title": "x"}` → `{"id": ...}` |
| POST | `/api/sources` | `{"notebook","kind","title","body"}` |
| POST | `/api/ask` | `{"notebook","query","top"}` → cited passages |
| POST | `/api/generate` | `{"notebook","kind","query"}` → artifact |

(`kind` ∈ datatable | citation | mindmap | report | quiz | flashcards)

## Test

```bash
python nimnote/tests/test_core.py
```

## License

MIT — same as `notebooklm-py`.
