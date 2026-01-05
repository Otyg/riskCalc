from decimal import Decimal
from internal.montecarlo import MonteCarloRange
from internal.questionaire import Questionaires
from internal.risk import RiskScenario
from internal.util import ComplexEncoder
import test.generate as g
import json
import codecs

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
turn_around = int(input("Vad är organisationens årliga omsättning (SEK)? "))
for q in loss_modifier.questions:
    i = 0
    alternatives = ""
    for a in q.alternatives:
        alternatives += str(i) + ": " + a.text + "\n"
        i += 1
    alt = input(q.text + "\n" + alternatives + "Svar [0-4]: ")
    q.set_answer(alt)
lm = loss_modifier.range()
loss_magnitude = MonteCarloRange(min=Decimal(lm.min*turn_around), probable=Decimal(lm.probable*turn_around), max=Decimal(lm.max*turn_around))
questionaires = Questionaires(tef=tef_modifier, vuln=vuln_modifier, lm=loss_modifier)
riskscenario = RiskScenario(
    name=name,
    actor=actor,
    description=description,
    asset=asset,
    threat=threat,
    vulnerability=vulnerability,
    tef=tef_modifier.multiply_factor(),
    vuln_score=vuln_modifier.sum_factor(),
    loss_magnitude=loss_magnitude,
    questionaires=questionaires
)
json.dump(riskscenario.to_dict(), codecs.open('test.json', 'w', encoding='utf-8'), cls=ComplexEncoder)

