import unittest
from otyg_risk_base.montecarlo import MonteCarloRange
from riskcalculator.questionaire import Alternative, Question, Questionaire, Questionaires

class TestQuestionaires(unittest.TestCase):

    def test_questionaires_equality(self):
        no_questionaires = Questionaires()
        self.assertTrue(no_questionaires == no_questionaires)
        question = Question(text="Test 1", alternatives=[Alternative(text="Ja", weight=MonteCarloRange(probable=1)), Alternative(text="Nej", weight=MonteCarloRange(probable=1))])
        questionaire = Questionaire(questions=[question])
        questionaires = Questionaires(tef=questionaire, vuln=questionaire, lm=questionaire)
        self.assertFalse(no_questionaires == questionaires)

    def test_questionaire_equality(self):
        questionaire = Questionaire()
        self.assertTrue(questionaire == questionaire)
        question = Question(text="Test 1", alternatives=[Alternative(text="Ja", weight=MonteCarloRange(probable=1)), Alternative(text="Nej", weight=MonteCarloRange(probable=1))])
        questionaire_with_question = Questionaire(questions=[question])
        self.assertFalse(questionaire == questionaire_with_question)
        question_b = Question(text="Test 2", alternatives=[Alternative(text="Ja", weight=MonteCarloRange(probable=1)), Alternative(text="Nej", weight=MonteCarloRange(probable=1))])
        questionaire_with_question_b = Questionaire(questions=[question, question_b])
        self.assertFalse(questionaire_with_question_b == questionaire_with_question)

    def test_question_equality(self):
        question = Question(text="Test 1", alternatives=[Alternative(text="Ja", weight=MonteCarloRange(probable=1)), Alternative(text="Nej", weight=MonteCarloRange(probable=1))])
        question_b = Question(text="Test 2", alternatives=[Alternative(text="Ja", weight=MonteCarloRange(probable=1)), Alternative(text="Nej", weight=MonteCarloRange(probable=1))])
        self.assertTrue(question == question)
        self.assertFalse(question == question_b)

    def test_alternatives_persistence(self):
        a1 = Alternative(text="Ja", weight=MonteCarloRange(min=0, probable=1, max=2))
        a2 = Alternative(text="Nej", weight=MonteCarloRange(min=0, probable=1, max=2))
        self.assertTrue(a1 == a1)
        self.assertFalse(a1 == a2)
        self.assertTrue(a1 == Alternative.from_dict(a1.to_dict()))

    def test_question_persistence(self):
        question = Question(text="Test 1", alternatives=[Alternative(text="Ja", weight=MonteCarloRange(min=0, probable=1, max=2)), Alternative(text="Nej", weight=MonteCarloRange(min=0, probable=1, max=2))])
        question_serialized = question.to_dict()
        question_deserialized = Question.from_dict(question_serialized)
        self.assertTrue(question == question_deserialized)

    def test_questionaire_persistence(self):
        question = Question(text="Test 1", alternatives=[Alternative(text="Ja", weight=MonteCarloRange(probable=1)), Alternative(text="Nej", weight=MonteCarloRange(probable=1))])
        question_b = Question(text="Test 2", alternatives=[Alternative(text="Ja", weight=MonteCarloRange(probable=1)), Alternative(text="Nej", weight=MonteCarloRange(probable=1))])
        questionaire = Questionaire(questions=[question, question_b])
        self.assertTrue(questionaire == Questionaire.from_dict(questionaire.to_dict()))
    
    def test_questionaires_equality(self):
        question = Question(text="Test 1", alternatives=[Alternative(text="Ja", weight=MonteCarloRange(probable=1)), Alternative(text="Nej", weight=MonteCarloRange(probable=1))])
        question_b = Question(text="Test 2", alternatives=[Alternative(text="Ja", weight=MonteCarloRange(probable=1)), Alternative(text="Nej", weight=MonteCarloRange(probable=1))])
        questionaire = Questionaire(questions=[question])
        questionaire_b = Questionaire(questions=[question_b])
        questionaire_c = Questionaire(questions=[question_b, question])
        questionaires = Questionaires(tef=questionaire, vuln=questionaire_b, lm=questionaire_c)
        self.assertTrue(questionaires == questionaires)
        questionaires_b = Questionaires(tef=questionaire, vuln=questionaire_b, lm=questionaire_b)
        self.assertFalse(questionaires == questionaires_b)

    def test_questionaires_persistence(self):
        question = Question(text="Test 1", alternatives=[Alternative(text="Ja", weight=MonteCarloRange(probable=1)), Alternative(text="Nej", weight=MonteCarloRange(probable=1))])
        question_b = Question(text="Test 2", alternatives=[Alternative(text="Ja", weight=MonteCarloRange(probable=1)), Alternative(text="Nej", weight=MonteCarloRange(probable=1))])
        questionaire = Questionaire(questions=[question])
        questionaire_b = Questionaire(questions=[question_b])
        questionaire_c = Questionaire(questions=[question_b, question])
        questionaires = Questionaires(tef=questionaire, vuln=questionaire_b, lm=questionaire_c)
        self.assertTrue(questionaires == Questionaires.from_dict(questionaires.to_dict()))
if __name__ == '__main__':
    unittest.main()