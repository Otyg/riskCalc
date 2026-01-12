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

from riskcalculator.montecarlo import *
from decimal import *


class Risk():
    def __init__(self, tef: MonteCarloRange = MonteCarloRange(probable=Decimal(0.5)),
                 vuln_score: MonteCarloRange = MonteCarloRange(
                     probable=Decimal(0.1)),
                 loss_magnitude: MonteCarloRange = MonteCarloRange(
                     probable=Decimal(0.001)),
                 budget: Decimal=Decimal(1000000),
                 currency: str="SEK"
                 ):
        self.threat_event_frequency = tef
        self.vuln_score = vuln_score
        self.loss_magnitude = MonteCarloSimulation(loss_magnitude)
        self.budget = budget
        self.currency = currency
        self.loss_event_frequency = MonteCarloSimulation(MonteCarloRange(min=self.threat_event_frequency.min*self.vuln_score.min,
                                                    max=self.threat_event_frequency.max*self.vuln_score.max,
                                                    probable=self.threat_event_frequency.probable*self.vuln_score.probable))
        self.update_ale()

    def update_ale(self):
        self.ale = MonteCarloRange(min=self.budget*self.loss_event_frequency.min*self.loss_magnitude.min,
                                   max=self.budget*self.loss_event_frequency.max*self.loss_magnitude.max,
                                   probable=self.budget*self.loss_event_frequency.probable*self.loss_magnitude.probable)
        self.annual_loss_expectancy = MonteCarloSimulation(self.ale)

    def to_dict(self):
        return {
            "threat_event_frequency": self.threat_event_frequency.to_dict(),
            "vulnerability": self.vuln_score.to_dict(),
            "loss_event_frequency": self.loss_event_frequency.to_dict(),
            "loss_magnitude": self.loss_magnitude.to_dict(),
            "annual_loss_expectancy": self.annual_loss_expectancy.to_dict(),
            "budget": float(self.budget),
            "currency": self.currency
        }

    def from_dict(self, dict:dict={}):
        self.budget = Decimal(dict['budget'])
        self.currency = dict['currency']
        self.threat_event_frequency = MonteCarloRange(min=dict['threat_event_frequency']['min'], probable=dict['threat_event_frequency']['probable'], max=dict['threat_event_frequency']['max'])
        self.vuln_score = MonteCarloRange(min=dict['vulnerability']['min'], probable=dict['vulnerability']['probable'], max=dict['vulnerability']['max'])
        self.loss_event_frequency = MonteCarloRange(min=dict['loss_event_frequency']['min'], probable=dict['loss_event_frequency']['probable'], max=dict['loss_event_frequency']['max'])
        self.loss_magnitude = MonteCarloRange(min=dict['loss_magnitude']['min'], probable=dict['loss_magnitude']['probable'], max=dict['loss_magnitude']['max'])
        self.ale = MonteCarloRange(min=self.loss_event_frequency.min*self.loss_magnitude.min,
                                   max=self.loss_event_frequency.max*self.loss_magnitude.max,
                                   probable=self.loss_event_frequency.probable*self.loss_magnitude.probable)
        tmp_ale = MonteCarloSimulation(MonteCarloRange(probable=1))
        tmp_ale.from_dict(dict['annual_loss_expectancy'])
        self.annual_loss_expectancy = tmp_ale
    
    def __repr__(self):
        return str(self.to_dict())
    
    def __str__(self):
        return str("ALE (p90): " + str(round(self.annual_loss_expectancy.p90, 2)) + f" {self.currency}/år\nALE (p50): " + str(round(self.annual_loss_expectancy.probable, 2)) + f" {self.currency}/år\n")
