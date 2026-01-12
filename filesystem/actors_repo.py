from __future__ import annotations

import json
from pathlib import Path


class JsonActorsRepository:
    def __init__(self, path: Path):
        self.path = path

    def load(self) -> list[str]:
        if not self.path.exists():
            return []
        with self.path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        actors = data.get("actors", [])
        cleaned = sorted({str(a).strip() for a in actors if str(a).strip()})
        return cleaned
