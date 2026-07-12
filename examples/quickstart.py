"""Quickstart: build a notebook from two sample sources and export artifacts.

Run:  python examples/quickstart.py
"""
import os
import tempfile

# Point the store at a temp dir so the demo is side-effect free.
os.environ["NIMNOTE_HOME"] = tempfile.mkdtemp()

from nimnote import (
    NotebookStore,
    ingest_text,
    retrieve,
    build_data_table,
    build_citation_index,
    build_mindmap_json,
)

store = NotebookStore()
nb = store.create_notebook("E-waste recovery")

src1 = ingest_text(
    "Mobile PCB",
    "Gold and copper dominate the value of mobile PCBs. "
    "Gómez et al. (2023) report gold grades near 200-300 g/tonne. "
    "Recovered metals fund circular e-waste recycling.",
)
src2 = ingest_text(
    "Catalytic converter",
    "Catalytic converters concentrate platinum, palladium and rhodium. "
    "Rhodium is the most valuable per gram. Recovery depends on the process.",
)
store.add_source(nb["id"], src1)
store.add_source(nb["id"], src2)

print("== ask: 'gold' ==")
for s, c, sc in retrieve(store.get(nb["id"]), "gold", top_k=2):
    print(f"  [{s['id']}] {s['title']} -> {c['text'][:80]}...")

print("\n== data table ==")
print(build_data_table(store.get(nb["id"])))

print("\n== mind map ==")
print(build_mindmap_json(store.get(nb["id"])))

print("\n== citation index (first 200 chars) ==")
print(build_citation_index(store.get(nb["id"]))[:200])
