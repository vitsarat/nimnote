"""Artifact builders: data-table, citation index, mind-map, LLM prompt."""
from __future__ import annotations

import csv
import io
import json
from collections import Counter

from .ground import _tokenize

_STOP = set(
    (
        "the a an and or of to in on for with is are be this that it as at by from "
        "we you they he she but if then so their our your his her them us not no can "
        "will would could should may might must do does did has have had was were been "
        "being ของ และ ใน ที่ ไป จาก กับ ให้ ไม่ ได้ จะ ถ้า แต่ เพราะ ว่า ซึ่ง นี้ นั้น "
        "เรา คุณ เขา เธอ ก็ ได้ ไป"
    ).split()
)


def _terms(text: str) -> list[str]:
    return [t for t in _tokenize(text) if t not in _STOP]


def build_data_table(notebook: dict) -> str:
    rows = []
    global_terms: Counter = Counter()
    for s in notebook.get("sources", []):
        toks = _terms(s.get("content", ""))
        global_terms.update(toks)
        rows.append(
            {
                "id": s["id"],
                "title": s["title"],
                "kind": s["kind"],
                "chars": len(s.get("content", "")),
                "chunks": len(s.get("chunks", [])),
                "top_terms": ", ".join(t for t, _ in Counter(toks).most_common(5)),
            }
        )
    buf = io.StringIO()
    w = csv.DictWriter(
        buf, fieldnames=["id", "title", "kind", "chars", "chunks", "top_terms"]
    )
    w.writeheader()
    for r in rows:
        w.writerow(r)
    buf.write("\n# Global top terms\n")
    for t, c in global_terms.most_common(20):
        buf.write(f"{t},{c}\n")
    return buf.getvalue()


def build_citation_index(notebook: dict) -> str:
    lines = ["# Citation Index\n"]
    for s in notebook.get("sources", []):
        lines.append(f"## [{s['id']}] {s['title']}  ({s['kind']})\n")
        for c in s.get("chunks", []):
            snippet = c["text"][:160].replace("\n", " ")
            lines.append(f"- {c['cid']}: {snippet}...\n")
    return "\n".join(lines)


def build_mindmap_json(notebook: dict) -> dict:
    tree = {"notebook": notebook.get("title", ""), "sources": []}
    for s in notebook.get("sources", []):
        terms = [t for t, _ in Counter(_terms(s.get("content", ""))).most_common(8)]
        tree["sources"].append(
            {"id": s["id"], "title": s["title"], "terms": terms}
        )
    return tree


def render_prompt(kind: str, notebook: dict, query: str, grounded: str) -> str:
    system = (
        "You are a research assistant. Answer using ONLY the provided sources "
        "and cite them by [source_id]."
    )
    body = (
        f"## Task: {kind}\n## Query: {query}\n\n"
        f"## Grounded sources:\n{grounded}\n\nProduce the {kind} now."
    )
    return f"# NimNote prompt ({kind})\n\nSystem:\n{system}\n\n{body}\n"
