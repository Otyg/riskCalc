import unittest

from riskcalculator.questionaire import Questionaires
from riskcalculator.scenario import RiskScenario
from riskregister.assessment import RiskAssessment


class TestAssessment(unittest.TestCase):
    SCENARIO_PARAMETERS = {
        "name": "Vatten",
        "actor": "Eije",
        "asset": "TV",
        "threat": "vatten",
        "vulnerability_desc": "vattenhink",
        "questionaires": Questionaires(),
        "description": "Risk att Eije utnyttjar vattenhink för att realisera vatten mot TV.",
        "threat_event_frequency": {
            "min": 0.8,
            "probable": 356.900000000001,
            "max": 500.0,
        },
        "vulnerability": {
            "min": 0.26,
            "probable": 0.41500000000000004,
            "max": 0.5700000000000001,
        },
        "loss_magnitude": {
            "min": 0.001093686365738183,
            "probable": 0.022984044092612316,
            "max": 0.06495147109509171,
            "p90": 0.050638026256677744,
        },
        "budget": 10000,
        "currency": "SEK",
    }

    def test_equality(self):
        assessment = RiskAssessment()
        self.assertTrue(assessment == assessment)
        assessment_dict = {
            "analysis_object": "foo",
            "version": 1.0,
            "date": "2026-02-02",
            "scope": "Allt",
            "owner": "Jag",
        }
        assessment_b = RiskAssessment(assessment=assessment_dict)
        self.assertFalse(assessment == assessment_b)

    def test_add_scenario(self):
        scenario = RiskScenario(parameters=self.SCENARIO_PARAMETERS)
        assessment_dict = {
            "analysis_object": "foo",
            "version": 1.0,
            "date": "2026-02-02",
            "scope": "Allt",
            "owner": "Jag",
        }
        assessment = RiskAssessment(assessment=assessment_dict)
        old_hash = assessment.__hash__()
        assessment.add_scenario(scenario=scenario)
        self.assertTrue(len(assessment.scenarios) == 1)
        self.assertNotEqual(assessment.__hash__(), old_hash)

    def test_persistence(self):
        scenario = RiskScenario(parameters=self.SCENARIO_PARAMETERS)
        assessment_dict = {
            "analysis_object": "foo",
            "version": 1.0,
            "date": "2026-02-02",
            "scope": "Allt",
            "owner": "Jag",
        }
        assessment = RiskAssessment(assessment=assessment_dict)
        assessment.add_scenario(scenario=scenario)
        assessment_b = RiskAssessment(assessment=assessment.to_dict())
        self.assertTrue(assessment == assessment_b)


if __name__ == "__main__":
    unittest.main()
