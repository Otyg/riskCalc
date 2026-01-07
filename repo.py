# repo.py
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class AnalysisListItem:
    analysis_id: str
    title: str
    date: str
    owner: str
    version: str


class JsonAnalysisRepository:
    def __init__(self, folder: Path):
        self.folder = folder
        self.folder.mkdir(parents=True, exist_ok=True)

    def _path(self, analysis_id: str) -> Path:
        # analysis_id = filnamn utan .json
        return self.folder / f"{analysis_id}.json"

    def list(self) -> list[AnalysisListItem]:
        items: list[AnalysisListItem] = []
        for p in sorted(self.folder.glob("*.json")):
            with p.open("r", encoding="utf-8") as f:
                d = json.load(f)

            items.append(
                AnalysisListItem(
                    analysis_id=p.stem,
                    title=str(d.get("analysis_object", p.stem)),
                    date=str(d.get("date", "")),
                    owner=str(d.get("owner", "")),
                    version=str(d.get("version", "")),
                )
            )

        # Om "date" är ISO (YYYY-MM-DD) så funkar str-sort bra
        items.sort(key=lambda x: x.date, reverse=True)
        return items

    def get_dict(self, analysis_id: str) -> dict[str, Any]:
        p = self._path(analysis_id)
        if not p.exists():
            raise FileNotFoundError(analysis_id)
        with p.open("r", encoding="utf-8") as f:
            return json.load(f)
