# app.py
from __future__ import annotations
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from repo import JsonAnalysisRepository

app = FastAPI()

BASE_DIR = Path(__file__).parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

repo = JsonAnalysisRepository(BASE_DIR / "data" / "analyses")


@app.get("/", response_class=HTMLResponse)
def index(request: Request, selected: str | None = None):
    analyses = repo.list()
    analysis = None

    if selected:
        try:
            analysis = repo.get_dict(selected)  # dict direkt från JSON
        except FileNotFoundError:
            analysis = None

    return templates.TemplateResponse(
        "list.html",
        {
            "request": request,
            "analyses": analyses,
            "selected": selected,
            "analysis": analysis,
        },
    )
