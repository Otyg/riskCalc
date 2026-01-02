from decimal import Decimal
from internal.montecarlo import MonteCarloRange
from internal.risk import RiskScenario

name = input("Namn på scenario: ")
actor = input("Aktör: ")
description = input("Beskrivning [auto]: ")
asset = input("Hotad tillgång: ")
threat = input("Hot: ")
vulnerability = input("Sårbarhet: ")
tef = input("Sannolik förekomst av händelser som utgör ett hot (antal per år): ")
vuln_score = input("Sårbarhet i procent (0-100): ")
loss_magnitude = input("Ekonomisk förlust av ett lyckat angrepp (kr): ")

riskscenario = RiskScenario(
    name=name,
    actor=actor,
    description=description,
    asset=asset,
    threat=threat,
    vulnerability=vulnerability,
    tef=MonteCarloRange(probable=tef),
    vuln_score=MonteCarloRange(probable=Decimal(vuln_score)/Decimal(100.0000)),
    loss_magnitude=MonteCarloRange(probable=loss_magnitude)
    )
print([riskscenario])