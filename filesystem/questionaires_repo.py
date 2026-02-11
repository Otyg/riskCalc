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
from pathlib import Path
from typing import Any
from riskcalculator.questionaire import Questionaire


class JsonQuestionairesRepository:
    """
    Laddar ett 'questionaires set' från data/questionaires/<set_id>.json
    och bygger dina Questionaire-objekt via from_dict.

    Förväntad JSON-struktur:
      {
        "tef":  {...},   # dict som Questionaire.from_dict kan läsa
        "vuln": {...},
        "lm":   {...}
      }
    """

    def __init__(self, folder: Path):
        self.folder = folder
        self.folder.mkdir(parents=True, exist_ok=True)

    def _path(self, set_id: str) -> Path:
        return self.folder / f"{set_id}.json"

    def list_sets(self) -> list[str]:
        return sorted([p.stem for p in self.folder.glob("*.json")])

    def load_dict(self, set_id: str) -> dict[str, Any]:
        p = self._path(set_id)
        if not p.exists():
            raise FileNotFoundError(set_id)
        with p.open("r", encoding="utf-8") as f:
            return json.load(f)

    def load_objects(self, set_id: str) -> dict[str, Any]:
        """
        Returnerar dict med nycklar: tef, vuln, lm
        och värden som är dina Questionaire-objekt.
        """
        raw = self.load_dict(set_id)

        tef = Questionaire.from_dict(raw.get("tef", {}))
        vuln = Questionaire.from_dict(raw.get("vuln", {}))
        lm = Questionaire.from_dict(raw.get("lm", {}))
        return {"qset": set_id, "tef": tef, "vuln": vuln, "lm": lm}
