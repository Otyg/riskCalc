from __future__ import annotations

import json
from pathlib import Path


class JsonVulnerabilitiesRepository:
    def __init__(self, path: Path):
        self.path = path

    def load(self) -> list[str]:
        if not self.path.exists():
            return []
        with self.path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        vulns = data.get("vulnerabilities", [])
        cleaned = sorted({str(v).strip() for v in vulns if str(v).strip()})
        return cleaned
