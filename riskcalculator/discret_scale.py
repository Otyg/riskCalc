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

from decimal import Decimal
from riskcalculator.montecarlo import MonteCarloRange
from riskcalculator.risk import Risk
class DiscreetThreshold():
    def __init__(self, probability:list=[{'value':1, 'text':'Mycket låg', 'threshold': float(0.1)},
                                         {'value':2, 'text':'Låg', 'threshold': float(0.5)},
                                         {'value':3, 'text':'Medel', 'threshold': float(8.0)},
                                         {'value':4, 'text':'Hög', 'threshold': float(13.0)},
                                         {'value':5, 'text':'Mycket hög', 'threshold': float(13.01)}],
                 consequence:list=[{'value':1, 'text':'Försumbar påverkan', 'threshold': float(0.001)},
                                   {'value':2, 'text':'Begränsad påverkan', 'threshold': float(0.005)},
                                   {'value':3, 'text':'Märkbar påverkan', 'threshold': float(0.02)},
                                   {'value':4, 'text':'Allvarlig påverkan', 'threshold': float(0.05)},
                                   {'value':5, 'text':'Kritisk påverkan', 'threshold': float(0.051)}],
                 risk:list=[{'value': 'very_low', 'text':'Mycket låg', 'threshold':3},
                            {'value': 'low', 'text':'Låg', 'threshold':6},
                            {'value': 'middle', 'text':'Medel', 'threshold':10},
                            {'value': 'high', 'text':'Hög', 'threshold':15},
                            {'value': 'critical', 'text':'Mycket hög', 'threshold':25}]):
        self.probability_values = probability
        self.consequence_values = consequence
        self.risk_values = risk

    def to_dict(self):
        return {
            "probability": self.probability_values,
            "consequence": self.consequence_values,
            "risk": self.risk_values
        }

class DiscreteRisk(Risk):
    def __init__(self,tef: MonteCarloRange = MonteCarloRange(probable=float(0.5)), 
                 vuln_score: MonteCarloRange = MonteCarloRange(probable=float(0.1)),
                 loss_magnitude: MonteCarloRange = MonteCarloRange(probable=float(0.005)),
                 budget: Decimal=Decimal(1), currency:str="SEK"
                 ):
        super().__init__(tef=tef, vuln_score=vuln_score, loss_magnitude=loss_magnitude, budget=budget, currency=currency)
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
        self.__set_values('probability', self.loss_event_frequency.p90, self.thresholds.probability_values)

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
        if key=="risk":
            self.risk.update({'level': value})
        self.risk.update({key: value})
        self.risk.update({key + '_text': text})
        
    
    def calculate_consequence(self):
        self.__set_values('consequence', self.loss_magnitude.p90, self.thresholds.consequence_values)

    def to_dict(self):
        me = super().to_dict()
        me.update({"discrete_risk": self.risk})
        me.update({"thresholds": self.thresholds.to_dict()})
        return me


    def from_dict(self, dict:dict={}):
        super().from_dict(dict=dict)
        thresholds = DiscreetThreshold(probability=dict["thresholds"]["probability"], consequence=dict["thresholds"]["consequence"], risk=dict["thresholds"]["risk"])
        self.thresholds = thresholds
        self.risk = dict["discrete_risk"]
    
    def __repr__(self):
        return str(self.to_dict())
    
    def __str__(self):
        return f"Sannolikhet: {str(self.risk['probability'])} ({self.risk['probability_text']})\nKonsekvens: {str(self.risk['consequence'])} ({self.risk['consequence_text']})\nRisk: {str(self.risk['risk'])} ({self.risk['risk_text']})"
