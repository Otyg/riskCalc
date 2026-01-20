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

import numpy as np
import statistics
from decimal import *


class MonteCarloRange():
    def __init__(self, min: Decimal = Decimal(0.00), probable: Decimal = Decimal(0.00), max: Decimal = Decimal(0.00)):
        self.max = Decimal(max)
        self.min = Decimal(min)
        self.probable = Decimal(probable)
        if not self.probable.is_zero() and (self.max == self.min):
            self.max = Decimal(self.probable*2)
            self.min = Decimal(self.probable/2)
        elif self.probable.is_zero and not self.max.is_zero():
            self.probable = (self.min + self.max)/2

    def to_dict(self):
        return {
            "min": float(self.min),
            "probable": float(self.probable),
            "max": float(self.max)
        }
    
    def add(self, other = None):
        max = self.max + other.max
        min = self.min + other.min
        probable = self.probable + other.probable
        result = MonteCarloRange(min=Decimal(min), probable=Decimal(probable), max=Decimal(max))
        return result

    def __repr__(self):
        return str(self.to_dict())

class PertDistribution():
    def __init__(self,range: MonteCarloRange):
        rng = np.random.default_rng()
        delta_min_max = range.max - range.min
        alpha = 1 + ((range.probable - range.min) * 4) / delta_min_max
        beta = 1 + ((range.max - range.probable) * 4) / delta_min_max
        self.__samples = float(range.min) + rng.beta(alpha, beta, 100000) * float(delta_min_max)

    def get(self):
        return self.__samples.copy()


class MonteCarloSimulation():
    def __init__(self, range: MonteCarloRange):
        if (range.min == range.max == range.probable):
            self.probable = Decimal(range.probable)
            range.max = Decimal(Decimal(range.probable)+Decimal(0.000000000001))
            range.min = Decimal(Decimal(range.probable)-Decimal(0.000000000001))
        
        pd = PertDistribution(range=range)
        self.__samples = pd.get()
        self.probable = Decimal(statistics.mode(self.__samples))
        self.p90 = Decimal(np.percentile(self.__samples, 90))
        self.max = Decimal(np.max(self.__samples))
        self.min = Decimal(np.min(self.__samples))

    def to_dict(self):
        return {
            "min": float(self.min),
            "probable": float(self.probable),
            "max": float(self.max),
            "p90": float(self.p90)
        }
    
    def from_dict(self, dict:dict={}):
        self.min = Decimal(dict['min'])
        self.probable = Decimal(dict['probable'])
        self.max = Decimal(dict['max'])
        self.p90 = Decimal(dict['p90'])
        self.__samples = np.array([])

    def __repr__(self):
        return str(self.to_dict())
    
    def __str__(self):
        return f"min: {str(self.min)} mode: {str(self.probable)} p90: {str(self.p90)} max: {str(self.max)}"
