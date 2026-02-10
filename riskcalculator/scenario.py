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

from riskcalculator.questionaire import Questionaire, Questionaires
from otyg_risk_base.hybrid import HybridRisk
from .util import freeze


class RiskScenario:
    def __init__(self, parameters: dict = None):
        if not parameters:
            self.actor = ""
            self.description = ""
            self.asset = ""
            self.threat = ""
            self.vulnerability = ""
            self.risk = None
            self.category = ""
            self.name = ""
            self.questionaires = None
        else:
            self.actor = parameters.get("actor", "")
            self.description = parameters.get("description", "")
            self.asset = parameters.get("asset", "")
            self.threat = parameters.get("threat", "")
            self.vulnerability = parameters.get("vulnerability_desc", "")
            self.risk = parameters.get("risk", HybridRisk())
            self.category = parameters.get("category", "")
            self.name = parameters.get("name", self.auto_desc())
            if self.name == "":
                self.name = self.auto_desc()
            if parameters.get("questionaires") and isinstance(
                parameters.get("questionaires"), Questionaires
            ):
                self.questionaires = parameters.get("questionaires")
            elif parameters.get("questionaires"):
                tef = Questionaire(
                    factor=parameters.get("questionaires")
                    .get("tef")
                    .get("factor", "tef")
                )
                tef.from_dict(
                    parameters.get("questionaires").get("tef", Questionaire())
                )
                vuln = Questionaire(
                    factor=parameters.get("questionaires")
                    .get("vuln")
                    .get("factor", "vuln")
                )
                vuln.from_dict(
                    parameters.get("questionaires").get("vuln", Questionaire())
                )
                lm = Questionaire(
                    factor=parameters.get("questionaires").get("lm").get("factor", "lm")
                )
                tef.from_dict(parameters.get("questionaires").get("lm", Questionaire()))
                questionaires = Questionaires(tef=tef, vuln=vuln, lm=lm)
                self.questionaires = questionaires
            else:
                self.questionaires = Questionaires(
                    tef=Questionaire(factor="tef"),
                    vuln=Questionaire(factor="vuln"),
                    lm=Questionaire(factor="lm"),
                )

    def auto_desc(self):
        return f"Risk att {self.actor} utnyttjar {self.vulnerability} för att realisera {self.threat} mot {self.asset}."

    def to_dict(self):
        return {
            "name": self.name,
            "category": self.category,
            "actor": self.actor,
            "asset": self.asset,
            "threat": self.threat,
            "vulnerability_desc": self.vulnerability,
            "description": self.description,
            "risk": self.risk.to_dict(),
            "questionaires": self.questionaires.to_dict(),
        }

    @classmethod
    def from_dict(cls, dict: dict = None):
        new = RiskScenario()
        new.name = dict.get("name", "")
        new.category = dict.get("category", "")
        new.actor = dict.get("actor", "")
        new.asset = dict.get("asset", "")
        new.threat = dict.get("threat", "")
        new.vulnerability = dict.get("vulnerability_desc", "")
        new.description = dict.get("description")
        new.risk = HybridRisk.from_dict(values=dict.get("risk", {}))
        new.questionaires = Questionaires.from_dict(dict.get("questionaires"))
        return new

    def __str__(self):
        short = self.name + "\n" + self.description + "\n"
        short += str(self.risk)
        return short

    def __repr__(self):
        return str(self.to_dict())

    def __hash__(self):
        return hash(
            (
                self.actor,
                self.description,
                self.asset,
                self.threat,
                freeze(self.vulnerability),
                self.category,
                self.name,
                self.risk.__hash__(),
                self.questionaires.__hash__(),
            )
        )

    def __eq__(self, value):
        return self.__hash__() == value.__hash__()
