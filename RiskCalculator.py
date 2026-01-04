from decimal import Decimal
from internal.montecarlo import MonteCarloRange
from internal.risk import RiskScenario
import test.generate as g
import pprint
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

riskscenario = RiskScenario(
    name=name,
    actor=actor,
    description=description,
    asset=asset,
    threat=threat,
    vulnerability=vulnerability,
    tef=tef_modifier.multiply_factor(),
    vuln_score=vuln_modifier.sum_factor(),
    loss_magnitude=loss_magnitude
)
pprint.pp(riskscenario.to_dict())
pprint.pp(tef_modifier.to_dict())
pprint.pp(vuln_modifier.to_dict())
pprint.pp(loss_modifier.to_dict())
