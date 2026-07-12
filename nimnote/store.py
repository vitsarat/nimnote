"""Persistent notebook store (JSON file under NIMNOTE_HOME)."""
from __future__ import annotations

import json
import os
import uuid
import datetime
from pathlib import Path
from dataclasses import dataclass, field, asdict


def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def _uid() -> str:
    return uuid.uuid4().hex[:12]


def _default_home() -> Path:
    return Path(os.environ.get("NIMNOTE_HOME", Path.home() / ".nimnote"))


@dataclass
class Chunk:
    cid: str
    idx: int
    text: str


@dataclass
class Source:
    id: str
    title: str
    kind: str
    uri: str
    created: str
    content: str
    chunks: list = field(default_factory=list)


@dataclass
class Note:
    id: str
    title: str
    body: str
    created: str
    refs: list = field(default_factory=list)


@dataclass
class Notebook:
    id: str
    title: str
    created: str
    sources: list = field(default_factory=list)
    notes: list = field(default_factory=list)


class NotebookStore:
    def __init__(self, home: str | Path | None = None):
        self.home = Path(home) if home else _default_home()
        self.home.mkdir(parents=True, exist_ok=True)
        self.path = self.home / "store.json"
        self.data = self._load()

    def _load(self) -> dict:
        if self.path.exists():
            try:
                return json.loads(self.path.read_text(encoding="utf-8"))
            except Exception:
                return {"notebooks": {}}
        return {"notebooks": {}}

    def _save(self) -> None:
        self.path.write_text(
            json.dumps(self.data, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def create_notebook(self, title: str) -> dict:
        nb = Notebook(id=_uid(), title=title, created=_now())
        self.data["notebooks"][nb.id] = asdict(nb)
        self._save()
        return self.get(nb.id)

    def get(self, nb_id: str) -> dict | None:
        return self.data["notebooks"].get(nb_id)

    def list(self) -> list[dict]:
        return list(self.data["notebooks"].values())

    def delete(self, nb_id: str) -> None:
        self.data["notebooks"].pop(nb_id, None)
        self._save()

    def add_source(self, nb_id: str, src: Source) -> None:
        nb = self.data["notebooks"][nb_id]
        nb["sources"].append(asdict(src))
        self._save()

    def add_note(self, nb_id: str, note: Note) -> None:
        nb = self.data["notebooks"][nb_id]
        nb["notes"].append(asdict(note))
        self._save()
