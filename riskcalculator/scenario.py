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
                 questionaires: Questionaires = None
                 ):
        self.name = name
        self.actor = actor
        self.description = description
        self.asset = asset
        self.threat = threat
        self.vulnerability = vulnerability
        self.risk = risk
        self.questionaires = questionaires
        if not name:
            self.name = self.auto_desc()

    def auto_desc(self):
        return f"Risk att {self.actor} utnyttjar {self.vulnerability} för att realisera {self.threat} mot {self.asset}."

    def to_dict(self):
        return {
            "name": self.name,
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
        self.actor = dict['actor']
        self.description = dict['description']
        self.asset = dict['asset']
        self.threat = dict['threat']
        self.vulnerability = dict['vulnerability']
        if 'discrete_risk' in dict['risk']:
            risk = DiscreteRisk()
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