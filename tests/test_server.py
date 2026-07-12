"""Self-contained end-to-end test: start server in a thread, hit it, stop it."""
import os
import sys
import tempfile
import threading
import time
import urllib.request
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["NIMNOTE_HOME"] = tempfile.mkdtemp()

from nimnote import server as srv_mod


def _post(path, payload):
    req = urllib.request.Request(
        "http://127.0.0.1:9421" + path,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=10) as r:
        return r.read().decode()


def main() -> int:
    httpd = srv_mod.ThreadingHTTPServer(("127.0.0.1", 9421), srv_mod.Handler)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    time.sleep(1.5)

    # index
    with urllib.request.urlopen("http://127.0.0.1:9421/", timeout=10) as r:
        html = r.read().decode()
    assert "nimnote" in html, "index should contain title"
    print("[ok] GET / -> index served (%d bytes)" % len(html))

    # create notebook
    nb = json.loads(_post("/api/notebooks", {"title": "E2E"}))
    assert nb["id"], "notebook id"
    print("[ok] POST /api/notebooks ->", nb["id"])

    # add source (thai)
    src = json.loads(
        _post(
            "/api/sources",
            {
                "notebook": nb["id"],
                "kind": "text",
                "title": "Doc1",
                "body": "Gold recovers from PCB. กู้คืนโลหะมีค่าจาก e-waste ด้วยการสกัด.",
            },
        )
    )
    print("[ok] POST /api/sources ->", src["id"])

    # ask (thai)
    hits = json.loads(_post("/api/ask", {"notebook": nb["id"], "query": "โลหะมีค่า", "top": 1}))
    assert hits, "thai ask should return hits"
    print("[ok] POST /api/ask (thai) -> score %.2f" % hits[0]["score"])

    # generate datatable
    dt = _post("/api/generate", {"notebook": nb["id"], "kind": "datatable"})
    assert "Doc1" in dt, "datatable lists source"
    print("[ok] POST /api/generate datatable (%d chars)" % len(dt))

    # generate mindmap (json)
    mm = json.loads(_post("/api/generate", {"notebook": nb["id"], "kind": "mindmap"}))
    assert mm["sources"][0]["title"] == "Doc1"
    print("[ok] POST /api/generate mindmap ->", mm["sources"][0]["title"])

    httpd.shutdown()
    print("\nALL E2E TESTS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
