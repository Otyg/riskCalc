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

from riskcalculator.discret_scale import DiscreteRisk
from riskcalculator.questionaire import Questionaire, Questionaires
from riskcalculator.risk import Risk


class RiskScenario():
    def __init__(self, name: str = "",
                 actor: str = "",
                 description: str = "",
                 asset: str = "",
                 threat: str = "",
                 vulnerability: str = "",
                 risk: Risk = None,
                 questionaires: Questionaires = None,
                 category: str = ""
                 ):
        self.name = name
        self.actor = actor
        self.description = description
        self.asset = asset
        self.threat = threat
        self.vulnerability = vulnerability
        self.risk = risk
        self.questionaires = questionaires
        self.category = category
        if not name:
            self.name = self.auto_desc()

    def auto_desc(self):
        return f"Risk att {self.actor} utnyttjar {self.vulnerability} för att realisera {self.threat} mot {self.asset}."

    def to_dict(self):
        return {
            "name": self.name,
            "category": self.category,
            "actor": self.actor,
            "asset": self.asset,
            "threat": self.threat,
            "vulnerability": self.vulnerability,
            "description": self.description,
            "risk": self.risk.to_dict(),
            "questionaires": self.questionaires.to_dict()
        }
    
    def from_dict(self, dict:dict={}):
        self.name = dict['name']
        self.category = dict['category']
        self.actor = dict['actor']
        self.description = dict['description']
        self.asset = dict['asset']
        self.threat = dict['threat']
        self.vulnerability = dict['vulnerability']
        if 'discrete_risk' in dict['risk']:
            risk = DiscreteRisk(dict['risk'])
        else:
            risk = Risk()
            risk.from_dict(dict['risk'])
        self.risk = risk
        tef = Questionaire(factor=dict['questionaires']['tef']['factor'])
        tef.from_dict(dict['questionaires']['tef'])
        vuln = Questionaire(factor=dict['questionaires']['vuln']['factor'])
        vuln.from_dict(dict['questionaires']['vuln'])
        lm = Questionaire(factor=dict['questionaires']['lm']['factor'])
        lm.from_dict(dict['questionaires']['lm'])
        questionaires = Questionaires(tef=tef, vuln=vuln, lm=lm)
        self.questionaires = questionaires

    def __str__(self):
        short = self.name + "\n" + self.description + "\n"
        short += str(self.risk)
        return short

    def __repr__(self):
        return str(self.to_dict())
