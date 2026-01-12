from __future__ import annotations

import json
from pathlib import Path


class JsonThreatsRepository:
    def __init__(self, path: Path):
        self.path = path

    def load(self) -> list[str]:
        if not self.path.exists():
            return []
        with self.path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        threats = data.get("threats", [])
        cleaned = sorted({str(t).strip() for t in threats if str(t).strip()})
        return cleaned
