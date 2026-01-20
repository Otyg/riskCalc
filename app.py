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
import uvicorn
from decimal import Decimal, InvalidOperation
import os
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.status import HTTP_303_SEE_OTHER

from riskcalculator.scenario import RiskScenario
from riskcalculator.discret_scale import DiscreteRisk
from filesystem.actors_repo import JsonActorsRepository
from filesystem.repo import JsonAnalysisRepository, DraftRepository, JsonCategoryRepository
from filesystem.questionaires_repo import JsonQuestionairesRepository
from riskcalculator.questionaire import Questionaire, Questionaires
from filesystem.threats_repo import JsonThreatsRepository
from filesystem.vulnerabilities_repo import JsonVulnerabilitiesRepository
from riskregister.assessment import RiskAssessment
from filesystem.paths import ensure_user_data_initialized, packaged_root

DEFAULT_QUESTIONAIRES_SET = "default"
app = FastAPI()
p = ensure_user_data_initialized()
os.environ["TEMPLATES_DIR"] = str(packaged_root() / "templates")
os.environ["DATA_DIR"] = str(p["data"])
BASE_DIR = Path(__file__).parent
TEMPLATES_DIR = Path(os.environ.get("TEMPLATES_DIR", str(BASE_DIR / "templates")))
DATA_DIR = Path(os.environ.get("DATA_DIR", str(BASE_DIR / "data")))

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

analyses_repo = JsonAnalysisRepository(DATA_DIR / "analyses")
draft_repo = DraftRepository(DATA_DIR / "drafts")
questionaires_repo = JsonQuestionairesRepository(DATA_DIR / "questionaires")

actors_repo = JsonActorsRepository(DATA_DIR / "actors.json")
threats_repo = JsonThreatsRepository(DATA_DIR / "threats.json")
vulns_repo = JsonVulnerabilitiesRepository(DATA_DIR / "vulnerabilities.json")
categories_repo = JsonCategoryRepository(DATA_DIR / "categories.json")

def _d(s: str, default: Decimal = Decimal(0)) -> Decimal:
    try:
        s = (s or "").strip()
        return Decimal(s) if s != "" else default
    except (InvalidOperation, ValueError):
        return default


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


@app.get("/create/{draft_id}/scenario/new", response_class=HTMLResponse)
def create_scenario_page(request: Request, draft_id: str, qset: str = DEFAULT_QUESTIONAIRES_SET):
    draft_repo.load(draft_id)
    threat_suggestions = threats_repo.load()
    actor_suggestions = actors_repo.load()
    vulnerability_suggestions = vulns_repo.load()
    category_suggestions = categories_repo.load()

    try:
        qs = questionaires_repo.load_objects(qset)
    except FileNotFoundError:
        # om set saknas: visa tomt + fel
        qs = {"tef": None, "vuln": None, "lm": None}

    return templates.TemplateResponse(
        "create_scenario_v4.html",
        {
            "request": request,
            "draft_id": draft_id,
            "defaults": _default_scenario_form(),
            "errors": [] if qs["tef"] else [f"Kunde inte ladda questionaires-set: {qset}"],
            "qs": qs,
            "qset": qset,
            "available_qsets": questionaires_repo.list_sets(),
            "threat_suggestions": threat_suggestions,
            "actor_suggestions": actor_suggestions,
            "vulnerability_suggestions": vulnerability_suggestions,
            "category_suggestions": category_suggestions,
        },
    )

@app.get("/create/{draft_id}/scenario/{scenario_index}/edit", response_class=HTMLResponse)
def edit_scenario_page(request: Request, draft_id: str, scenario_index: int, qset: str | None = None):
    draft = draft_repo.load(draft_id)
    scenarios = draft.get("scenarios", [])

    if scenario_index < 0 or scenario_index >= len(scenarios):
        return RedirectResponse(url=f"/create/{draft_id}", status_code=HTTP_303_SEE_OTHER)

    scenario = scenarios[scenario_index]
    scenario_qset = (scenario.get("questionaires") or {}).get("qset")
    effective_qset = qset or scenario_qset or DEFAULT_QUESTIONAIRES_SET

    threat_suggestions = threats_repo.load()
    actor_suggestions = actors_repo.load()
    vulnerability_suggestions = vulns_repo.load()
    category_suggestions = categories_repo.load()

    # questionaires-set (för att rendera frågor). qset kommer via querystring.
    try:
        qs = scenario.get("questionaires")
    except FileNotFoundError:
        qs = {"tef": None, "vuln": None, "lm": None}

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
            "threat_suggestions": threat_suggestions,
            "actor_suggestions": actor_suggestions,
            "vulnerability_suggestions": vulnerability_suggestions,
            "category_suggestions": category_suggestions,
            "errors": [],
        },
    )

@app.post("/create/{draft_id}/scenario/save")
async def create_scenario_save(request: Request, draft_id: str):
    draft_dict = draft_repo.load(draft_id)
    draft=RiskAssessment(draft_dict)
    form = await request.form()

    name = str(form.get("name", "")).strip()
    actor = str(form.get("actor", "")).strip()
    asset = str(form.get("asset", "")).strip()
    threat = str(form.get("threat", "")).strip()
    vulnerability = str(form.get("vulnerability", "")).strip()
    description = str(form.get("description", "")).strip()
    category = str(form.get("category", "")).strip()
    risk_input_mode = str(form.get("risk_input_mode", "questionnaire"))
    qset = str(form.get("qset", DEFAULT_QUESTIONAIRES_SET))
    threat_suggestions = threats_repo.load()
    errors: list[str] = []
    
    risk_dict: dict[str, Any] = {
        "budget": str(_d(str(form.get("budget", "1000000")), Decimal(1000000))),
        "currency": str(form.get("currency", "SEK")) or "SEK",
    }
    if risk_input_mode == "questionnaire":
        try:
            qs = questionaires_repo.load_objects(qset)
        except FileNotFoundError:
            errors.append(f"Kunde inte ladda questionaires-set: {qset}")
            qs = {"tef": None, "vuln": None, "lm": None}

        # Sätt answers från dropdowns: q_<dim>_<qi> = alt_index
        for dim_key in ("tef", "vuln", "lm"):
            qobj = qs.get(dim_key)
            if qobj is None:
                continue

            for qi, question in enumerate(qobj.questions):
                raw = form.get(f"q_{dim_key}_{qi}")
                if raw is None or str(raw).strip() == "":
                    continue
                try:
                    ans_idx = int(raw)
                except ValueError:
                    continue

                question.set_answer(ans_idx)

    if errors:
        try:
            qs = questionaires_repo.load_objects(qset)
        except FileNotFoundError:
            qs = {"tef": None, "vuln": None, "lm": None}

        return templates.TemplateResponse(
            "create_scenario_v4.html",
            {
                "request": request,
                "draft_id": draft_id,
                "defaults": {**_default_scenario_form(), "risk_input_mode": risk_input_mode},
                "errors": errors,
                "qs": qs,
                "qset": qset,
                "available_qsets": questionaires_repo.list_sets(),
                "threat_suggestions": threat_suggestions,
                "category_suggestions": categories_repo.load(),
            },
            status_code=400,
        )

    try:
        print(qs.get('tef').mean())
        questionaires = Questionaires(tef=qs.get('tef'), vuln=qs.get('vuln'), lm=qs.get('lm'))
        questionaires_values = questionaires.calculate_questionairy_values()
        questionaires_values.update({'budget': Decimal(risk_dict.get('budget'))})
        questionaires_values.update({'currency': risk_dict.get('currency')})
        risk = DiscreteRisk(values=questionaires_values)
        scenario_obj = RiskScenario(parameters= {"name": name,
                                    "category": category,
                                    "actor": actor,
                                    "asset": asset,
                                    "threat": threat,
                                    "vulnerability": vulnerability,
                                    "description": description,
                                    "risk": risk,
                                    "questionaires": questionaires})
    except Exception as e:
        raise e

    draft.add_scenario(scenario=scenario_obj)
    draft_repo.save(draft_id, draft.to_dict())

    return RedirectResponse(url=f"/create/{draft_id}", status_code=HTTP_303_SEE_OTHER)

@app.post("/analysis/{analysis_id}/new-version")
def new_version_from_analysis(analysis_id: str):
    original = analyses_repo.get_dict(analysis_id)

    draft = dict(original)
    draft["version"] = ""
    draft["date"] = ""
    draft.setdefault("scenarios", [])
    draft["previous_analysis_id"] = analysis_id
    # Skapa draft från kopian
    draft_id = draft_repo.create_from(draft)

    return RedirectResponse(url=f"/create/{draft_id}", status_code=HTTP_303_SEE_OTHER)


@app.post("/create/{draft_id}/scenario/{scenario_index}/update")
async def edit_scenario_save(request: Request, draft_id: str, scenario_index: int):
    draft_dict = draft_repo.load(draft_id)
    draft=RiskAssessment(draft_dict)
    form = await request.form()

    name = str(form.get("name", "")).strip()
    actor = str(form.get("actor", "")).strip()
    asset = str(form.get("asset", "")).strip()
    threat = str(form.get("threat", "")).strip()
    vulnerability = str(form.get("vulnerability", "")).strip()
    description = str(form.get("description", "")).strip()
    category = str(form.get("category", "")).strip()
    risk_input_mode = str(form.get("risk_input_mode", "questionnaire"))
    qset = str(form.get("qset", DEFAULT_QUESTIONAIRES_SET))
    threat_suggestions = threats_repo.load()
    errors: list[str] = []
    
    risk_dict: dict[str, Any] = {
        "budget": str(_d(str(form.get("budget", "1000000")), Decimal(1000000))),
        "currency": str(form.get("currency", "SEK")) or "SEK",
    }
    if risk_input_mode == "questionnaire":
        try:
            tef = draft.scenarios[scenario_index].questionaires.questionaires['tef']
            vuln = draft.scenarios[scenario_index].questionaires.questionaires['vuln']
            lm = draft.scenarios[scenario_index].questionaires.questionaires['lm']
            qs = {"qset": scenario_index, "tef": tef, "vuln": vuln, "lm": lm}

        except FileNotFoundError:
            errors.append(f"Kunde inte ladda questionaires-set: {qset}")
            qs = {"tef": None, "vuln": None, "lm": None}

        # Sätt answers från dropdowns: q_<dim>_<qi> = alt_index
        for dim_key in ("tef", "vuln", "lm"):
            qobj = qs.get(dim_key)
            if qobj is None:
                continue

            for qi, question in enumerate(qobj.questions):
                raw = form.get(f"q_{dim_key}_{qi}")
                if raw is None or str(raw).strip() == "":
                    continue
                try:
                    ans_idx = int(raw)
                except ValueError:
                    continue

                question.set_answer(ans_idx)

    if errors:
        try:
            qs = questionaires_repo.load_objects(qset)
        except FileNotFoundError:
            qs = {"tef": None, "vuln": None, "lm": None}

        return templates.TemplateResponse(
            "create_scenario_v4.html",
            {
                "request": request,
                "draft_id": draft_id,
                "defaults": {**_default_scenario_form(), "risk_input_mode": risk_input_mode},
                "errors": errors,
                "qs": qs,
                "qset": qset,
                "available_qsets": questionaires_repo.list_sets(),
                "threat_suggestions": threat_suggestions,
                "category_suggestions": categories_repo.load(),
            },
            status_code=400,
        )

    try:
        questionaires = Questionaires(tef=qs.get('tef'), vuln=qs.get('vuln'), lm=qs.get('lm'))
        questionaires_values = questionaires.calculate_questionairy_values()
        questionaires_values.update({'budget': Decimal(risk_dict.get('budget'))})
        questionaires_values.update({'currency': risk_dict.get('currency')})
        risk = DiscreteRisk(values=questionaires_values)
        scenario_obj = RiskScenario(parameters= {"name": name,
                                    "category": category,
                                    "actor": actor,
                                    "asset": asset,
                                    "threat": threat,
                                    "vulnerability": vulnerability,
                                    "description": description,
                                    "risk": risk,
                                    "questionaires": questionaires})
    except Exception as e:
        raise e

    draft.update_scenario(index=scenario_index, scenario=scenario_obj)
    draft_repo.save(draft_id, draft.to_dict())

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

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
