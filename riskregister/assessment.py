from riskcalculator.scenario import *


class RiskAssessment():
    def __init__(self, assessment:dict = None):
        self.summary = {'critical': 0, 'high':0, 'middle': 0, 'low': 0, 'very_low':0}
        self.scenarios = list()
        if assessment: 
            self.analysis_object = assessment["analysis_object"]
            self.version = assessment["version"]
            self.date = assessment["date"]
            self.scope = assessment["scope"]
            self.owner = assessment["owner"]
            for scenario in assessment["scenarios"]:
                base_scenario = RiskScenario()
                base_scenario.from_dict(scenario)
                self.add_scenario(base_scenario)
        else:
            self.analysis_object = str()
            self.version = float()
            self.date = str()
            self.scope = str()
            self.owner = str()
    
    def add_scenario(self, scenario:RiskScenario):
        self.scenarios.append(scenario)
        risk = scenario.risk
        if isinstance(risk, DiscreteRisk):
            self.summary[risk.risk['level']] += 1

    def update_scenario(self, index:int, scenario:RiskScenario):
        old_scenario = self.scenarios[index]
        risk = old_scenario.risk
        if isinstance(risk, DiscreteRisk):
            self.summary[risk.risk['level']] -= 1
        self.scenarios[index] = scenario
        risk = scenario.risk
        if isinstance(risk, DiscreteRisk):
            self.summary[risk.risk['level']] += 1

    def to_dict(self):
        scenarios_as_dicts = []
        for scenario in self.scenarios:
            scenarios_as_dicts.append(scenario.to_dict())
        return {
            "analysis_object": self.analysis_object,
            "version": self.version,
            "date": self.date,
            "scope": self.scope,
            "owner": self.owner,
            "scenarios": scenarios_as_dicts,
            "summary": self.summary
        }
    
    def __str__(self):
        scenarios = str()
        for scenario in self.scenarios:
            scenarios += str(scenario) +"\n"
        return f"Objekt: {self.analysis_object} (Ägare: {self.owner})\nScope: {self.scope}\nVersion: {self.version} (Upprättad: {self.date})\n\n{scenarios}"