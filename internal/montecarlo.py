import numpy as np
from decimal import *

class MonteCarloRange:
    def __init__(self, min:Decimal=Decimal(0.00), probable:Decimal=Decimal(0.00), max:Decimal=Decimal(0.00)):
        self.max = Decimal(max)
        self.min = Decimal(min)
        self.probable = Decimal(probable)
        if not self.probable.is_zero() and (self.max == self.min):
            self.max = Decimal(self.probable*2)
            self.min = Decimal(self.probable/2)
        elif self.probable.is_zero and not self.max.is_zero():
            self.probable = (self.min + self.max)/2
        if not (self.min <= self.probable <= self.max):
            raise ValueError('Minimum is not less than or equal to probable or maximum is less than or equal to probable')
    
    def __repr__(self):
        return str({"min":self.min, "probable":self.probable, "max": self.max})

class MonteCarloSimulation:
    def __init__(self, range: type[MonteCarloRange]):
        if not (range.min == range.max == range.probable):
            rng = np.random.default_rng()
            self.__samples = rng.triangular(left=range.min, mode=range.probable, right=range.max, size=1000000)
            self.probable = Decimal(np.mean(self.__samples))
            self.max = Decimal(np.max(self.__samples))
            self.min = Decimal(np.min(self.__samples))
        else:
            self.probable = Decimal(range.probable)
            self.max = Decimal(range.probable)
            self.min = Decimal(range.probable)
    
    def __repr__(self):
        return str({"min": self.min, "probable": self.probable, "max": self.max})

