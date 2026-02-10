import unittest

from riskcalculator.questionaire import Questionaires
from riskcalculator.scenario import RiskScenario

class TestScenario(unittest.TestCase):
    DEFAULT_PARAMETERS = {
            "name": "Vatten",
            "actor": "Eije",
            "asset": "TV",
            "threat": "vatten",
            "vulnerability_desc": "vattenhink",
            "description": "Risk att Eije utnyttjar vattenhink för att realisera vatten mot TV.",
            "threat_event_frequency": {
                "min": 316.8, "probable": 4428.900000000001,"max": 8541.0
            },
            "vulnerability": {
                "min": 0.26, "probable": 0.41500000000000004, "max": 0.5700000000000001
            },
            "loss_magnitude": {
                "min": 0.001093686365738183, "probable": 0.022984044092612316, 
                "max": 0.06495147109509171, "p90": 0.050638026256677744
            },
            'budget': 10000, 'currency':"SEK",
        }
    SECOND_PARAMETER_SET = {
            "name": "Vatten",
            "actor": "Eije",
            "asset": "TV",
            "threat": "vatten",
            "vulnerability_desc": "vattenhink",
            "questionaires": Questionaires(),
            "description": "Risk att Eije utnyttjar vattenhink för att realisera vatten mot TV.",
            "threat_event_frequency": {
                "min": 0.8, "probable": 356.900000000001,"max": 500.0
            },
            "vulnerability": {
                "min": 0.26, "probable": 0.41500000000000004, "max": 0.5700000000000001
            },
            "loss_magnitude": {
                "min": 0.001093686365738183, "probable": 0.022984044092612316, 
                "max": 0.06495147109509171, "p90": 0.050638026256677744
            },
            'budget': 10000, 'currency':"SEK",
        }
    def test_equality(self):
        scenario = RiskScenario()
        self.assertTrue(scenario == scenario)
        scenario_mod = RiskScenario(parameters={'actor': 'meh'})
        self.assertFalse(scenario == scenario_mod)
    
    def test_construktor(self):
        scenario = RiskScenario(parameters=self.DEFAULT_PARAMETERS)
        empty_scenario = RiskScenario()
        self.assertIsNotNone(scenario)
        self.assertFalse(scenario.auto_desc is None)
        self.assertTrue(scenario == scenario)
        self.assertTrue(scenario != empty_scenario)

    def test_persistence(self):
        scenario = RiskScenario(parameters=self.DEFAULT_PARAMETERS)
        self.assertTrue(scenario == RiskScenario.from_dict(scenario.to_dict()))
        
        scenario2 = RiskScenario(parameters=self.SECOND_PARAMETER_SET)
        self.assertFalse(scenario == scenario2)
        

if __name__ == '__main__':
    unittest.main()
