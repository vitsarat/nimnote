"""nimnote — local, file-grounded research & memory tool.

The spirit of NotebookLM, runnable offline:
  * ingest sources (text / file / url)
  * retrieve grounded passages (citation-aware)
  * generate artifacts (data-table, citation index, mind-map, report/quiz/flashcards)
  * keep a persistent "notebook" store across sessions

No third-party dependencies. LLM generation is optional and plugs into any
OpenAI-compatible endpoint via env vars.
"""
from .store import NotebookStore
from .ingest import ingest_text, ingest_file, ingest_url
from .ground import retrieve
from .artifacts import (
    build_data_table,
    build_citation_index,
    build_mindmap_json,
    render_prompt,
)
from .llm import get_provider, OfflineProvider, OpenAIProvider

__version__ = "0.1.0"

__all__ = [
    "NotebookStore",
    "ingest_text",
    "ingest_file",
    "ingest_url",
    "retrieve",
    "build_data_table",
    "build_citation_index",
    "build_mindmap_json",
    "render_prompt",
    "get_provider",
    "OfflineProvider",
    "OpenAIProvider",
]
