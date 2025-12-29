import numpy as np
from decimal import *

class MonteCarloSimulation:
    def __init__(self, high = Decimal(0.00), low = Decimal(0.00), probable = Decimal(0.00)):
        self.__high = Decimal(high)
        self.__low = Decimal(low)
        self.__probable = Decimal(probable)
        if not self.__probable.is_zero():
            if self.__high < self.__probable:
                self.__high = 2 * probable
        elif self.__probable.is_zero and not self.__high.is_zero():
            self.__probable = (self.__low + self.__high)/2
        if (self.__low == self.__high) or not (self.__low <= self.__probable <= self.__high):
            self.probable = self.__probable
            self.max = self.__high
            self.min = self.__low
        else:
            rng = np.random.default_rng()
            self.__samples = rng.triangular(left=self.__low, mode=self.__probable, right=self.__high, size=1000000)
            self.probable = Decimal(np.mean(self.__samples))
            self.max = Decimal(np.max(self.__samples))
            self.min = Decimal(np.min(self.__samples))