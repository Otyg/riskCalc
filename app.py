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
from decimal import Decimal
from pathlib import Path
from typing import Any, Optional

import uvicorn
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.status import HTTP_200_OK, HTTP_303_SEE_OTHER
import re
import tempfile
from fastapi.responses import FileResponse

from common import D, get_scenario, set_questionaire_answers, set_scenario_parameters
from filesystem.actors_repo import JsonActorsRepository
from filesystem.paths import ensure_user_data_initialized, packaged_root
from filesystem.questionaires_repo import JsonQuestionairesRepository
from filesystem.repo import (
    DiscreteThresholdsRepository,
    DraftRepository,
    JsonAnalysisRepository,
    JsonCategoryRepository,
)
from filesystem.threats_repo import JsonThreatsRepository
from filesystem.vulnerabilities_repo import JsonVulnerabilitiesRepository
from otyg_risk_base.hybrid import HybridRisk
from riskcalculator.questionaire import Questionaires
from riskregister.assessment import RiskAssessment


app = FastAPI()
p = ensure_user_data_initialized()
os.environ["TEMPLATES_DIR"] = str(packaged_root() / "templates")
os.environ["DATA_DIR"] = str(p["data"])

BASE_DIR = Path(__file__).parent
TEMPLATES_DIR = Path(os.environ.get("TEMPLATES_DIR", str(BASE_DIR / "templates")))
DATA_DIR = Path(os.environ.get("DATA_DIR", str(BASE_DIR / "data")))
DEFAULT_QUESTIONAIRES_SET = "default"

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

analyses_repo = JsonAnalysisRepository(DATA_DIR / "analyses")
draft_repo = DraftRepository(DATA_DIR / "drafts")
questionaires_repo = JsonQuestionairesRepository(DATA_DIR / "questionaires")

actors_repo = JsonActorsRepository(DATA_DIR / "actors.json")
threats_repo = JsonThreatsRepository(DATA_DIR / "threats.json")
vulns_repo = JsonVulnerabilitiesRepository(DATA_DIR / "vulnerabilities.json")
categories_repo = JsonCategoryRepository(DATA_DIR / "categories.json")
discrete_thresholds_repo = DiscreteThresholdsRepository(
    DATA_DIR / "discrete_thresholds.json"
)


def _default_scenario_form() -> dict[str, str]:
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


def _load_questionaires_objects(qset: str) -> dict[str, Any]:
    """Load a questionaires-set for rendering. Returns {tef,vuln,lm} dict with None values on failure."""
    try:
        return questionaires_repo.load_objects(qset)
    except FileNotFoundError:
        return {"tef": None, "vuln": None, "lm": None}


def _scenario_suggestions() -> dict[str, Any]:
    """Collect suggestions used by scenario forms."""
    return {
        "threat_suggestions": threats_repo.load(),
        "actor_suggestions": actors_repo.load(),
        "vulnerability_suggestions": vulns_repo.load(),
        "category_suggestions": categories_repo.load(),
    }


def _build_risk_dict(form: Any) -> dict[str, Any]:
    return {
        "budget": str(D(str(form.get("budget", "1000000")))),
        "currency": str(form.get("currency", "SEK")) or "SEK",
    }


def _render_create_scenario(
    *,
    request: Request,
    draft_id: str,
    qset: str,
    qs: dict[str, Any],
    errors: list[str],
    risk_input_mode: str = "questionnaire",
    status_code: int = 200,
) -> HTMLResponse:
    context = {
        "request": request,
        "draft_id": draft_id,
        "defaults": {**_default_scenario_form(), "risk_input_mode": risk_input_mode},
        "errors": errors,
        "qs": qs,
        "qset": qset,
        "available_qsets": questionaires_repo.list_sets(),
        **_scenario_suggestions(),
    }
    return templates.TemplateResponse(
        "create_scenario_v4.html", context, status_code=status_code
    )


def _safe_filename(s: str) -> str:
    s = (s or "").strip()
    s = re.sub(r"[^A-Za-z0-9._-]+", "_", s)
    return s or "riskrapport"


@app.get("/analysis/{analysis_id}/export/pdf")
def export_analysis_pdf(analysis_id: str):
    analysis = analyses_repo.get_dict(
        analysis_id
    )  # du använder redan get_dict för att läsa analys :contentReference[oaicite:3]{index=3}

    # Din renderer (lägg report.py i projektet)
    from filesystem.report import build_pdf_report  # <-- se till att denna finns

    analysis_object = str(analysis.get("analysis_object", "") or "analysis")
    filename = f"{_safe_filename(analysis_object)}__{analysis_id}.pdf"

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp_path = tmp.name

    # build_pdf_report ska skriva PDF till tmp_path
    build_pdf_report(analysis, tmp_path, source_name=analysis_id)

    return FileResponse(
        tmp_path,
        media_type="application/pdf",
        filename=filename,
    )


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
        {
            "request": request,
            "analyses": analyses,
            "selected": selected,
            "analysis": analysis,
        },
    )


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

    return RedirectResponse(
        url=f"/?selected={analysis_id}", status_code=HTTP_303_SEE_OTHER
    )


@app.get("/create/{draft_id}/scenario/new", response_class=HTMLResponse)
def create_scenario_page(
    request: Request, draft_id: str, qset: str = DEFAULT_QUESTIONAIRES_SET
):
    # validate draft exists
    draft_repo.load(draft_id)

    qs = _load_questionaires_objects(qset)
    errors = [] if qs.get("tef") else [f"Kunde inte ladda questionaires-set: {qset}"]

    return templates.TemplateResponse(
        "create_scenario_v4.html",
        {
            "request": request,
            "draft_id": draft_id,
            "defaults": _default_scenario_form(),
            "errors": errors,
            "qs": qs,
            "qset": qset,
            "available_qsets": questionaires_repo.list_sets(),
            **_scenario_suggestions(),
        },
    )


@app.get(
    "/create/{draft_id}/scenario/{scenario_index}/edit", response_class=HTMLResponse
)
def edit_scenario_page(
    request: Request, draft_id: str, scenario_index: int, qset: str | None = None
):
    draft = draft_repo.load(draft_id)
    scenarios = draft.get("scenarios", [])

    if scenario_index < 0 or scenario_index >= len(scenarios):
        return RedirectResponse(
            url=f"/create/{draft_id}", status_code=HTTP_303_SEE_OTHER
        )

    scenario = scenarios[scenario_index]
    scenario_qset = (scenario.get("questionaires") or {}).get("qset")
    effective_qset = qset or scenario_qset or DEFAULT_QUESTIONAIRES_SET
    qs = scenario.get("questionaires") or _load_questionaires_objects(effective_qset)

    return templates.TemplateResponse(
        "edit_scenario_v1.html",
        {
            "request": request,
            "draft_id": draft_id,
            "scenario_index": scenario_index,
            "scenario": scenario,
            "qs": qs,
            "qset": effective_qset,
            "available_qsets": questionaires_repo.list_sets(),
            **_scenario_suggestions(),
            "errors": [],
        },
    )


async def _upsert_scenario_from_form(
    *,
    request: Request,
    draft_id: str,
    scenario_index: Optional[int] = None,
) -> HTMLResponse:
    """Create or update a scenario in a draft from submitted form data."""
    draft_dict = draft_repo.load(draft_id)
    draft = RiskAssessment(draft_dict)
    form = await request.form()

    risk_input_mode = str(form.get("risk_input_mode", "questionnaire"))
    qset = str(form.get("qset", DEFAULT_QUESTIONAIRES_SET))
    errors: list[str] = []

    risk_dict = _build_risk_dict(form)

    qs: dict[str, Any]
    if risk_input_mode == "questionnaire":
        seed_qs = None
        if scenario_index is not None:
            try:
                existing = draft.scenarios[scenario_index].questionaires.questionaires
                seed_qs = {
                    "qset": qset,
                    "tef": existing.get("tef"),
                    "vuln": existing.get("vuln"),
                    "lm": existing.get("lm"),
                }
            except Exception:
                seed_qs = None

        qs = set_questionaire_answers(
            form=form,
            questionaires_repo=questionaires_repo,
            qset=qset,
            errors=errors,
            qs=seed_qs,
        )
    else:
        qs = _load_questionaires_objects(qset)

    if errors:
        qs_for_render = _load_questionaires_objects(qset)
        return _render_create_scenario(
            request=request,
            draft_id=draft_id,
            qset=qset,
            qs=qs_for_render,
            errors=errors,
            risk_input_mode=risk_input_mode,
            status_code=400,
        )

    scenario_obj = get_scenario(
        qs=qs,
        risk_dict=risk_dict,
        discrete_thresholds_repo=discrete_thresholds_repo,
        parameters=set_scenario_parameters(form),
    )

    if scenario_index is None:
        draft.add_scenario(scenario=scenario_obj)
    else:
        draft.update_scenario(index=scenario_index, scenario=scenario_obj)

    draft_repo.save(draft_id, draft.to_dict())
    return RedirectResponse(url=f"/create/{draft_id}", status_code=HTTP_303_SEE_OTHER)


@app.post("/create/{draft_id}/scenario/save")
async def create_scenario_save(request: Request, draft_id: str):
    return await _upsert_scenario_from_form(
        request=request, draft_id=draft_id, scenario_index=None
    )


@app.post("/create/{draft_id}/scenario/{scenario_index}/update")
async def edit_scenario_save(request: Request, draft_id: str, scenario_index: int):
    return await _upsert_scenario_from_form(
        request=request, draft_id=draft_id, scenario_index=scenario_index
    )


@app.post("/analysis/{analysis_id}/new-version")
def new_version_from_analysis(analysis_id: str):
    original = analyses_repo.get_dict(analysis_id)

    draft = dict(original)
    draft["version"] = ""
    draft["date"] = ""
    draft.setdefault("scenarios", [])
    draft["previous_analysis_id"] = analysis_id
    draft_id = draft_repo.create_from(draft)

    return RedirectResponse(url=f"/create/{draft_id}", status_code=HTTP_303_SEE_OTHER)


@app.post("/create/{draft_id}/scenario/{scenario_index}/delete")
def delete_scenario(draft_id: str, scenario_index: int):
    draft = draft_repo.load(draft_id)
    scenarios = draft.get("scenarios", [])
    if 0 <= scenario_index < len(scenarios):
        scenarios.pop(scenario_index)
        draft["scenarios"] = scenarios
        draft_repo.save(draft_id, draft)
    return RedirectResponse(url=f"/create/{draft_id}", status_code=HTTP_303_SEE_OTHER)


@app.get("/risk-calc", response_class=HTMLResponse)
def risk_calc_page(request: Request, qset: str | None = None):
    available_qsets = questionaires_repo.list_sets()
    effective_qset = qset or (available_qsets[0] if available_qsets else "default")
    available_thresholds_names = discrete_thresholds_repo.get_set_names()
    qs = _load_questionaires_objects(effective_qset)

    return templates.TemplateResponse(
        "risk_calc.html",
        {
            "request": request,
            "available_qsets": available_qsets,
            "qset": effective_qset,
            "qs": qs,
            "available_thresholds": available_thresholds_names,
            "result": None,
            "errors": [],
            "mode": "questionnaire",  # default
            "manual": {
                "tef": {"min": "", "probable": "", "max": ""},
                "vuln": {"min": "", "probable": "", "max": ""},
                "lm": {"min": "", "probable": "", "max": ""},
                "budget": "1000000",
                "currency": "SEK",
            },
        },
        status_code=HTTP_200_OK,
    )


@app.post("/risk-calc", response_class=HTMLResponse)
async def risk_calc_submit(request: Request):
    form = await request.form()

    mode = str(form.get("risk_input_mode", "questionnaire"))
    qset = str(form.get("qset", "")) or None

    available_qsets = questionaires_repo.list_sets()
    effective_qset = qset or (available_qsets[0] if available_qsets else "default")
    available_thresholds_names = discrete_thresholds_repo.get_set_names()

    qs = _load_questionaires_objects(effective_qset)

    threshold_set = discrete_thresholds_repo.load(form.get("threshold_set", ""))

    errors: list[str] = []
    result = None

    if mode == "manual":
        values = {
            "threat_event_frequency": {
                "min": str(D(form.get("tef_min"))),
                "probable": str(D(form.get("tef_probable"))),
                "max": str(D(form.get("tef_max"))),
            },
            "vulnerability": {
                "min": str(D(form.get("vuln_min"))),
                "probable": str(D(form.get("vuln_probable"))),
                "max": str(D(form.get("vuln_max"))),
            },
            "loss_magnitude": {
                "min": str(D(form.get("lm_min"))),
                "probable": str(D(form.get("lm_probable"))),
                "max": str(D(form.get("lm_max"))),
            },
            "budget": D(str(form.get("budget", "1000000")), Decimal("1000000")),
            "currency": str(form.get("currency", "SEK") or "SEK"),
            "thresholds": threshold_set,
        }

        try:
            risk = HybridRisk(values=values)
            result = risk.to_dict() if hasattr(risk, "to_dict") else {"risk": str(risk)}
        except Exception as e:
            errors.append(f"Kunde inte skapa Risk från manuella intervall: {e}")

    else:
        tef_q = qs.get("tef")
        vuln_q = qs.get("vuln")
        lm_q = qs.get("lm")

        if not tef_q or not vuln_q or not lm_q:
            errors.append(
                "Valt formulär saknar en eller flera dimensioner (tef/vuln/lm)."
            )

        qs = set_questionaire_answers(
            form=form,
            questionaires_repo=questionaires_repo,
            errors=errors,
            qset=qset,
            qs=qs,
        )

        if not errors:
            questionaires = Questionaires(
                tef=qs.get("tef"), vuln=qs.get("vuln"), lm=qs.get("lm")
            )
            values = questionaires.calculate_questionairy_values()
            values.update({"budget": Decimal("1000000")})
            values.update({"currency": "SEK"})
            values.update({"mappings": threshold_set.to_dict()})
            risk = HybridRisk(values=values)
            result = risk.to_dict() if hasattr(risk, "to_dict") else {"risk": str(risk)}

    return templates.TemplateResponse(
        "risk_calc.html",
        {
            "request": request,
            "available_qsets": available_qsets,
            "qset": effective_qset,
            "qs": qs,
            "result": result,
            "errors": errors,
            "mode": mode,
            "available_thresholds": available_thresholds_names,
            "threshold_set": threshold_set,
            "manual": {
                "tef": {
                    "min": form.get("tef_min", ""),
                    "probable": form.get("tef_probable", ""),
                    "max": form.get("tef_max", ""),
                },
                "vuln": {
                    "min": form.get("vuln_min", ""),
                    "probable": form.get("vuln_probable", ""),
                    "max": form.get("vuln_max", ""),
                },
                "lm": {
                    "min": form.get("lm_min", ""),
                    "probable": form.get("lm_probable", ""),
                    "max": form.get("lm_max", ""),
                },
                "budget": str(form.get("budget", "1000000")),
                "currency": str(form.get("currency", "SEK")),
            },
        },
    )


@app.get("/license", response_class=HTMLResponse)
def license_page(request: Request):
    return templates.TemplateResponse(
        "license.html",
        {
            "request": request,
        },
        status_code=HTTP_200_OK,
    )


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
