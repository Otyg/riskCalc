from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from riskcalculator.util import ComplexEncoder


@dataclass(frozen=True)
class AnalysisListItem:
    analysis_id: str
    title: str
    date: str
    owner: str
    version: str


def _safe_slug(text: str) -> str:
    text = (text or "").strip().lower()
    text = re.sub(r"[^a-z0-9\-_]+", "-", text)
    text = re.sub(r"-{2,}", "-", text).strip("-")
    return text or "analysis"


class JsonAnalysisRepository:
    def __init__(self, analyses_folder: Path):
        self.folder = analyses_folder
        self.folder.mkdir(parents=True, exist_ok=True)

    def list(self) -> list[AnalysisListItem]:
        items: list[AnalysisListItem] = []
        for p in sorted(self.folder.glob("*.json")):
            try:
                with p.open("r", encoding="utf-8") as f:
                    d = json.load(f)
            except Exception:
                continue

            items.append(
                AnalysisListItem(
                    analysis_id=p.stem,
                    title=str(d.get("analysis_object", p.stem)),
                    date=str(d.get("date", "")),
                    owner=str(d.get("owner", "")),
                    version=str(d.get("version", "")),
                )
            )

        # Om date är ISO (YYYY-MM-DD) funkar str-sort ok
        items.sort(key=lambda x: x.date, reverse=True)
        return items

    def get_dict(self, analysis_id: str) -> dict[str, Any]:
        p = self.folder / f"{analysis_id}.json"
        if not p.exists():
            raise FileNotFoundError(analysis_id)
        with p.open("r", encoding="utf-8") as f:
            return json.load(f)

    def save_new(self, analysis: dict[str, Any]) -> str:
        slug = _safe_slug(str(analysis.get("analysis_object", "")))
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        analysis_id = f"{slug}_{ts}"
        path = self.folder / f"{analysis_id}.json"
        with path.open("w", encoding="utf-8") as f:
            json.dump(analysis, f, ensure_ascii=False, indent=2)
        return analysis_id


class DraftRepository:
    """
    Sparar utkast under data/drafts/<draft_id>.json
    """
    def __init__(self, drafts_folder: Path):
        self.folder = drafts_folder
        self.folder.mkdir(parents=True, exist_ok=True)

    def _path(self, draft_id: str) -> Path:
        return self.folder / f"{draft_id}.json"

    def create(self) -> str:
        draft_id = datetime.now().strftime("draft_%Y%m%d_%H%M%S_%f")
        self.save(
            draft_id,
            {
                "analysis_object": "",
                "version": "",
                "date": "",
                "scope": "",
                "owner": "",
                "scenarios": [],
            },
        )
        return draft_id

    def load(self, draft_id: str) -> dict[str, Any]:
        p = self._path(draft_id)
        if not p.exists():
            raise FileNotFoundError(draft_id)
        with p.open("r", encoding="utf-8") as f:
            return json.load(f)

    def save(self, draft_id: str, data: dict[str, Any]) -> None:
        p = self._path(draft_id)
        with p.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2, cls=ComplexEncoder)

    def delete(self, draft_id: str) -> None:
        p = self._path(draft_id)
        if p.exists():
            p.unlink()
