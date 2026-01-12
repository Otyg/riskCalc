from decimal import Decimal
import statistics
from .montecarlo import MonteCarloRange


class Alternative():
    def __init__(self, text: str = "", weight: MonteCarloRange = MonteCarloRange(probable=0.5)):
        self.text = text
        self.weight = weight
    
    def to_dict(self):
        return {
            "text": self.text,
            "weight": self.weight.to_dict()
        }

    def __repr__(self):
        return str(self.to_dict())

class Question():
    def __init__(self, text: str = "", alternatives: list = []):
        self.text = text
        self.alternatives = alternatives
        self.answer = Alternative()

    def to_dict(self):
        alternatives = []
        for a in self.alternatives:
            alternatives.append(a.to_dict())
        return {
            "text": self.text,
            "alternatives": alternatives,
            "answer": self.answer.to_dict()
        }

    def __repr__(self):
        return str(self.to_dict())

    def add(self, alternative: Alternative = Alternative()):
        self.alternatives.append(alternative)

    def get(self, index: int = 0):
        return self.alternatives[index]

    def get_alternatives(self):
        return self.alternatives.copy()

    def set_answer(self, answer):
        if isinstance(answer, str):
            self.answer = self.alternatives[int(answer)]
        elif isinstance(answer, int):
            self.answer = self.alternatives[answer]
        elif isinstance(answer, Alternative):
            self.answer = answer


class Questionaire():
    def __init__(self, factor: str="", questions: list = None):
        if questions is None:
            self.questions = []
        else:
            self.questions = list(questions)
        self.factor = factor
        self.factor_mul = MonteCarloRange(probable=0.5)
        self.factor_sum = MonteCarloRange(probable=0.5)

    def to_dict(self):
        questions = []
        for q in self.questions:
            questions.append(q.to_dict())
        return {
            "factor": self.factor,
            "questions": questions,
            "factor_mul": self.factor_mul.to_dict(),
            "factor_sum": self.factor_sum.to_dict()
        }

    def from_dict(self, dict:dict={}):
        self.factor = dict['factor']

        questions = []
        for q in dict['questions']:
            alternatives = []
            for a in q['alternatives']:
                alternatives.append(Alternative(text=a['text'], weight=MonteCarloRange(min=Decimal(a['weight']['min']), max=Decimal(a['weight']['max']), probable=Decimal(a['weight']['probable']))))
            question = Question(q['text'], alternatives=alternatives)
            question.set_answer(Alternative(text=q['answer']['text'], weight=MonteCarloRange(min=Decimal(q['answer']['weight']['min']), max=Decimal(q['answer']['weight']['max']), probable=Decimal(q['answer']['weight']['probable']))))
            self.append_question(question=question)
        self.sum_factor()
        self.multiply_factor()

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
        if (max == min == mode == 0):
            self.factor_sum = 0
        else:
            self.factor_sum = MonteCarloRange(min=min, max=max, probable=mode)
        return self.factor_sum

    def multiply_factor(self):
        max = min = mode = 1
        for q in self.questions:
            max *= q.answer.weight.max
            min *= q.answer.weight.min
            mode *= q.answer.weight.probable
        if (max == min == mode == 1):
            self.factor_mul = 0
        else:
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

    def mode(self):
        mode=[]
        for q in self.questions:
            mode.append(q.answer.weight.probable)
        return Decimal(statistics.mode(mode))

    def range(self):
        return MonteCarloRange(min=self.min(), probable=self.mode(), max=self.max())

    def mean(self):
        return MonteCarloRange(min=self.factor_sum.min/len(self.questions), max=self.factor_sum.max/len(self.questions), probable=self.factor_sum.probable/len(self.questions))
    
class Questionaires:
    def __init__(self, tef: Questionaire=Questionaire(), vuln:Questionaire=Questionaire(), lm:Questionaire=Questionaire()):
        self.questionaires={
            'tef': tef,
            'vuln': vuln,
            'lm': lm
        }

    def to_dict(self):
        return {
            'tef': self.questionaires['tef'].to_dict(),
            'vuln': self.questionaires['vuln'].to_dict(),
            'lm': self.questionaires['lm'].to_dict(),
        }
    def from_dict(self, dict:dict={}):
        tef = Questionaire(factor=dict['tef']['factor'])
        tef.from_dict(dict['tef'])
        vuln = Questionaire(factor=dict['vuln']['factor'])
        vuln.from_dict(dict['vuln'])
        lm = Questionaire(factor=dict['lm']['factor'])
        lm.from_dict(dict['lm'])
        self.questionaires={
            'tef': tef,
            'vuln': vuln,
            'lm': lm
        }
