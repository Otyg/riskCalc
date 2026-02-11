#
# MIT License
#
# Copyright (c) 2025 Martin Vesterlund
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
import uuid

from otyg_risk_base.qualitative_scale import QualitativeScale
from riskcalculator.util import ComplexEncoder


@dataclass(frozen=True)
class AnalysisListItem:
    analysis_id: str
    title: str
    date: str
    owner: str
    version: str
    summary: str


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
                    summary=str(d.get("summary", "")),
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

    def create_from(self, draft_dict: dict[str, Any]) -> str:
        """
        Skapa ett draft som är initierat från en existerande analys.
        """
        draft_id = uuid.uuid4().hex[:12]
        self.save(draft_id, draft_dict)
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


class JsonCategoryRepository:
    def __init__(self, path: Path):
        self.path = path

    def load(self) -> list[str]:
        if not self.path.exists():
            return []
        with self.path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        categories = data.get("categories", [])
        cleaned = sorted({str(c).strip() for c in categories if str(c).strip()})
        return cleaned


class DiscreteThresholdsRepository:
    def __init__(self, path: Path):
        self.path = path

    def __read_file(self):
        if not self.path.exists():
            raise FileNotFoundError(self.path)
        with self.path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return data

    def get_set_names(self):
        data = self.__read_file()
        return data.keys()

    def load(self, threshold_set: str = "default_thresholds") -> QualitativeScale:
        data = self.__read_file()
        return QualitativeScale(scales=data.get(threshold_set, {}))
