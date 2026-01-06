from riskcalculator.scenario import *


class RiskAssessment():
    def __init__(self):
        self.analysis_object = str()
        self.version = float()
        self.date = str()
        self.scope = str()
        self.scenarios = list()
        self.owner = str()
    
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
            "scenarios": self.scenarios
        }
    
    def __str__(self):
        scenarios = str()
        for scenario in self.scenarios:
            scenarios += str(scenario) +"\n"
        return f"Objekt: {self.analysis_object} (Ägare: {self.owner})\nScope: {self.scope}\nVersion: {self.version} (Upprättad: {self.date})\n\n{scenarios}"