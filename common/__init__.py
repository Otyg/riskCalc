from decimal import Decimal
from riskcalculator.questionaire import Questionaires
from riskcalculator.scenario import RiskScenario
from otyg_risk_base.hybrid import HybridRisk


def get_scenario(qs=None, risk_dict=None, parameters:dict=None, discrete_thresholds_repo=None) -> RiskScenario:
    try:
        questionaires = Questionaires(
            tef=qs.get("tef"), vuln=qs.get("vuln"), lm=qs.get("lm")
        )
        values = questionaires.calculate_questionairy_values()
        values.update({"budget": Decimal(risk_dict.get("budget"))})
        values.update({"currency": risk_dict.get("currency")})
        values.update({"mappings": discrete_thresholds_repo.load().to_dict()})
        risk = HybridRisk(values=values)
        parameters.update({"risk": risk, "questionaires": questionaires})
        return RiskScenario(parameters=parameters)
    except Exception as e:
        raise e

def set_questionaire_answers(form=None, questionaires_repo=None, errors=None, qset=None, qs=None):
    if not qs:
        try:
            qs = questionaires_repo.load_objects(qset)
        except FileNotFoundError:
            errors.append(f"Kunde inte ladda questionaires-set: {qset}")
            qs = {"tef": None, "vuln": None, "lm": None}

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
    return qs