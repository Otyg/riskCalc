from internal.questionaire import *
from decimal import Decimal


def tef_questions():
    q1 = Question(
        text="Hur ofta observerar vi försök från denna typ av hotaktör att få åtkomst till tillgången?",
        alternatives=[
            Alternative(text="Aldrig / mindre än en gång per 10 år", weight=MonteCarloRange(
                min=Decimal("0.05"), probable=Decimal("0.1"), max=Decimal("0.2"))),
            Alternative(text="Mycket sällan (mindre än en gång per år)", weight=MonteCarloRange(
                min=Decimal("0.2"), probable=Decimal("0.5"), max=Decimal("0.9"))),
            Alternative(text="Sällan (i snitt en gång per år)", weight=MonteCarloRange(
                min=Decimal("0.8"), probable=Decimal("1.0"), max=Decimal("2.5"))),
            Alternative(text="Periodvis (ungefär en gång per kvartal)", weight=MonteCarloRange(
                min=Decimal("3"), probable=Decimal("4"), max=Decimal("6"))),
            Alternative(text="Ofta (nästan dagligen)", weight=MonteCarloRange(
                min=Decimal("150"), probable=Decimal("250"), max=Decimal("365"))),
        ]
    )
    q2 = Question(
        text="Hur attraktiv är tillgången för hotaktören?",
        alternatives=[
            Alternative(text="Mycket låg attraktivitet", weight=MonteCarloRange(
                min=Decimal("0.2"), probable=Decimal("0.3"), max=Decimal("0.5"))),
            Alternative(text="Låg attraktivitet", weight=MonteCarloRange(
                min=Decimal("0.5"), probable=Decimal("0.7"), max=Decimal("0.9"))),
            Alternative(text="Medelattraktiv", weight=MonteCarloRange(
                min=Decimal("0.9"), probable=Decimal("1.0"), max=Decimal("1.2"))),
            Alternative(text="Hög attraktivitet", weight=MonteCarloRange(
                min=Decimal("1.2"), probable=Decimal("1.6"), max=Decimal("2.0"))),
            Alternative(text="Mycket hög attraktivitet", weight=MonteCarloRange(
                min=Decimal("2.0"), probable=Decimal("3.0"), max=Decimal("4.0"))),
        ]
    )

    q3 = Question(
        text="Hur resursstark och motiverad är den aktuella hotaktören?",
        alternatives=[
            Alternative(text="Låg förmåga & låg motivation", weight=MonteCarloRange(
                min=Decimal("0.3"), probable=Decimal("0.5"), max=Decimal("0.8"))),
            Alternative(text="Låg–medel förmåga eller motivation", weight=MonteCarloRange(
                min=Decimal("0.8"), probable=Decimal("1.0"), max=Decimal("1.3"))),
            Alternative(text="Medelnivå", weight=MonteCarloRange(
                min=Decimal("1.0"), probable=Decimal("1.2"), max=Decimal("1.8"))),
            Alternative(text="Hög förmåga eller motivation", weight=MonteCarloRange(
                min=Decimal("1.8"), probable=Decimal("2.5"), max=Decimal("3.5"))),
            Alternative(text="Mycket hög förmåga & hög motivation", weight=MonteCarloRange(
                min=Decimal("3.5"), probable=Decimal("5.0"), max=Decimal("8.0"))),
        ]
    )

    q4 = Question(
        text="I vilken utsträckning är systemet eller processen exponerad mot hotaktören?",
        alternatives=[
            Alternative(text="Mycket begränsad exponering (intern, strikt åtkomst)", weight=MonteCarloRange(
                min=Decimal("0.3"), probable=Decimal("0.5"), max=Decimal("0.8"))),
            Alternative(text="Begränsad exponering (VPN/åtkomstkontroller)", weight=MonteCarloRange(
                min=Decimal("0.7"), probable=Decimal("0.9"), max=Decimal("1.2"))),
            Alternative(text="Måttlig exponering (delvis internetnära/beroenden)",
                        weight=MonteCarloRange(min=Decimal("1.0"), probable=Decimal("1.2"), max=Decimal("1.6"))),
            Alternative(text="Hög exponering (flera åtkomstytor, öppna API:er)", weight=MonteCarloRange(
                min=Decimal("1.4"), probable=Decimal("1.8"), max=Decimal("2.6"))),
            Alternative(text="Mycket hög exponering (internetexponerat, stor attackyta)", weight=MonteCarloRange(
                min=Decimal("2.2"), probable=Decimal("3.2"), max=Decimal("5.0"))),
        ]
    )

    q5 = Question(
        text="Har vi historik över incidenter eller försök relaterade till detta hot?",
        alternatives=[
            Alternative(text="Ingen historik", weight=MonteCarloRange(
                min=Decimal("0.3"), probable=Decimal("0.5"), max=Decimal("0.8"))),
            Alternative(text="Enstaka mindre incidenter", weight=MonteCarloRange(
                min=Decimal("0.8"), probable=Decimal("1.0"), max=Decimal("1.3"))),
            Alternative(text="Regelbundet förekommande", weight=MonteCarloRange(
                min=Decimal("1.2"), probable=Decimal("1.6"), max=Decimal("2.2"))),
            Alternative(text="Återkommande större incidenter", weight=MonteCarloRange(
                min=Decimal("1.8"), probable=Decimal("2.5"), max=Decimal("3.5"))),
            Alternative(text="Frekvent och nyligen förekommande", weight=MonteCarloRange(
                min=Decimal("2.5"), probable=Decimal("3.5"), max=Decimal("5.0"))),
        ]
    )
    return Questionaire(factor="tef", questions=[q1, q2, q3, q4, q5])


def vuln_questions():
    # --- VULN additive (percentage-points; Q6–Q10). Sum contributions, cap at 100% ---

    q6 = Question(
        text="Hur starka är våra kontroller i relation till hotaktörens förmåga?",
        alternatives=[
            Alternative(text="Mycket starka kontroller", weight=MonteCarloRange(
                min=Decimal("0.00"), probable=Decimal("0.02"), max=Decimal("0.05"))),
            Alternative(text="Starka kontroller", weight=MonteCarloRange(
                min=Decimal("0.04"), probable=Decimal("0.07"), max=Decimal("0.10"))),
            Alternative(text="Medelstarka kontroller", weight=MonteCarloRange(
                min=Decimal("0.10"), probable=Decimal("0.15"), max=Decimal("0.20"))),
            Alternative(text="Svaga kontroller", weight=MonteCarloRange(
                min=Decimal("0.18"), probable=Decimal("0.24"), max=Decimal("0.28"))),
            Alternative(text="Mycket svaga kontroller", weight=MonteCarloRange(
                min=Decimal("0.24"), probable=Decimal("0.28"), max=Decimal("0.30"))),
        ]
    )

    q7 = Question(
        text="Hur konsekvent tillämpas och efterlevs säkerhetskontroller i praktiken?",
        alternatives=[
            Alternative(text="Nära 100 % efterlevnad", weight=MonteCarloRange(
                min=Decimal("0.00"), probable=Decimal("0.01"), max=Decimal("0.03"))),
            Alternative(text="Hög efterlevnad (70–90 %)", weight=MonteCarloRange(
                min=Decimal("0.03"), probable=Decimal("0.06"), max=Decimal("0.10"))),
            Alternative(text="Medelgod efterlevnad", weight=MonteCarloRange(
                min=Decimal("0.08"), probable=Decimal("0.12"), max=Decimal("0.15"))),
            Alternative(text="Låg efterlevnad", weight=MonteCarloRange(
                min=Decimal("0.12"), probable=Decimal("0.16"), max=Decimal("0.19"))),
            Alternative(text="Mycket låg efterlevnad", weight=MonteCarloRange(
                min=Decimal("0.16"), probable=Decimal("0.19"), max=Decimal("0.20"))),
        ]
    )

    q8 = Question(
        text="Finns det kända svagheter eller sårbarheter som hotaktören sannolikt kan utnyttja?",
        alternatives=[
            Alternative(text="Inga kända svagheter", weight=MonteCarloRange(
                min=Decimal("0.00"), probable=Decimal("0.01"), max=Decimal("0.04"))),
            Alternative(text="Mindre svagheter", weight=MonteCarloRange(
                min=Decimal("0.03"), probable=Decimal("0.06"), max=Decimal("0.09"))),
            Alternative(text="Kända svagheter", weight=MonteCarloRange(
                min=Decimal("0.08"), probable=Decimal("0.12"), max=Decimal("0.17"))),
            Alternative(text="Utnyttjningsbara svagheter", weight=MonteCarloRange(
                min=Decimal("0.15"), probable=Decimal("0.20"), max=Decimal("0.23"))),
            Alternative(text="Kritiska svagheter", weight=MonteCarloRange(
                min=Decimal("0.20"), probable=Decimal("0.23"), max=Decimal("0.25"))),
        ]
    )

    q9 = Question(
        text="Hur snabbt kan vi upptäcka och stoppa ett angrepp om det sker?",
        alternatives=[
            Alternative(text="Mycket snabbt", weight=MonteCarloRange(
                min=Decimal("0.00"), probable=Decimal("0.01"), max=Decimal("0.03"))),
            Alternative(text="Snabbt", weight=MonteCarloRange(min=Decimal(
                "0.02"), probable=Decimal("0.04"), max=Decimal("0.06"))),
            Alternative(text="Måttligt", weight=MonteCarloRange(
                min=Decimal("0.06"), probable=Decimal("0.09"), max=Decimal("0.11"))),
            Alternative(text="Långsamt", weight=MonteCarloRange(
                min=Decimal("0.10"), probable=Decimal("0.13"), max=Decimal("0.14"))),
            Alternative(text="Mycket långsamt", weight=MonteCarloRange(
                min=Decimal("0.12"), probable=Decimal("0.14"), max=Decimal("0.15"))),
        ]
    )

    q10 = Question(
        text="Finns det beroenden till tredjepart som kan öka sårbarheten?",
        alternatives=[
            Alternative(text="Inga beroenden", weight=MonteCarloRange(
                min=Decimal("0.00"), probable=Decimal("0.01"), max=Decimal("0.02"))),
            Alternative(text="Minimala beroenden", weight=MonteCarloRange(
                min=Decimal("0.01"), probable=Decimal("0.03"), max=Decimal("0.05"))),
            Alternative(text="Måttliga beroenden", weight=MonteCarloRange(
                min=Decimal("0.04"), probable=Decimal("0.06"), max=Decimal("0.07"))),
            Alternative(text="Betydande beroenden", weight=MonteCarloRange(
                min=Decimal("0.06"), probable=Decimal("0.08"), max=Decimal("0.09"))),
            Alternative(text="Kritiska beroenden", weight=MonteCarloRange(
                min=Decimal("0.08"), probable=Decimal("0.09"), max=Decimal("0.10"))),
        ]
    )

    return Questionaire(factor="vuln", questions=[q6, q7, q8, q9, q10])
