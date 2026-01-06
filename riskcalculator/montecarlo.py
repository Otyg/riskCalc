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
        if not (self.min <= self.probable <= self.max):
            raise ValueError(
                'Minimum is not less than or equal to probable or maximum is less than or equal to probable')

    def to_dict(self):
        return {
            "min": float(self.min),
            "probable": float(self.probable),
            "max": float(self.max)
        }

    def __repr__(self):
        return str(self.to_dict())


class MonteCarloSimulation():
    def __init__(self, range: MonteCarloRange):
        if (range.min == range.max == range.probable):
            self.probable = Decimal(range.probable)
            range.max = Decimal(range.probable*1.5)
            range.min = Decimal(range.probable/1.5)
        
        rng = np.random.default_rng()
        self.__samples = rng.triangular(left=range.min, mode=range.probable, right=range.max, size=100000)
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
        self.__samples = np.array()

    def __repr__(self):
        return str(self.to_dict())
    
    def __str__(self):
        return f"min: {str(self.min)} mode: {str(self.probable)} p90: {str(self.p90)} max: {str(self.max)}"
