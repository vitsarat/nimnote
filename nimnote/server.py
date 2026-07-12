"""Local REST + Web UI server (stdlib only)."""
from __future__ import annotations

import json
import os
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from .store import NotebookStore
from .ingest import ingest_text, ingest_file, ingest_url
from .ground import retrieve
from .artifacts import (
    build_data_table,
    build_citation_index,
    build_mindmap_json,
    render_prompt,
)
from .llm import get_provider

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


class Handler(BaseHTTPRequestHandler):
    store = NotebookStore()

    def _send(self, code, body, ctype="application/json"):
        if isinstance(body, (dict, list)):
            body = json.dumps(body, ensure_ascii=False)
        if not isinstance(body, bytes):
            body = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        if u.path in ("/", "/index.html"):
            html = (STATIC_DIR / "index.html").read_text(encoding="utf-8")
            return self._send(200, html, "text/html; charset=utf-8")
        if u.path == "/api/notebooks":
            return self._send(
                200, [{"id": n["id"], "title": n["title"]} for n in self.store.list()]
            )
        self._send(404, {"error": "not found"})

    def do_POST(self):
        u = urllib.parse.urlparse(self.path)
        length = int(self.headers.get("Content-Length", 0))
        data = json.loads(self.rfile.read(length) or b"{}")

        if u.path == "/api/notebooks":
            nb = self.store.create_notebook(data.get("title", "untitled"))
            return self._send(201, {"id": nb["id"]})

        if u.path == "/api/sources":
            nb_id = data.get("notebook", "")
            kind = data.get("kind", "text")
            title = data.get("title", "untitled")
            body = data.get("body", "")
            if kind == "file":
                src = ingest_file(body, title)
            elif kind == "url":
                src = ingest_url(body, title)
            else:
                src = ingest_text(title, body)
            self.store.add_source(nb_id, src)
            return self._send(201, {"id": src.id})

        if u.path == "/api/ask":
            nb = self.store.get(data.get("notebook", ""))
            if not nb:
                return self._send(404, {"error": "no notebook"})
            hits = retrieve(nb, data.get("query", ""), data.get("top", 5))
            return self._send(
                200,
                [
                    {"source": s["id"], "score": sc, "text": c["text"]}
                    for s, c, sc in hits
                ],
            )

        if u.path == "/api/generate":
            nb = self.store.get(data.get("notebook", ""))
            if not nb:
                return self._send(404, {"error": "no notebook"})
            kind = data.get("kind", "datatable")
            if kind in ("datatable", "citation", "mindmap"):
                fn = {
                    "datatable": build_data_table,
                    "citation": build_citation_index,
                    "mindmap": build_mindmap_json,
                }[kind]
                out = fn(nb)
                if kind == "mindmap":
                    return self._send(200, out)
                return self._send(200, out, "text/plain; charset=utf-8")
            # LLM-driven
            hits = retrieve(nb, data.get("query", ""), 8)
            grounded = "\n\n".join(f"[{s['id']}] {c['text']}" for s, c, _ in hits)
            prompt = render_prompt(kind, nb, data.get("query", ""), grounded)
            provider = get_provider()
            text = provider.complete(
                "You are a research assistant. Cite by [source_id].", prompt
            )
            if text:
                return self._send(200, text, "text/plain; charset=utf-8")
            # offline fallback
            Path("nimnote_prompt.md").write_text(prompt, encoding="utf-8")
            return self._send(
                200,
                "LLM not configured. Wrote nimnote_prompt.md — paste into your chat model.",
                "text/plain; charset=utf-8",
            )

        self._send(404, {"error": "not found"})

    def log_message(self, *a):
        pass


def serve(port: int = 9421):
    httpd = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"nimnote running at http://127.0.0.1:{port}")
    httpd.serve_forever()
