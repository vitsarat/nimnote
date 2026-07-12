"""Core tests — run offline, no LLM required."""
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ["NIMNOTE_HOME"] = tempfile.mkdtemp()

from nimnote.store import NotebookStore
from nimnote.ingest import ingest_text
from nimnote.ground import retrieve
from nimnote.artifacts import (
    build_data_table,
    build_citation_index,
    build_mindmap_json,
)


def main() -> int:
    store = NotebookStore()
    nb = store.create_notebook("Test")
    assert nb["id"], "notebook should have an id"

    src = ingest_text(
        "Doc1",
        "NotebookLM helps research. กู้คืนโลหะมีค่าจาก e-waste ได้ด้วยการสกัด. "
        "Research offload saves tokens. Gold recovery from PCB is profitable.",
    )
    store.add_source(nb["id"], src)

    nb2 = store.get(nb["id"])
    assert len(nb2["sources"]) == 1, "source should be stored"

    hits = retrieve(nb2, "research")
    assert hits, "retrieve should find matches for 'research'"

    thai_hits = retrieve(nb2, "โลหะมีค่า")
    assert thai_hits, "retrieve should handle Thai queries"

    dt = build_data_table(nb2)
    assert "Doc1" in dt, "data table should list the source"

    ci = build_citation_index(nb2)
    assert "Doc1" in ci, "citation index should list the source"

    mm = build_mindmap_json(nb2)
    assert mm["sources"][0]["title"] == "Doc1"

    print("ALL TESTS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
