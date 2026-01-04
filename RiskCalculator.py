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
    alt = input(q.text + " ")
    q.set_answer(alt)
vuln_modifier = g.vuln_questions()
for q in vuln_modifier.questions:
    alt = input(q.text + " ")
    q.set_answer(alt)
loss_magnitude = input("Ekonomisk förlust av ett lyckat angrepp (kr): ")

riskscenario = RiskScenario(
    name=name,
    actor=actor,
    description=description,
    asset=asset,
    threat=threat,
    vulnerability=vulnerability,
    tef=tef_modifier.multiply_factor(),
    vuln_score=vuln_modifier.sum_factor(),
    loss_magnitude=MonteCarloRange(probable=loss_magnitude)
)
pprint.pp(riskscenario.to_dict())
pprint.pp(tef_modifier.to_dict())
pprint.pp(vuln_modifier.to_dict())
