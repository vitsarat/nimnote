"""Source ingestion: text / local file / URL -> chunked Source objects."""
from __future__ import annotations

import re
import ssl
import urllib.request
from pathlib import Path

from .store import Source, Chunk, _uid, _now

CHUNK_SIZE = 900
OVERLAP = 120


def _chunk(text: str) -> list[Chunk]:
    text = text.strip()
    if not text:
        return []
    chunks: list[Chunk] = []
    start = 0
    idx = 0
    while start < len(text):
        end = min(start + CHUNK_SIZE, len(text))
        seg = text[start:end]
        chunks.append(Chunk(cid=_uid(), idx=idx, text=seg))
        idx += 1
        if end == len(text):
            break
        start = end - OVERLAP
    return chunks


def ingest_text(
    title: str, text: str, kind: str = "text", uri: str = ""
) -> Source:
    return Source(
        id=_uid(),
        title=title,
        kind=kind,
        uri=uri,
        created=_now(),
        content=text,
        chunks=_chunk(text),
    )


def ingest_file(path: str, title: str | None = None) -> Source:
    p = Path(path)
    text = p.read_text(encoding="utf-8", errors="ignore")
    if p.suffix.lower() in (".html", ".htm"):
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text)
    return ingest_text(title or p.name, text, kind="file", uri=str(p))


def ingest_url(url: str, title: str | None = None) -> Source:
    ctx = ssl.create_default_context()
    req = urllib.request.Request(url, headers={"User-Agent": "nimnote/0.1"})
    with urllib.request.urlopen(req, context=ctx, timeout=20) as r:
        raw = r.read().decode("utf-8", "ignore")
    text = re.sub(r"<[^>]+>", " ", raw)
    text = re.sub(r"\s+", " ", text)
    return ingest_text(title or url, text, kind="url", uri=url)
