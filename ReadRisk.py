from decimal import Decimal
from internal.discret_scale import DiscreteRisk
from internal.montecarlo import MonteCarloRange
from internal.questionaire import Questionaires
from internal.risk import Risk
from internal.scenario import RiskScenario
from internal.util import ComplexEncoder
import test.generate as g
import json
import codecs

with open('test.json', mode='r', encoding='utf-8') as file:
    data = json.load(file)
scenario = RiskScenario()
print(scenario)
scenario.from_dict(data)
print(scenario)

