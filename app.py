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
from actors_repo import JsonActorsRepository
from repo import JsonAnalysisRepository, DraftRepository, JsonCategoryRepository
from questionaires_repo import JsonQuestionairesRepository
from riskcalculator.questionaire import Questionaires
from threats_repo import JsonThreatsRepository
from vulnerabilities_repo import JsonVulnerabilitiesRepository
from riskregister.assessment import RiskAssessment
from paths import ensure_user_data_initialized, packaged_root

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


def _validate_range(prefix: str, mn: str, pr: str, mx: str, errors: list[str]) -> None:
    dmn = _d(mn, Decimal(0))
    dpr = _d(pr, Decimal(0))
    dmx = _d(mx, Decimal(0))
    if dmn > dpr or dpr > dmx:
        errors.append(f"{prefix}: förväntar min ≤ probable ≤ max (fick {dmn}, {dpr}, {dmx})")


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
        qs = questionaires_repo.load_objects(qset)  # {"tef": Questionaire, "vuln": ..., "lm": ...}
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
def edit_scenario_page(request: Request, draft_id: str, scenario_index: int, qset: str = DEFAULT_QUESTIONAIRES_SET):
    draft = draft_repo.load(draft_id)
    scenarios = draft.get("scenarios", [])

    if scenario_index < 0 or scenario_index >= len(scenarios):
        return RedirectResponse(url=f"/create/{draft_id}", status_code=HTTP_303_SEE_OTHER)

    scenario = scenarios[scenario_index]

    threat_suggestions = threats_repo.load()
    actor_suggestions = actors_repo.load()
    vulnerability_suggestions = vulns_repo.load()
    category_suggestions = categories_repo.load()

    # questionaires-set (för att rendera frågor). qset kommer via querystring.
    try:
        qs = questionaires_repo.load_objects(qset)
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
            "qset": qset,
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

        if qs.get("tef") and hasattr(qs["tef"], "to_dict"):
            questionaires_payload = {
                "qset": qset,
                "tef": qs["tef"].to_dict(),
                "vuln": qs["vuln"].to_dict() if qs.get("vuln") else {},
                "lm": qs["lm"].to_dict() if qs.get("lm") else {},
            }
        else:
            # Minimal variant: spara bara svar-index
            questionaires_payload = {
                "qset": qset,
                "answers": {
                    dim_key: {
                        str(qi): getattr(qobj.questions[qi], "answer", None)
                        for qi in range(len(qobj.questions))
                        if isinstance(getattr(qobj.questions[qi], "answer", None), int)
                    }
                    for dim_key, qobj in qs.items()
                    if qobj is not None and hasattr(qobj, "questions")
                },
            }

    else:
        # manual mode
        def get_range(prefix: str) -> dict[str, str]:
            return {
                "min": str(_d(str(form.get(f"{prefix}_min", "0")))),
                "probable": str(_d(str(form.get(f"{prefix}_probable", "0")))),
                "max": str(_d(str(form.get(f"{prefix}_max", "0")))),
            }

        risk_dict["tef"] = get_range("tef")
        risk_dict["vuln_score"] = get_range("vuln_score")
        risk_dict["loss_magnitude"] = get_range("loss_magnitude")

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
        tef = qs.get('tef').multiply_factor()
        vuln_score = qs.get('vuln').sum_factor()
        loss_magnitude = qs.get('lm').range()
        risk = DiscreteRisk(tef=tef, vuln_score=vuln_score, loss_magnitude=loss_magnitude, budget=Decimal(risk_dict.get('budget')), currency=risk_dict.get('currency'))
        scenario_obj = RiskScenario(name=name, category=category ,actor=actor, asset=asset, threat=threat, vulnerability=vulnerability, description=description, risk=risk, questionaires=questionaires)
        scenario_json = scenario_obj.to_dict()
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
    draft = draft_repo.load(draft_id)
    scenarios = draft.get("scenarios", [])

    if scenario_index < 0 or scenario_index >= len(scenarios):
        return RedirectResponse(url=f"/create/{draft_id}", status_code=HTTP_303_SEE_OTHER)

    form = await request.form()

    # samma fält som i create
    name = str(form.get("name", "")).strip()
    category = str(form.get("category", "")).strip()
    actor = str(form.get("actor", "")).strip()
    asset = str(form.get("asset", "")).strip()
    threat = str(form.get("threat", "")).strip()
    vulnerability = str(form.get("vulnerability", "")).strip()
    description = str(form.get("description", "")).strip()
    qset = str(form.get("qset", DEFAULT_QUESTIONAIRES_SET))

    errors: list[str] = []

    risk_dict: dict[str, Any] = {
        "budget": str(_d(str(form.get("budget", "1000000")), Decimal(1000000))),
        "currency": str(form.get("currency", "SEK")) or "SEK",
    }

    questionaires_payload: dict[str, Any] = {}

    # Ladda questionaires-set och sätt svar-index
    try:
        qmap = questionaires_repo.load_objects(qset)
    except FileNotFoundError:
        qmap = {"tef": None, "vuln": None, "lm": None}
        errors.append(f"Kunde inte ladda questionaires-set: {qset}")

    for dim_key in ("tef", "vuln", "lm"):
        qobj = qmap.get(dim_key)
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

    # spara svaren minimalt (index)
    questionaires_payload = {
        "qset": qset,
        "answers": {
            dim_key: {
                str(qi): getattr(qobj.questions[qi], "answer", None)
                for qi in range(len(qobj.questions))
                if isinstance(getattr(qobj.questions[qi], "answer", None), int)
            }
            for dim_key, qobj in qmap.items()
            if qobj is not None and hasattr(qobj, "questions")
        },
    }
    if errors:
        # rendera om edit-sidan
        threat_suggestions = threats_repo.load()
        actor_suggestions = actors_repo.load()
        vulnerability_suggestions = vulns_repo.load()
        category_suggestions = categories_repo.load()
        try:
            qs = questionaires_repo.load_objects(qset)
        except FileNotFoundError:
            qs = {"tef": None, "vuln": None, "lm": None}

        return templates.TemplateResponse(
            "edit_scenario_v1.html",
            {
                "request": request,
                "draft_id": draft_id,
                "scenario_index": scenario_index,
                "scenario": scenarios[scenario_index],
                "qs": qs,
                "qset": qset,
                "available_qsets": questionaires_repo.list_sets(),
                "threat_suggestions": threat_suggestions,
                "actor_suggestions": actor_suggestions,
                "vulnerability_suggestions": vulnerability_suggestions,
                "category_suggestions": category_suggestions,
                "errors": errors,
            },
            status_code=400,
        )

    # om du vill canonicalisera via RiskScenario:
    try:
        questionaires = Questionaires(tef=qs.get('tef'), vuln=qs.get('vuln'), lm=qs.get('lm'))
        tef = qs.get('tef').multiply_factor()
        vuln_score = qs.get('vuln').sum_factor()
        loss_magnitude = qs.get('lm').range()
        risk = DiscreteRisk(tef=tef, vuln_score=vuln_score, loss_magnitude=loss_magnitude, budget=Decimal(risk_dict.get('budget')), currency=risk_dict.get('currency'))
        scenario_obj = RiskScenario(name=name, category=category ,actor=actor, asset=asset, threat=threat, vulnerability=vulnerability, description=description, risk=risk, questionaires=questionaires)
    except Exception as e:
        raise e

    draft.add_scenario(scenario=scenario_obj)
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
    p = ensure_user_data_initialized()
    os.environ["TEMPLATES_DIR"] = str(packaged_root() / "templates")
    os.environ["DATA_DIR"] = str(p["data"])
    uvicorn.run(app, host="127.0.0.1", port=8000)