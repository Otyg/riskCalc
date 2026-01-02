from montecarlo import *
from decimal import *


class RiskScenario:
    def __init__(self, name:str="", actor:str="", description:str="", asset:str="", threat:str="", vulnerability:str="",
                 tef:MonteCarloRange = MonteCarloRange(probable=Decimal(0.5)),
                 vuln_score:MonteCarloRange  = MonteCarloRange(probable=Decimal(0.1)),
                 loss_magnitude:MonteCarloRange = MonteCarloRange(probable=Decimal(10000))
                 ):
        self.name = name
        self.actor = actor
        self.description = description
        self.asset = asset
        self.threat = threat
        self.vulnerability = vulnerability
        self.risk = Risk(tef=tef, vuln_score=vuln_score, loss_magnitude=loss_magnitude)
        if not description:
            self.auto_desc()

    def auto_desc(self):
        self.description = f"Risk att {self.actor} utnyttjar {self.vulnerability} för att realisera {self.threat} mot {self.asset}."


class Risk:
    def __init__(self, tef:MonteCarloRange = MonteCarloRange(probable=Decimal(0.5)),
                 vuln_score:MonteCarloRange  = MonteCarloRange(probable=Decimal(0.1)),
                 loss_magnitude:MonteCarloRange = MonteCarloRange(probable=Decimal(10000))
                 ):
        self.threat_event_frequency = tef
        self.vuln_score = vuln_score
        self.loss_magnitude = loss_magnitude
        self.loss_event_frequency = MonteCarloRange(min=self.threat_event_frequency.min*self.vuln_score.min,
                              max=self.threat_event_frequency.max*self.vuln_score.max,
                              probable=self.threat_event_frequency.probable*self.vuln_score.probable)
        self.update_ale()

    def update_ale(self):
        ale = MonteCarloRange(min=self.loss_event_frequency.min*self.loss_magnitude.min,
                              max=self.loss_event_frequency.max*self.loss_magnitude.max,
                              probable=self.loss_event_frequency.probable*self.loss_magnitude.probable)
        self.annual_loss_expectancy = MonteCarloSimulation(ale)