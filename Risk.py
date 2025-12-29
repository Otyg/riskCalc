from internal.montecarlo import MonteCarloSimulation
from decimal import *


class Risk:
    def __init__(self, name="", actor="", description="", asset="", threat="", vulnerability="",
                 tef={'max': Decimal(1.00), 'min': Decimal(0.00)},
                 vuln_score={'max': Decimal(1.00), 'min': Decimal(0.00)},
                 loss_magnitude={'max': Decimal(1.00), 'min': Decimal(0.00)}
                 ):
        self.name = name
        self.actor = actor
        self.description = description
        self.asset = asset
        self.threat = threat
        self.vulnerability = vulnerability
        self.threat_event_frequency = MonteCarloSimulation(
            high=tef['max'], low=tef['min'])
        self.vuln_score = MonteCarloSimulation(
            high=vuln_score['max'], low=vuln_score['min'])
        self.loss_magnitude = MonteCarloSimulation(
            high=loss_magnitude['max'], low=loss_magnitude['min'])
        self.update_lef()
        self.update_ale() # Kanske bara ALE som ska vara simulering?

    def auto_desc(self):
        self.description = f"Risk att {self.actor} utnyttjar {self.vulnerability} för att realisera {self.threat} mot {self.asset}."

    def update_lef(self):
        self.loss_event_frequency = MonteCarloSimulation(
            high=self.threat_event_frequency.max*self.vuln_score.max, low=self.threat_event_frequency.min*self.vuln_score.min)
        self.update_ale()

    def update_ale(self):
        self.annual_loss_expectancy = MonteCarloSimulation(high=self.loss_event_frequency.max*self.loss_magnitude.max, low=self.loss_event_frequency.min *
                                                           self.loss_magnitude.min, probable=self.loss_event_frequency.probable*self.loss_magnitude.probable)