import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient


def _write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def _minimal_questionaire(factor: str, q_text: str, alt0_text="A0", alt1_text="A1"):
    return {
        "factor": factor,
        "calculation": "mean",
        "questions": [
            {
                "text": q_text,
                "alternatives": [
                    {
                        "text": alt0_text,
                        "weight": {"min": "0.1", "probable": "0.2", "max": "0.3"},
                    },
                    {
                        "text": alt1_text,
                        "weight": {"min": "0.4", "probable": "0.5", "max": "0.6"},
                    },
                ],
                "answer": {
                    "text": alt0_text,
                    "weight": {"min": "0.0", "probable": "0.0", "max": "0.0"},
                },
            }
        ],
    }


class TestAppScenarioEndpoints(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.tmp_root = Path(cls._tmp.name)

        def fake_user_app_root():
            return cls.tmp_root

        if "app" in sys.modules:
            del sys.modules["app"]

        cls._p1 = patch("filesystem.paths.user_app_root", new=fake_user_app_root)
        cls._p1.start()

        import app as app_module

        cls.app_module = app_module
        cls.client = TestClient(app_module.app)

        cls.data_dir = cls.tmp_root / "data"

        _write_json(cls.data_dir / "actors.json", {"actors": ["Actor 1"]})
        _write_json(cls.data_dir / "threats.json", {"threats": ["Threat 1"]})
        _write_json(
            cls.data_dir / "vulnerabilities.json", {"vulnerabilities": ["Vuln 1"]}
        )
        _write_json(cls.data_dir / "categories.json", {"categories": ["Category 1"]})
        _write_json(
            cls.data_dir / "discrete_thresholds.json", {"default_thresholds": {}}
        )

        qset = {
            "tef": _minimal_questionaire(
                "tef", "TEF Q1", alt0_text="TEF0", alt1_text="TEF1"
            ),
            "vuln": _minimal_questionaire(
                "vuln", "VULN Q1", alt0_text="V0", alt1_text="V1"
            ),
            "lm": _minimal_questionaire(
                "lm", "LM Q1", alt0_text="LM0", alt1_text="LM1"
            ),
        }
        _write_json(cls.data_dir / "questionaires" / "default.json", qset)

        from filesystem.actors_repo import JsonActorsRepository
        from filesystem.repo import (
            DiscreteThresholdsRepository,
            DraftRepository,
            JsonAnalysisRepository,
        )
        from filesystem.questionaires_repo import JsonQuestionairesRepository
        from filesystem.threats_repo import JsonThreatsRepository
        from filesystem.vulnerabilities_repo import JsonVulnerabilitiesRepository

        cls.app_module.draft_repo = DraftRepository(cls.data_dir / "drafts")
        cls.app_module.analyses_repo = JsonAnalysisRepository(cls.data_dir / "analyses")
        cls.app_module.actors_repo = JsonActorsRepository(cls.data_dir / "actors.json")
        cls.app_module.threats_repo = JsonThreatsRepository(
            cls.data_dir / "threats.json"
        )
        cls.app_module.vulnerabilities_repo = JsonVulnerabilitiesRepository(
            cls.data_dir / "vulnerabilities.json"
        )
        cls.app_module.questionaires_repo = JsonQuestionairesRepository(
            cls.data_dir / "questionaires"
        )
        cls.app_module.discrete_thresholds_repo = DiscreteThresholdsRepository(
            cls.data_dir / "discrete_thresholds.json"
        )

    @classmethod
    def tearDownClass(cls):
        cls._p1.stop()
        cls._tmp.cleanup()

    def _create_draft(self) -> str:

        r = self.client.request("GET", "/create", follow_redirects=False)
        self.assertEqual(r.status_code, 303)
        loc = r.headers["location"]
        return loc.rsplit("/", 1)[-1]

    def test_create_scenario_save_adds_scenario_and_persists_answers(self):
        draft_id = self._create_draft()

        form = {
            "name": "Scenario 1",
            "category": "Category 1",
            "actor": "Actor 1",
            "asset": "Asset 1",
            "threat": "Threat 1",
            "vulnerability": "Vuln 1",
            "description": "Desc 1",
            "risk_input_mode": "questionnaire",
            "qset": "default",
            "budget": "12345",
            "currency": "SEK",
            "q_tef_0": "1",
            "q_vuln_0": "0",
            "q_lm_0": "1",
        }
        r = self.client.post(
            f"/create/{draft_id}/scenario/save", data=form, follow_redirects=False
        )
        self.assertEqual(r.status_code, 303)

        saved = self.app_module.draft_repo.load(draft_id)
        self.assertIn("scenarios", saved)
        self.assertEqual(len(saved["scenarios"]), 1)

        scenario = saved["scenarios"][0]
        self.assertEqual(scenario["name"], "Scenario 1")
        self.assertEqual(scenario["actor"], "Actor 1")
        self.assertEqual(scenario["threat"], "Threat 1")

        q = scenario["questionaires"]
        self.assertEqual(q["tef"]["questions"][0]["answer"]["text"], "TEF1")
        self.assertEqual(q["vuln"]["questions"][0]["answer"]["text"], "V0")
        self.assertEqual(q["lm"]["questions"][0]["answer"]["text"], "LM1")

    def test_update_endpoint_updates_existing_scenario_and_answers(self):
        draft_id = self._create_draft()

        create_form = {
            "name": "Scenario 1",
            "category": "Category 1",
            "actor": "Actor 1",
            "asset": "Asset 1",
            "threat": "Threat 1",
            "vulnerability": "Vuln 1",
            "description": "Desc 1",
            "risk_input_mode": "questionnaire",
            "qset": "default",
            "budget": "100",
            "currency": "SEK",
            "q_tef_0": "0",
            "q_vuln_0": "0",
            "q_lm_0": "0",
        }
        r1 = self.client.post(
            f"/create/{draft_id}/scenario/save",
            data=create_form,
            follow_redirects=False,
        )
        self.assertEqual(r1.status_code, 303)

        update_form = {
            "name": "Scenario 1 UPDATED",
            "category": "Category 1",
            "actor": "Actor 1",
            "asset": "Asset 1",
            "threat": "Threat 1",
            "vulnerability": "Vuln 1",
            "description": "Desc UPDATED",
            "risk_input_mode": "questionnaire",
            "qset": "default",
            "budget": "999",
            "currency": "SEK",
            "q_tef_0": "1",
            "q_vuln_0": "1",
            "q_lm_0": "1",
        }
        r2 = self.client.post(
            f"/create/{draft_id}/scenario/0/update",
            data=update_form,
            follow_redirects=False,
        )
        self.assertEqual(r2.status_code, 303)

        saved = self.app_module.draft_repo.load(draft_id)
        self.assertEqual(len(saved["scenarios"]), 1)
        scenario = saved["scenarios"][0]
        self.assertEqual(scenario["name"], "Scenario 1 UPDATED")
        self.assertEqual(scenario["description"], "Desc UPDATED")

        q = scenario["questionaires"]
        self.assertEqual(q["tef"]["questions"][0]["answer"]["text"], "TEF1")
        self.assertEqual(q["vuln"]["questions"][0]["answer"]["text"], "V1")
        self.assertEqual(q["lm"]["questions"][0]["answer"]["text"], "LM1")


if __name__ == "__main__":
    unittest.main()
