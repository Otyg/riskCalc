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

turn_around = int(input("Vad är organisationens årliga omsättning (SEK)? "))
name = input("Namn på scenario: ")
actor = input("Aktör: ")
asset = input("Hotad tillgång: ")
threat = input("Hot: ")
vulnerability = input("Sårbarhet: ")
description = input(f"Beskrivning [auto: Risk att {actor} utnyttjar {vulnerability} för att realisera {threat} mot {asset}.]: ")
tef_modifier = g.tef_questions()
for q in tef_modifier.questions:
    i = 0
    alternatives = ""
    for a in q.alternatives:
        alternatives += str(i) + ": " + a.text + "\n"
        i += 1
    alt = input(q.text + "\n" + alternatives + "Svar [0-4]: ") 
    q.set_answer(alt)
vuln_modifier = g.vuln_questions()
for q in vuln_modifier.questions:
    i = 0
    alternatives = ""
    for a in q.alternatives:
        alternatives += str(i) + ": " + a.text + "\n"
        i += 1
    alt = input(q.text + "\n" + alternatives + "Svar [0-4]: ")
    q.set_answer(alt)
loss_modifier = g.consequence_questions()

for q in loss_modifier.questions:
    i = 0
    alternatives = ""
    for a in q.alternatives:
        alternatives += str(i) + ": " + a.text + "\n"
        i += 1
    alt = input(q.text + "\n" + alternatives + "Svar [0-4]: ")
    q.set_answer(alt)
lm = loss_modifier.range()
loss_magnitude = MonteCarloRange(min=Decimal(lm.min), probable=Decimal(lm.probable), max=Decimal(lm.max))
questionaires = Questionaires(tef=tef_modifier, vuln=vuln_modifier, lm=loss_modifier)
disc_risk = DiscreteRisk(tef=tef_modifier.multiply_factor(),
    vuln_score=vuln_modifier.sum_factor(),
    loss_magnitude=loss_magnitude,
    budget=turn_around)
risk = Risk(tef=tef_modifier.multiply_factor(),
    vuln_score=vuln_modifier.sum_factor(),
    loss_magnitude=loss_magnitude,
    budget=turn_around)

riskscenario_disc = RiskScenario(
    name=name,
    actor=actor,
    description=description,
    asset=asset,
    threat=threat,
    vulnerability=vulnerability,
    risk=disc_risk,
    questionaires=questionaires
)
riskscenario = RiskScenario(
    name=name,
    actor=actor,
    description=description,
    asset=asset,
    threat=threat,
    vulnerability=vulnerability,
    risk=risk,
    questionaires=questionaires
)

json.dump(riskscenario_disc.to_dict(), codecs.open('test.json', 'w', encoding='utf-8'), cls=ComplexEncoder)
print(riskscenario_disc)
print(riskscenario)

