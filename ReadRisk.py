from riskcalculator.scenario import RiskScenario
import json

with open('test.json', mode='r', encoding='utf-8') as file:
    data = json.load(file)
scenario = RiskScenario()
print(scenario)
scenario.from_dict(data)
print(scenario)

