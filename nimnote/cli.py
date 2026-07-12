"""nimnote command-line interface."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .store import NotebookStore, Note, _uid, _now
from .ingest import ingest_text, ingest_file, ingest_url
from .ground import retrieve
from .artifacts import (
    build_data_table,
    build_citation_index,
    build_mindmap_json,
    render_prompt,
)
from .llm import get_provider


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="nimnote", description="Local grounded research & memory tool"
    )
    sub = ap.add_subparsers(dest="cmd")

    p = sub.add_parser("notebook", help="notebook operations")
    ps = p.add_subparsers(dest="nb")
    pc = ps.add_parser("create")
    pc.add_argument("title")
    ps.add_parser("list")
    pd = ps.add_parser("delete")
    pd.add_argument("id")

    s = sub.add_parser("source", help="source operations")
    ss = s.add_subparsers(dest="src")
    sa = ss.add_parser("add-text")
    sa.add_argument("notebook")
    sa.add_argument("title")
    sa.add_argument("text")
    sf = ss.add_parser("add-file")
    sf.add_argument("notebook")
    sf.add_argument("path")
    sf.add_argument("--title", default=None)
    su = ss.add_parser("add-url")
    su.add_argument("notebook")
    su.add_argument("url")
    su.add_argument("--title", default=None)

    a = sub.add_parser("ask")
    a.add_argument("notebook")
    a.add_argument("query")
    a.add_argument("--top", type=int, default=5)

    g = sub.add_parser("generate")
    g.add_argument("notebook")
    g.add_argument(
        "kind",
        choices=["report", "quiz", "flashcards", "datatable", "citation", "mindmap"],
    )
    g.add_argument("--query", default="")

    e = sub.add_parser("export")
    e.add_argument("notebook")
    e.add_argument("kind", choices=["datatable", "citation", "mindmap"])
    e.add_argument("out")

    args = ap.parse_args(argv)
    store = NotebookStore()

    if args.cmd == "notebook":
        if args.nb == "create":
            nb = store.create_notebook(args.title)
            print(nb["id"])
        elif args.nb == "list":
            for nb in store.list():
                print(f"{nb['id']}\t{nb['title']}\t{len(nb['sources'])} src")
        elif args.nb == "delete":
            store.delete(args.id)
            print("deleted")
        return 0

    if args.cmd == "source":
        if args.src == "add-text":
            src = ingest_text(args.title, args.text)
            store.add_source(args.notebook, src)
            print("added", src.id)
        elif args.src == "add-file":
            src = ingest_file(args.path, args.title)
            store.add_source(args.notebook, src)
            print("added", src.id)
        elif args.src == "add-url":
            src = ingest_url(args.url, args.title)
            store.add_source(args.notebook, src)
            print("added", src.id)
        return 0

    if args.cmd == "ask":
        nb = store.get(args.notebook)
        if not nb:
            print("no such notebook"); return 1
        hits = retrieve(nb, args.query, args.top)
        if not hits:
            print("no matches")
            return 0
        for s, c, sc in hits:
            print(f"[{s['id']}] {s['title']} (score {sc:.2f})\n{c['text'][:300]}\n---")
        return 0

    if args.cmd == "generate":
        nb = store.get(args.notebook)
        if not nb:
            print("no such notebook"); return 1
        if args.kind == "datatable":
            print(build_data_table(nb))
        elif args.kind == "citation":
            print(build_citation_index(nb))
        elif args.kind == "mindmap":
            print(json.dumps(build_mindmap_json(nb), ensure_ascii=False, indent=2))
        else:
            hits = retrieve(nb, args.query, 8)
            grounded = "\n\n".join(f"[{s['id']}] {c['text']}" for s, c, _ in hits)
            prompt = render_prompt(args.kind, nb, args.query, grounded)
            provider = get_provider()
            text = provider.complete(
                "You are a research assistant. Cite by [source_id].", prompt
            )
            if text:
                print(text)
            else:
                Path("nimnote_prompt.md").write_text(prompt, encoding="utf-8")
                print("LLM not configured. Wrote nimnote_prompt.md — paste into your chat model.")
        return 0

    if args.cmd == "export":
        nb = store.get(args.notebook)
        if not nb:
            print("no such notebook"); return 1
        if args.kind == "datatable":
            Path(args.out).write_text(build_data_table(nb), encoding="utf-8")
        elif args.kind == "citation":
            Path(args.out).write_text(build_citation_index(nb), encoding="utf-8")
        elif args.kind == "mindmap":
            Path(args.out).write_text(
                json.dumps(build_mindmap_json(nb), ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        print("exported", args.out)
        return 0

    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
