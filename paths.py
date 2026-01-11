from __future__ import annotations

import os
import sys
import shutil
from pathlib import Path


APP_NAME = "RiskAnalysisUI"


def packaged_root() -> Path:
    """
    Roten för paketerade resurser.
    Vid PyInstaller onefile finns allt i sys._MEIPASS.
    """
    base = getattr(sys, "_MEIPASS", None)
    if base:
        return Path(base)
    return Path(__file__).parent


def user_app_root() -> Path:
    """
    Windows: %APPDATA%\\RiskAnalysisUI
    Fallback: ~\\AppData\\Roaming\\RiskAnalysisUI
    """
    appdata = os.environ.get("APPDATA")
    if appdata:
        return Path(appdata) / APP_NAME
    return Path.home() / "AppData" / "Roaming" / APP_NAME


def ensure_user_data_initialized() -> dict[str, Path]:
    """
    Skapar användarmappar och kopierar seed-data vid första start.

    Returnerar paths:
      root, data, analyses, drafts, questionaires, actors_json, threats_json, vulnerabilities_json
    """
    root = user_app_root()
    data_dir = root / "data"
    analyses_dir = data_dir / "analyses"
    drafts_dir = data_dir / "drafts"
    questionaires_dir = data_dir / "questionaires"

    analyses_dir.mkdir(parents=True, exist_ok=True)
    drafts_dir.mkdir(parents=True, exist_ok=True)
    questionaires_dir.mkdir(parents=True, exist_ok=True)

    # Seed-källa (paketerad)
    seed_data_dir = packaged_root() / "data"
    seed_questionaires_dir = seed_data_dir / "questionaires"

    # Kopiera listfiler om de saknas
    for filename in ["actors.json", "threats.json", "vulnerabilities.json"]:
        src = seed_data_dir / filename
        dst = data_dir / filename
        if src.exists() and not dst.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)

    # Kopiera questionaires-sets (*.json) om de saknas
    if seed_questionaires_dir.exists():
        for src in seed_questionaires_dir.glob("*.json"):
            dst = questionaires_dir / src.name
            if not dst.exists():
                shutil.copy2(src, dst)

    return {
        "root": root,
        "data": data_dir,
        "analyses": analyses_dir,
        "drafts": drafts_dir,
        "questionaires": questionaires_dir,
        "actors_json": data_dir / "actors.json",
        "threats_json": data_dir / "threats.json",
        "vulnerabilities_json": data_dir / "vulnerabilities.json",
    }
