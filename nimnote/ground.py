"""Grounded retrieval: TF-IDF over chunks (no external deps).

Supports Latin/Thai scripts: for whitespace-free scripts (Thai) it falls back
to character bigrams so sub-word matching still works.
"""
from __future__ import annotations

import math
import re
from collections import Counter

_TOKEN_RE = re.compile(r"[a-z0-9\u0e00-\u0e7f]+")


def _tokenize(text: str) -> list[str]:
    toks: list[str] = [t for t in _TOKEN_RE.findall(text.lower()) if len(t) > 1]
    # Thai has no spaces -> add character bigrams so retrieval works
    out: list[str] = []
    for t in toks:
        out.append(t)
        if any("\u0e00" <= ch <= "\u0e7f" for ch in t) and len(t) >= 2:
            for i in range(len(t) - 1):
                out.append(t[i : i + 2])
    return out


def retrieve(notebook: dict, query: str, top_k: int = 5) -> list[tuple]:
    """Return list of (source_dict, chunk_dict, score) for top matches."""
    chunks: list[tuple] = []
    for s in notebook.get("sources", []):
        for c in s.get("chunks", []):
            chunks.append((s, c))
    if not chunks:
        return []

    n = len(chunks)
    df: Counter = Counter()
    for _, c in chunks:
        for t in set(_tokenize(c["text"])):
            df[t] += 1

    qterms = _tokenize(query)
    scored: list[tuple] = []
    for s, c in chunks:
        tf = Counter(_tokenize(c["text"]))
        score = 0.0
        for qt in qterms:
            if qt in tf:
                idf = math.log((n + 1) / (df.get(qt, 0) + 1)) + 1
                score += tf[qt] * idf
        if score > 0:
            scored.append((score, s, c))

    scored.sort(key=lambda x: -x[0])
    return [(s, c, sc) for sc, s, c in scored[:top_k]]
