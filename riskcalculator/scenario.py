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
    def __init__(self, parameters:dict = None):
        if not parameters:
            self.actor = ""
            self.description = ""
            self.asset = ""
            self.threat = ""
            self.vulnerability = ""
            self.risk = Risk()
            self.category = ""
            self.name = ""
            self.questionaires = Questionaires(tef=Questionaire(factor="tef"), vuln=Questionaire(factor="vuln"), lm=Questionaire(factor="lm"))
        else:
            self.actor = parameters.get('actor', "")
            self.description = parameters.get('description', "")
            self.asset = parameters.get('asset', "")
            self.threat = parameters.get('threat', "")
            self.vulnerability = parameters.get('vulnerability', "")
            self.risk = parameters.get('risk')
            self.category = parameters.get('category', "")
            self.name = parameters.get('name', self.auto_desc())
            tmp_risk = parameters.get('risk', Risk())
            if isinstance(tmp_risk, dict):
                if 'discrete_risk' in tmp_risk:
                    self.risk = DiscreteRisk(tmp_risk)
                else:
                    self.risk = Risk(tmp_risk)
            else:
                self.risk = tmp_risk
            if parameters.get('questionaires') and isinstance(parameters.get('questionaires'), Questionaires):
                self.questionaires = parameters.get('questionaires')
            elif parameters.get('questionaires'):
                tef = Questionaire(factor=parameters.get('questionaires').get('tef').get('factor', "tef"))
                tef.from_dict(parameters.get('questionaires').get('tef', Questionaire()))
                vuln = Questionaire(factor=parameters.get('questionaires').get('vuln').get('factor', "vuln"))
                vuln.from_dict(parameters.get('questionaires').get('vuln', Questionaire()))
                lm = Questionaire(factor=parameters.get('questionaires').get('lm').get('factor', "lm"))
                tef.from_dict(parameters.get('questionaires').get('lm', Questionaire()))
                questionaires = Questionaires(tef=tef, vuln=vuln, lm=lm)
                self.questionaires = questionaires
            else:
                self.questionaires = Questionaires(tef=Questionaire(factor="tef"), vuln=Questionaire(factor="vuln"), lm=Questionaire(factor="lm"))

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
    
    def from_dict(self, dict:dict=None):
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
