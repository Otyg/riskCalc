from decimal import Decimal
from internal.montecarlo import MonteCarloRange
from internal.risk import RiskScenario, Risk
class DiscreetThreshold():
    def __init__(self, probability:list=[{'value':1, 'text':'Mycket låg', 'threshold': Decimal(0.1)},
                                         {'value':2, 'text':'Låg', 'threshold': Decimal(0.5)},
                                         {'value':3, 'text':'Medel', 'threshold': Decimal(1.0)},
                                         {'value':4, 'text':'Hög', 'threshold': Decimal(10.0)},
                                         {'value':5, 'text':'Mycket hög', 'threshold': Decimal(10.01)}],
                 consequence:list=[{'value':1, 'text':'Försumbar påverkan', 'threshold': Decimal(0.001)},
                                   {'value':2, 'text':'Begränsad påverkan', 'threshold': Decimal(0.005)},
                                   {'value':3, 'text':'Märkbar påverkan', 'threshold': Decimal(0.02)},
                                   {'value':4, 'text':'Allvarlig påverkan', 'threshold': Decimal(0.05)},
                                   {'value':5, 'text':'Kritisk påverkan', 'threshold': Decimal(0.051)}],
                 risk:list=[{'value': 0, 'text':'Mycket låg', 'threshold':3},
                            {'value': 0, 'text':'Låg', 'threshold':6},
                            {'value': 0, 'text':'Medel', 'threshold':10},
                            {'value': 0, 'text':'Hög', 'threshold':15},
                            {'value': 0, 'text':'Mycket hög', 'threshold':25}]):
        self.probability_values = probability
        self.consequence_values = consequence
        self.risk_values = risk

class DiscreetRisk(Risk):
    def __init__(self,tef: MonteCarloRange = MonteCarloRange(probable=Decimal(0.5)), 
                 vuln_score: MonteCarloRange = MonteCarloRange(probable=Decimal(0.1)),
                 loss_magnitude: MonteCarloRange = MonteCarloRange(probable=Decimal(0.005))
                 ):
        super().__init__(tef=tef, vuln_score=vuln_score, loss_magnitude=loss_magnitude)
        self.thresholds = DiscreetThreshold()
        self.risk = {}
        self.calculate_probability()
        self.calculate_consequence()
        self.calculate_risk()
    
    def get(self):
        return self.risk.copy()
    
    def calculate_risk(self):
        value = self.risk['probability'] * self.risk['consequence']
        self.__set_values('risk', value, self.thresholds.risk_values)
        self.risk['risk'] = value
    
    def calculate_probability(self):
        print(self.threat_event_frequency.probable)
        self.__set_values('probability', self.threat_event_frequency.probable, self.thresholds.probability_values)

    def __set_values(self, key, non_discreet_value, thresholds):
        threshold_max = max(thresholds, key=lambda x:x['threshold'])
        value = 0
        text = ""
        if non_discreet_value >= threshold_max['threshold']:
            value = threshold_max['value']
            text = threshold_max['text']
        else:
            for x in reversed(thresholds):
                if non_discreet_value <= x['threshold']:
                    value = x['value']
                    text = x['text']
        self.risk.update({key: value})
        self.risk.update({key + '_text': text})
    
    def calculate_consequence(self):
        print(self.loss_magnitude.probable)
        self.__set_values('consequence', self.loss_magnitude.probable, self.thresholds.consequence_values)