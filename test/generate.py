from internal.questionaire import *
from decimal import Decimal
LEVEL_1_RANGE = MonteCarloRange(
    min=Decimal(0.001),
    probable=Decimal(0.005),
    max=Decimal(0.01)
)

LEVEL_2_RANGE = MonteCarloRange(
    min=Decimal(0.005),
    probable=Decimal(0.015),
    max=Decimal(0.025)
)

LEVEL_3_RANGE = MonteCarloRange(
    min=Decimal(0.015),
    probable=Decimal(0.03),
    max=Decimal(0.04)
)

LEVEL_4_RANGE = MonteCarloRange(
    min=Decimal(0.03),
    probable=Decimal(0.05),
    max=Decimal(0.065)
)

LEVEL_5_RANGE = MonteCarloRange(
    min=Decimal(0.05),
    probable=Decimal(0.08),
    max=Decimal(0.08)
)


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

def consequence_questions():
    questions = [
        Question(
            text="Om händelsen inträffar, vilken är den allvarligaste rimliga konsekvensen för människors liv och hälsa?",
            alternatives=[
                Alternative(text="Inga eller obetydliga personskador utan medicinsk behandling", weight=LEVEL_1_RANGE),
                Alternative(text="Lindriga personskador eller tillfällig arbetsfrånvaro", weight=LEVEL_2_RANGE),
                Alternative(text="Allvarlig personskada med långvarig frånvaro eller bestående men", weight=LEVEL_3_RANGE),
                Alternative(text="Mycket allvarlig skada, bestående men eller enstaka dödsfall", weight=LEVEL_4_RANGE),
                Alternative(text="Flera dödsfall eller mycket omfattande påverkan på människoliv", weight=LEVEL_5_RANGE),
            ]
        ),
        Question(
            text="Om information röjs till obehöriga, vilken är den allvarligaste rimliga konsekvensen?",
            alternatives=[
                Alternative(text="Röjande av offentliga eller redan allmänt kända uppgifter", weight=LEVEL_1_RANGE),
                Alternative(text="Begränsat röjande av vanliga personuppgifter", weight=LEVEL_2_RANGE),
                Alternative(text="Röjande av känsliga personuppgifter, hälsodata eller OSL-uppgifter i enskilda fall", weight=LEVEL_3_RANGE),
                Alternative(text="Omfattande röjande av känsliga personuppgifter eller sekretessbelagd information", weight=LEVEL_4_RANGE),
                Alternative(text="Mycket omfattande eller systematiskt röjande med allvarliga och långvariga konsekvenser", weight=LEVEL_5_RANGE),
            ]
        ),
        Question(
            text="Om information blir felaktig, manipulerad eller ofullständig, vilken är den allvarligaste rimliga konsekvensen?",
            alternatives=[
                Alternative(text="Mindre fel utan faktisk påverkan", weight=LEVEL_1_RANGE),
                Alternative(text="Fel som kräver korrigering eller leder till mindre felbeslut", weight=LEVEL_2_RANGE),
                Alternative(text="Fel som påverkar individers rättigheter eller viktiga beslut", weight=LEVEL_3_RANGE),
                Alternative(text="Systematiska eller allvarliga fel i information", weight=LEVEL_4_RANGE),
                Alternative(text="Utbredd och långvarig integritetsförlust med mycket allvarliga konsekvenser", weight=LEVEL_5_RANGE),
            ]
        ),
        Question(
            text="Om information, system eller tjänster inte är tillgängliga vid behov, vilken är den allvarligaste rimliga konsekvensen?",
            alternatives=[
                Alternative(text="Kortvarig störning utan märkbar påverkan", weight=LEVEL_1_RANGE),
                Alternative(text="Tillfällig otillgänglighet med begränsad verksamhetspåverkan", weight=LEVEL_2_RANGE),
                Alternative(text="Avbrott som påverkar viktiga processer eller tjänster", weight=LEVEL_3_RANGE),
                Alternative(text="Allvarlig otillgänglighet med betydande verksamhetspåverkan", weight=LEVEL_4_RANGE),
                Alternative(text="Långvarig eller omfattande otillgänglighet i samhällsviktiga system", weight=LEVEL_5_RANGE),
            ]
        ),
        Question(
            text="Om händelsen blir känd externt, vilken är den allvarligaste rimliga påverkanen på förtroendet för sjukhuset?",
            alternatives=[
                Alternative(text="Begränsad intern negativ uppmärksamhet", weight=LEVEL_1_RANGE),
                Alternative(text="Lokal eller begränsad negativ uppmärksamhet", weight=LEVEL_2_RANGE),
                Alternative(text="Påtaglig förtroendeskada och mediabevakning", weight=LEVEL_3_RANGE),
                Alternative(text="Omfattande nationell negativ mediebevakning", weight=LEVEL_4_RANGE),
                Alternative(text="Mycket allvarlig och varaktig förtroendekris", weight=LEVEL_5_RANGE),
            ]
        ),
        Question(
            text="Vilken är den allvarligaste rimliga konsekvensen för vårdproduktion och patientsäkerhet?",
            alternatives=[
                Alternative(text="Marginell påverkan på enskilda vårdmoment", weight=LEVEL_1_RANGE),
                Alternative(text="Tillfällig påverkan på vårdflöden eller väntetider", weight=LEVEL_2_RANGE),
                Alternative(text="Påtaglig påverkan på klinisk verksamhet, omplanering krävs", weight=LEVEL_3_RANGE),
                Alternative(text="Allvarliga störningar i vårdproduktionen eller patientsäkerheten", weight=LEVEL_4_RANGE),
                Alternative(text="Omfattande och långvarig påverkan med risk för allvarliga vårdskador eller dödsfall", weight=LEVEL_5_RANGE),
            ]
        ),
        Question(
            text="Vilken är den allvarligaste rimliga konsekvensen för forskningsverksamheten?",
            alternatives=[
                Alternative(text="Försumbar påverkan på forskningsaktiviteter", weight=LEVEL_1_RANGE),
                Alternative(text="Tillfällig försening i forskningsprojekt", weight=LEVEL_2_RANGE),
                Alternative(text="Allvarlig försening eller omplanering av forskningsprojekt", weight=LEVEL_3_RANGE),
                Alternative(text="Avbrott i forskning med risk för förlorad finansiering eller regelbrister", weight=LEVEL_4_RANGE),
                Alternative(text="Omfattande och långvarig påverkan med förlorat förtroende hos finansiärer", weight=LEVEL_5_RANGE),
            ]
        )
    ]
    return Questionaire(factor="consequence", questions=questions)

def to_dict():
    return vuln_questions().to_dict()