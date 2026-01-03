import statistics
from decimal import Decimal
from .montecarlo import MonteCarloRange


class Alternative:
    def __init__(self, text: str = "", weight: MonteCarloRange = MonteCarloRange(probable=0.5)):
        self.text = text
        self.weight = weight


class Question:
    def __init__(self, text: str = "", alternatives: list = []):
        self.text = text
        self.alternatives = alternatives
        self.answer = ""

    def add(self, alternative: Alternative = Alternative()):
        self.alternatives.append(alternative)

    def get(self, index: int = 0):
        return self.alternatives[index]

    def get_alternatives(self):
        return self.alternatives.copy()

    def set_answer(self, answer: int = -1):
        self.answer = self.alternatives[int(answer)]


class Questionaire:
    def __init__(self, factor: str = "", questions: list = []):
        self.factor = factor
        self.questions = questions
        self.factor_sum = MonteCarloRange(probable=0.5)

    def append_question(self, question: Question = Question()):
        self.questions.append(question)

    def sum_factor(self):
        max = 0
        min = 0
        mode = 0
        for q in self.questions:
            max += q.answer.weight.max
            min += q.answer.weight.min
            mode += q.answer.weight.probable
        self.factor_sum = MonteCarloRange(min=min, max=max, probable=mode)
        return self.factor_sum

    def multiply_factor(self):
        max = min = mode = 1
        for q in self.questions:
            max *= q.answer.weight.max
            min *= q.answer.weight.min
            mode *= q.answer.weight.probable
        self.factor_mul = MonteCarloRange(min=min, max=max, probable=mode)
        return self.factor_mul

    def max(self):
        factor_max = self.questions[0].answer.weight.max
        for q in self.questions:
            if factor_max < q.answer.weight.max:
                factor_max = q.answer.weight.max
        return Decimal(factor_max)

    def min(self):
        factor_min = self.questions[0].answer.weight.min
        for q in self.questions:
            if factor_min > q.answer.weight.min:
                factor_min = q.answer.weight.min
        return Decimal(factor_min)

    def mean(self):
        return MonteCarloRange(min=self.factor_sum.min/len(self.questions), max=self.factor_sum.max/len(self.questions), probable=self.factor_sum.probable/len(self.questions))
