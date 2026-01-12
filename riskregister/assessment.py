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
