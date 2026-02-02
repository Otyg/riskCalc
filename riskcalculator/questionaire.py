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
import statistics

import numpy
from otyg_risk_base.montecarlo import MonteCarloRange
from .util import freeze, reduce_decimal_places


class Alternative():
    def __init__(self, text: str = "", weight: MonteCarloRange = MonteCarloRange()):
        # TODO: Dict i konstruktorn
        self.text = text
        self.weight = weight
    
    def to_dict(self):
        return {
            "text": self.text,
            "weight": self.weight.to_dict()
        }
    @classmethod
    def from_dict(cls, values:dict):
        new = Alternative()
        new.text = values.get("text")
        new.weight=MonteCarloRange.from_dict(values=values.get("weight"))
        return new
    
    def __repr__(self):
        return str(self.to_dict())
    
    def __hash__(self):
        reduced = reduce_decimal_places(value=self.weight, ndigits=10)
        return hash((self.text, reduced.max, reduced.min, reduced.probable))
    
    def __eq__(self, value):
        return isinstance(value, Alternative) and self.__hash__() == value.__hash__()

class Question():
    def __init__(self, text: str = "", alternatives: list = None):
        #TODO: dict i konstruktorn
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
    
    @classmethod
    def from_dict(cls, values:dict):
        new = Question()
        new.text = values.get('text', "")
        alternatives = list()
        for a in values.get('alternatives'):
            alternative = Alternative.from_dict(a)
            alternatives.append(alternative)
        new.alternatives = alternatives
        new.answer = Alternative.from_dict(values.get("answer"))
        return new
    
    def __hash__(self):
        return hash(freeze(self.to_dict()))
    
    def __eq__(self, value):
        return isinstance(value, Question) and self.__hash__() == value.__hash__()
    
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
    def __init__(self, factor: str="", calculation: str="mean", questions: list = None):
        if questions is None:
            self.questions = []
        else:
            self.questions = list(questions)
        self.factor = factor
        self.calculation = calculation
        self.sum_factor()
        self.multiply_factor()
        self.mean()
        self.range()
        self.mean_75()
    
    def __hash__(self):
        questions_hash = 0
        for question in self.questions:
            questions_hash += hash((question.text, question.answer.__hash__()))
            for alternative in question.alternatives:
                reduced = reduce_decimal_places(value=alternative.weight, ndigits=10)
                questions_hash += hash((alternative.text, reduced.max, reduced.min, reduced.probable))
        return hash((self.factor, self.calculation, questions_hash)) 
    
    def __eq__(self, value):
        return isinstance(value, Questionaire) and self.__hash__() == value.__hash__()
    
    def to_dict(self):
        self.sum_factor()
        self.multiply_factor()
        self.mean()
        self.range()
        self.mean_75()
        questions = []
        for q in self.questions:
            questions.append(q.to_dict())
        return {
            "factor": self.factor,
            "calculation": self.calculation,
            "questions": questions,
            "factor_sum": self.factor_sum.to_dict(),
            "factor_mul": self.factor_mul.to_dict(),
            "factor_range": self.factor_range.to_dict(),
            "factor_mean": self.factor_mean.to_dict(),
            "factor_mean_75": self.factor_mean_75.to_dict(),
        }
    @classmethod
    def from_dict(cls, dict:dict={}):
        qs = Questionaire()
        qs.factor = dict['factor']
        qs.calculation = dict.get('calculation', 'mean')
        for q in dict['questions']:
            alternatives = []
            for a in q['alternatives']:
                alternatives.append(Alternative(text=a['text'], weight=MonteCarloRange(min=Decimal(a['weight']['min']), max=Decimal(a['weight']['max']), probable=Decimal(a['weight']['probable']))))
            question = Question(q['text'], alternatives=alternatives)
            question.set_answer(Alternative(text=q['answer']['text'], weight=MonteCarloRange(min=Decimal(q['answer']['weight']['min']), max=Decimal(q['answer']['weight']['max']), probable=Decimal(q['answer']['weight']['probable']))))
            qs.append_question(question=question)
        qs.factor_sum = dict.get('factor_sum', MonteCarloRange())
        qs.factor_mul = dict.get('factor_mul', MonteCarloRange(probable=1))
        qs.factor_range = dict.get('factor_range', MonteCarloRange())
        qs.factor_mean = dict.get('factor_mean', MonteCarloRange())
        qs.factor_mean_75 = dict.get('factor_mean_75', MonteCarloRange())
        return qs

    def append_question(self, question: Question = Question()):
        self.questions.append(question)

    def sum(self):
        return self.sum_factor()
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
            if(q.answer.weight.max != q.answer.weight.min != q.answer.weight.probable != 0):
                max *= q.answer.weight.max
                min *= q.answer.weight.min
                mode *= q.answer.weight.probable
        self.factor_mul = MonteCarloRange(min=min, max=max, probable=mode)
        return self.factor_mul

    def max_range(self):
        if len(self.questions) == 0:
            return MonteCarloRange()
        factor_max = self.questions[0].answer.weight
        max = factor_max.max
        for q in self.questions:
            if max < q.answer.weight.max:
                max = q.answer.weight.max
        return factor_max
    
    def max(self):
        if len(self.questions) == 0:
            return Decimal(1)
        factor_max = self.questions[0].answer.weight.max
        for q in self.questions:
            if factor_max < q.answer.weight.max:
                factor_max = q.answer.weight.max
        return Decimal(factor_max)

    def min(self):
        if len(self.questions) == 0:
            return Decimal(0)
        factor_min = self.questions[0].answer.weight.min
        for q in self.questions:
            if factor_min > q.answer.weight.min:
                factor_min = q.answer.weight.min
        return Decimal(factor_min)

    def mode(self):
        #TODO: Returnera max, mode, min
        if len(self.questions) == 0:
            return Decimal(0)
        mode=[]
        for q in self.questions:
            mode.append(q.answer.weight.probable)
            mode.append(q.answer.weight.max)
            mode.append(q.answer.weight.min)
        return Decimal(statistics.mode(mode))

    def range(self):
        if len(self.questions) == 0:
            self.factor_range = MonteCarloRange(min=Decimal(0), probable=Decimal(0), max=Decimal(0))
        else:
            mode=[]
            for q in self.questions:
                mode.append(q.answer.weight.probable)
                mode.append(q.answer.weight.max)
                mode.append(q.answer.weight.min)
            self.factor_range = MonteCarloRange(min=Decimal(numpy.min(mode)), probable=Decimal(statistics.mode(mode)), max=Decimal(numpy.max(mode)))
        return self.factor_range

    def count_answered_questions(self):
        num = 0
        for a in self.questions:
            if not (round(a.answer.weight.max, 10) == round(a.answer.weight.min, 10) == round(a.answer.weight.probable, 10)):
                num +=1
        return num
    
    def mean(self):
        if len(self.questions) == 0:
            self.factor_mean = MonteCarloRange()
        else:
            sum = self.sum_factor()
            non_zero_answers = self.count_answered_questions()
            if non_zero_answers == 0:
                non_zero_answers = 1
            self.factor_mean = MonteCarloRange(min=sum.min/non_zero_answers, max=sum.max/non_zero_answers, probable=sum.probable/non_zero_answers)
        return self.factor_mean
    
    def mean_75(self):
        if len(self.questions) == 0:
            self.factor_mean_75 = MonteCarloRange()
        else:
            weights=[]
            for q in self.questions:
                weights.append(q.answer.weight.probable)
                weights.append(q.answer.weight.max)
                weights.append(q.answer.weight.min)
            weights.sort()
            split = numpy.array_split(weights, 3)
            p75 = split[2]
            self.factor_mean_75 = MonteCarloRange(min=Decimal(numpy.min(p75)), probable=Decimal(statistics.mode(p75)), max=Decimal(numpy.max(p75)))
        return self.factor_mean_75

    def calculate_questionaire_value(self):
        calc = getattr(self, self.calculation)
        return calc()

class Questionaires:
    def __init__(self, tef: Questionaire=Questionaire(), vuln:Questionaire=Questionaire(), lm:Questionaire=Questionaire()):
        self.questionaires={
            'tef': tef,
            'vuln': vuln,
            'lm': lm
        }

    def calculate_questionairy_values(self):
        values = dict()
        values.update({'threat_event_frequency': self.questionaires.get('tef').calculate_questionaire_value()})
        values.update({'vulnerability': self.questionaires.get('vuln').calculate_questionaire_value()})
        values.update({'loss_magnitude': self.questionaires.get('lm').calculate_questionaire_value()})
        return values

    def to_dict(self):
        return {
            'tef': self.questionaires['tef'].to_dict(),
            'vuln': self.questionaires['vuln'].to_dict(),
            'lm': self.questionaires['lm'].to_dict(),
        }
    def __hash__(self):
        return hash(freeze(self.to_dict()))
    def __eq__(self, other):
        if isinstance(other, Questionaires):
            if self.__hash__() == other.__hash__():
                if not (self.questionaires['tef'].__hash__() == other.questionaires['tef'].__hash__()):
                    return False
                elif not (self.questionaires['vuln'].__hash__() == other.questionaires['vuln'].__hash__()):
                    return False
                elif not (self.questionaires['lm'].__hash__() == other.questionaires['lm'].__hash__()):
                    return False
                return True
        return False
    @classmethod
    def from_dict(cls, values:dict={}):
        tef = Questionaire.from_dict(dict=values['tef'])
        vuln = Questionaire.from_dict(dict=values['vuln'])
        lm = Questionaire.from_dict(dict=values['lm'])
        return Questionaires(tef=tef, vuln=vuln, lm=lm)
