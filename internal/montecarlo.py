import numpy as np
import statistics
from decimal import *


class MonteCarloRange:
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
            "min": self.min,
            "probable": self.probable,
            "max": self.max
        }

    def __repr__(self):
        return str(self.to_dict())


class MonteCarloSimulation:
    def __init__(self, range: MonteCarloRange):
        if (range.min == range.max == range.probable):
            self.probable = Decimal(range.probable)
            self.max = Decimal(range.probable*1.5)
            self.min = Decimal(range.probable/1.5)
        
        rng = np.random.default_rng()
        self.__samples = rng.triangular(left=range.min, mode=range.probable, right=range.max, size=100000)
        self.probable = Decimal(statistics.mode(self.__samples))
        self.max = Decimal(np.max(self.__samples))
        self.min = Decimal(np.min(self.__samples))

    def to_dict(self):
        return {
            "min": self.min,
            "probable": self.probable,
            "max": self.max,
            "samples": self.__samples
        }
    def __repr__(self):
        return str(self.to_dict())
