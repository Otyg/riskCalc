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

import os
import sys
import shutil
from pathlib import Path
import logging

APP_NAME = "RiskAnalysisUI"
logger = logging.getLogger(APP_NAME)
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(levelname)s:    %(message)s")
log_stream = logging.StreamHandler()
log_stream.setLevel(logging.INFO)
log_stream.setFormatter(formatter)
logger.addHandler(log_stream)


def packaged_root() -> Path:
    """
    Vid PyInstaller onefile finns allt i sys._MEIPASS.
    """
    base = getattr(sys, "_MEIPASS", None)
    if base:
        return Path(base)
    return Path(__file__).parent.parent


def user_app_root() -> Path:
    """
    Windows: %APPDATA%\\RiskAnalysisUI
    Fallback: ~\.local\share\RiskAnalysisUI
    """
    appdata = os.environ.get("APPDATA")
    if appdata:
        return Path(appdata) / APP_NAME
    return Path.home() / ".local" / "share" / APP_NAME


def ensure_user_data_initialized() -> dict[str, Path]:
    """
    Skapar användarmappar och kopierar seed-data vid första start.

    Returnerar paths:
      root, data, analyses, drafts, questionaires, actors_json, threats_json, vulnerabilities_json
    """

    root = user_app_root()
    logger.info("Setting up datadirectories, base: " + str(root.absolute()))
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
    for filename in [
        "actors.json",
        "threats.json",
        "vulnerabilities.json",
        "categories.json",
        "discrete_thresholds.json",
    ]:
        src = seed_data_dir / filename
        dst = data_dir / filename
        if src.exists() and not dst.exists():
            logger.info("Copy " + str(src.absolute()) + " to " + str(dst.absolute()))
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)

    # Kopiera questionaires-sets (*.json) om de saknas
    if seed_questionaires_dir.exists():
        for src in seed_questionaires_dir.glob("*.json"):
            dst = questionaires_dir / src.name
            if not dst.exists():
                logger.info(
                    "Copy " + str(src.absolute()) + " to " + str(dst.absolute())
                )
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
