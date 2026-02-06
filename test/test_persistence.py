from __future__ import annotations

import tempfile
import shutil
from pathlib import Path
import unittest

from filesystem.questionaires_repo import JsonQuestionairesRepository
from filesystem.repo import DiscreteThresholdsRepository, JsonAnalysisRepository
from otyg_risk_base.qualitative_scale import QualitativeScale

from riskcalculator.questionaire import Questionaire

class TestPersistence(unittest.TestCase):
    def setUp(self):
        self.packaged_root = Path(__file__).parent.parent
        self.user_app_root = tempfile.TemporaryDirectory()
        root = Path(str(self.user_app_root))
        data_dir = root / "data"
        analyses_dir = data_dir / "analyses"
        drafts_dir = data_dir / "drafts"
        questionaires_dir = data_dir / "questionaires"

        analyses_dir.mkdir(parents=True, exist_ok=True)
        drafts_dir.mkdir(parents=True, exist_ok=True)
        questionaires_dir.mkdir(parents=True, exist_ok=True)

        # Seed-källa (paketerad)
        seed_data_dir = self.packaged_root / "data"
        seed_questionaires_dir = seed_data_dir / "questionaires"

        # Kopiera listfiler om de saknas
        for filename in ["actors.json", "threats.json", "vulnerabilities.json", "categories.json", "discrete_thresholds.json"]:
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

        self.paths= {
            "root": root,
            "data": data_dir,
            "analyses": analyses_dir,
            "drafts": drafts_dir,
            "questionaires": questionaires_dir,
            "actors_json": data_dir / "actors.json",
            "threats_json": data_dir / "threats.json",
            "vulnerabilities_json": data_dir / "vulnerabilities.json",
            "discrete_thresholds.json": data_dir / "discrete_thresholds.json",
        }
    
    def tearDown(self):
        self.user_app_root.cleanup()

    def test_qualitative_mappings_repo(self):
        repo = DiscreteThresholdsRepository(path=self.paths.get("discrete_thresholds.json"))
        self.assertIn("default_thresholds", repo.get_set_names())
        self.assertIsInstance(repo.load(), QualitativeScale)
    
    def test_questionaires_repo(self):
        repo = JsonQuestionairesRepository(folder=self.paths.get("questionaires"))
        self.assertIsInstance(repo.load_objects(repo.list_sets()[0]).get("tef"), Questionaire)
