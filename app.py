from __future__ import annotations

from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.status import HTTP_303_SEE_OTHER

from repo import JsonAnalysisRepository, DraftRepository

app = FastAPI()

BASE_DIR = Path(__file__).parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

analyses_repo = JsonAnalysisRepository(BASE_DIR / "data" / "analyses")
draft_repo = DraftRepository(BASE_DIR / "data" / "drafts")


# ----------------------
# Helpers
# ----------------------
def _d(s: str, default: Decimal = Decimal(0)) -> Decimal:
    try:
        s = (s or "").strip()
        return Decimal(s) if s != "" else default
    except (InvalidOperation, ValueError):
        return default


def _validate_range(prefix: str, mn: str, pr: str, mx: str, errors: list[str]) -> None:
    dmn = _d(mn, Decimal(0))
    dpr = _d(pr, Decimal(0))
    dmx = _d(mx, Decimal(0))
    if dmn > dpr or dpr > dmx:
        errors.append(f"{prefix}: förväntar min ≤ probable ≤ max (fick {dmn}, {dpr}, {dmx})")


def _default_scenario_form() -> dict[str, str]:
    # default från din Risk-konstruktor: probable 0.5 / 0.1 / 0.001, budget 1_000_000, currency SEK
    return {
        "tef_min": "0",
        "tef_probable": "0.5",
        "tef_max": "0",
        "vuln_score_min": "0",
        "vuln_score_probable": "0.1",
        "vuln_score_max": "0",
        "loss_magnitude_min": "0",
        "loss_magnitude_probable": "0.001",
        "loss_magnitude_max": "0",
        "budget": "1000000",
        "currency": "SEK",
    }


# ----------------------
# Visa/lista analyser
# ----------------------
@app.get("/", response_class=HTMLResponse)
def index(request: Request, selected: str | None = None):
    analyses = analyses_repo.list()
    analysis = None

    if selected:
        try:
            analysis = analyses_repo.get_dict(selected)
        except FileNotFoundError:
            analysis = None

    return templates.TemplateResponse(
        "list.html",
        {"request": request, "analyses": analyses, "selected": selected, "analysis": analysis},
    )


# ----------------------
# Skapa analys (wizard steg 1)
# ----------------------
@app.get("/create", response_class=HTMLResponse)
def create_analysis_start(request: Request):
    draft_id = draft_repo.create()
    return RedirectResponse(url=f"/create/{draft_id}", status_code=HTTP_303_SEE_OTHER)


@app.get("/create/{draft_id}", response_class=HTMLResponse)
def create_analysis_page(request: Request, draft_id: str):
    draft = draft_repo.load(draft_id)
    return templates.TemplateResponse(
        "create_analysis.html",
        {"request": request, "draft_id": draft_id, "draft": draft},
    )


@app.post("/create/{draft_id}/update")
def create_analysis_update(
    draft_id: str,
    analysis_object: str = Form(""),
    version: str = Form(""),
    date: str = Form(""),
    scope: str = Form(""),
    owner: str = Form(""),
):
    draft = draft_repo.load(draft_id)
    draft["analysis_object"] = analysis_object
    draft["version"] = version
    draft["date"] = date
    draft["scope"] = scope
    draft["owner"] = owner
    draft.setdefault("scenarios", [])
    draft_repo.save(draft_id, draft)
    return RedirectResponse(url=f"/create/{draft_id}", status_code=HTTP_303_SEE_OTHER)


@app.post("/create/{draft_id}/finalize")
def create_analysis_finalize(draft_id: str):
    draft = draft_repo.load(draft_id)
    draft.setdefault("scenarios", [])

    analysis_id = analyses_repo.save_new(draft)
    draft_repo.delete(draft_id)

    return RedirectResponse(url=f"/?selected={analysis_id}", status_code=HTTP_303_SEE_OTHER)


# ----------------------
# Skapa scenario (wizard steg 2)
# ----------------------
@app.get("/create/{draft_id}/scenario/new", response_class=HTMLResponse)
def create_scenario_page(request: Request, draft_id: str):
    # verifiera att draft finns
    draft_repo.load(draft_id)

    return templates.TemplateResponse(
        "create_scenario_v2.html",
        {
            "request": request,
            "draft_id": draft_id,
            "defaults": _default_scenario_form(),
            "errors": [],
        },
    )


@app.post("/create/{draft_id}/scenario/save")
def create_scenario_save(
    request: Request,
    draft_id: str,

    name: str = Form(""),
    actor: str = Form(""),
    asset: str = Form(""),
    threat: str = Form(""),
    vulnerability: str = Form(""),
    description: str = Form(""),

    tef_min: str = Form(""),
    tef_probable: str = Form(""),
    tef_max: str = Form(""),

    vuln_score_min: str = Form(""),
    vuln_score_probable: str = Form(""),
    vuln_score_max: str = Form(""),

    loss_magnitude_min: str = Form(""),
    loss_magnitude_probable: str = Form(""),
    loss_magnitude_max: str = Form(""),

    budget: str = Form("1000000"),
    currency: str = Form("SEK"),
):
    draft = draft_repo.load(draft_id)

    errors: list[str] = []
    if not (name or "").strip():
        errors.append("name: måste anges")

    _validate_range("tef", tef_min, tef_probable, tef_max, errors)
    _validate_range("vuln_score", vuln_score_min, vuln_score_probable, vuln_score_max, errors)
    _validate_range("loss_magnitude", loss_magnitude_min, loss_magnitude_probable, loss_magnitude_max, errors)

    # Dict som din RiskScenario.from_dict bör kunna ta (justera nycklar om din implementering skiljer sig)
    scenario_dict: dict[str, Any] = {
        "name": name,
        "actor": actor,
        "asset": asset,
        "threat": threat,
        "vulnerability": vulnerability,
        "description": description,
        "questionaires": {},  # v1: tomt
        "risk": {
            "tef": {"min": str(_d(tef_min)), "probable": str(_d(tef_probable)), "max": str(_d(tef_max))},
            "vuln_score": {"min": str(_d(vuln_score_min)), "probable": str(_d(vuln_score_probable)), "max": str(_d(vuln_score_max))},
            "loss_magnitude": {"min": str(_d(loss_magnitude_min)), "probable": str(_d(loss_magnitude_probable)), "max": str(_d(loss_magnitude_max))},
            "budget": str(_d(budget, Decimal(1000000))),
            "currency": (currency or "SEK"),
        },
    }

    if errors:
        defaults = {
            "tef_min": tef_min, "tef_probable": tef_probable, "tef_max": tef_max,
            "vuln_score_min": vuln_score_min, "vuln_score_probable": vuln_score_probable, "vuln_score_max": vuln_score_max,
            "loss_magnitude_min": loss_magnitude_min, "loss_magnitude_probable": loss_magnitude_probable, "loss_magnitude_max": loss_magnitude_max,
            "budget": budget, "currency": currency,
        }
        return templates.TemplateResponse(
            "create_scenario_v2.html",
            {"request": request, "draft_id": draft_id, "defaults": defaults, "errors": errors},
            status_code=400,
        )

    try:
        from riskcalculator.scenario import RiskScenario
        from riskcalculator.discret_scale import DiscreteRisk
        from riskcalculator.montecarlo import MonteCarloRange
        tef = MonteCarloRange(min=_d(tef_min),probable=_d(tef_probable), max=_d(tef_max))
        vuln_score = MonteCarloRange(min=_d(vuln_score_min), probable=_d(vuln_score_probable), max=_d(vuln_score_max))
        loss_magnitude = MonteCarloRange(min=_d(loss_magnitude_min),probable=_d(loss_magnitude_probable),max=_d(loss_magnitude_max))
        risk = DiscreteRisk(tef=tef, vuln_score=vuln_score, loss_magnitude=loss_magnitude, budget=Decimal(budget), currency=currency)
        scenario_obj = RiskScenario(name=name, actor=actor, asset=asset, threat=threat, vulnerability= vulnerability, risk=risk)
        scenario_json = scenario_obj.to_dict()
    except Exception as e:
        # fallback: spara dict rakt av om import/klass ej är kopplad ännu
        raise e

    draft.setdefault("scenarios", [])
    draft["scenarios"].append(scenario_json)
    draft_repo.save(draft_id, draft)

    return RedirectResponse(url=f"/create/{draft_id}", status_code=HTTP_303_SEE_OTHER)
