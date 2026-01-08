import codecs
import json
from riskcalculator.questionaire import *
from decimal import Decimal

from riskcalculator.util import ComplexEncoder
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

def generate_privacy_questions():
    # Privacy context:
    # - TEF (q1–q5) estimates how often "privacy threat events" are attempted/occur in your processing context
    #   (e.g., re-identification attempts, unauthorized access, excessive collection, unintended disclosure).
    # - VULN (q6–q10) is additive and represents the summed likelihood contribution (0–1) that a threat event
    #   becomes a "privacy loss event" (mapped to LINDDUN + Solove-style privacy harms). Cap at 1.0 in your calc.
    # - LEF = TEF × VULN  (events/year)

    # -----------------------
    # TEF (Q1–Q5) — privacy
    # -----------------------

    q1 = Question(
    text="Hur ofta inträffar (eller försöks) en integritetsrelaterad händelse i detta flöde? (t.ex. obehörig åtkomst, överinsamling, felaktig delning, re-identifiering, otillåten spårning)",
    alternatives=[
        Alternative(text="Aldrig / mindre än en gång per 10 år",      weight=MonteCarloRange(min=Decimal("0.05"), probable=Decimal("0.1"),  max=Decimal("0.2"))),
        Alternative(text="Sällan (mindre än en gång per år)",         weight=MonteCarloRange(min=Decimal("0.2"),  probable=Decimal("0.5"),  max=Decimal("0.9"))),
        Alternative(text="Periodvis (i snitt en gång per år)",        weight=MonteCarloRange(min=Decimal("0.8"),  probable=Decimal("1.0"),  max=Decimal("1.5"))),
        Alternative(text="Ofta (ungefär en gång per kvartal)",        weight=MonteCarloRange(min=Decimal("3"),    probable=Decimal("4"),    max=Decimal("6"))),
        Alternative(text="Mycket ofta (nästan dagligen)",             weight=MonteCarloRange(min=Decimal("150"),  probable=Decimal("250"),  max=Decimal("350"))),
    ]
    )

    q2 = Question(
    text="Hur attraktivt är detta dataflöde för integritetsintrång (Solove: insamling/processing/spridning/intrång; LINDDUN: linkability/identifiability/disclosure m.fl.)?",
    alternatives=[
        Alternative(text="Mycket låg attraktivitet (låg känslighet, låg nytta för angripare)", weight=MonteCarloRange(min=Decimal("0.2"), probable=Decimal("0.3"), max=Decimal("0.5"))),
        Alternative(text="Låg attraktivitet",                                                   weight=MonteCarloRange(min=Decimal("0.5"), probable=Decimal("0.7"), max=Decimal("0.9"))),
        Alternative(text="Medelattraktivt",                                                      weight=MonteCarloRange(min=Decimal("0.9"), probable=Decimal("1.0"), max=Decimal("1.2"))),
        Alternative(text="Hög attraktivitet (t.ex. personprofiler, beteendedata, identifierare)", weight=MonteCarloRange(min=Decimal("1.2"), probable=Decimal("1.6"), max=Decimal("2.0"))),
        Alternative(text="Mycket hög attraktivitet (känsliga personuppgifter/nyckelidentifierare i stor skala)", weight=MonteCarloRange(min=Decimal("2.0"), probable=Decimal("3.0"), max=Decimal("4.0"))),
    ]
    )

    q3 = Question(
    text="Hur sannolikt är det att en relevant aktör driver integritetsintrång här (extern angripare, insider, leverantör, 'curious analyst')?",
    alternatives=[
        Alternative(text="Låg sannolikhet (svag motivation/förmåga)",               weight=MonteCarloRange(min=Decimal("0.3"), probable=Decimal("0.5"), max=Decimal("0.8"))),
        Alternative(text="Låg–medel sannolikhet",                                  weight=MonteCarloRange(min=Decimal("0.8"), probable=Decimal("1.0"), max=Decimal("1.3"))),
        Alternative(text="Medel sannolikhet",                                      weight=MonteCarloRange(min=Decimal("1.0"), probable=Decimal("1.2"), max=Decimal("1.8"))),
        Alternative(text="Hög sannolikhet (starka incitament eller vana mönster)",  weight=MonteCarloRange(min=Decimal("1.8"), probable=Decimal("2.5"), max=Decimal("3.5"))),
        Alternative(text="Mycket hög sannolikhet (aktivt jagad data/övervakning)",  weight=MonteCarloRange(min=Decimal("3.5"), probable=Decimal("5.0"), max=Decimal("8.0"))),
    ]
    )

    q4 = Question(
    text="Hur exponerat är dataflödet för integritetsrelaterade hot (åtkomstvägar, antal system/ytor, delningar, API:er, loggar, export, analysmiljöer)?",
    alternatives=[
        Alternative(text="Mycket begränsad exponering (få ytor, strikt åtkomst, ingen export)", weight=MonteCarloRange(min=Decimal("0.3"), probable=Decimal("0.5"), max=Decimal("0.8"))),
        Alternative(text="Begränsad exponering (några ytor/roller, kontrollerade integrationer)", weight=MonteCarloRange(min=Decimal("0.7"), probable=Decimal("0.9"), max=Decimal("1.2"))),
        Alternative(text="Måttlig exponering (flera system/roller, viss export/analys)",         weight=MonteCarloRange(min=Decimal("1.0"), probable=Decimal("1.2"), max=Decimal("1.6"))),
        Alternative(text="Hög exponering (många integrationer, data lakes/BI, många läsare)",    weight=MonteCarloRange(min=Decimal("1.4"), probable=Decimal("1.8"), max=Decimal("2.6"))),
        Alternative(text="Mycket hög exponering (bred delning/åtkomst, internetnära komponenter, många tredjepartsflöden)", weight=MonteCarloRange(min=Decimal("2.2"), probable=Decimal("3.2"), max=Decimal("5.0"))),
    ]
    )

    q5 = Question(
    text="Hur ser historiken ut för integritetsincidenter/avvikelser i liknande flöden (inkl. 'near-misses', felkonfigurationer, otillåten åtkomst, felaktig delning)?",
    alternatives=[
        Alternative(text="Ingen känd historik",                                weight=MonteCarloRange(min=Decimal("0.3"), probable=Decimal("0.5"), max=Decimal("0.8"))),
        Alternative(text="Enstaka avvikelser/near-misses",                     weight=MonteCarloRange(min=Decimal("0.8"), probable=Decimal("1.0"), max=Decimal("1.3"))),
        Alternative(text="Regelbundet återkommande mindre avvikelser",          weight=MonteCarloRange(min=Decimal("1.2"), probable=Decimal("1.6"), max=Decimal("2.2"))),
        Alternative(text="Återkommande incidenter med extern rapportering/DSR", weight=MonteCarloRange(min=Decimal("1.8"), probable=Decimal("2.5"), max=Decimal("3.5"))),
        Alternative(text="Frekventa incidenter eller tydlig trend uppåt",       weight=MonteCarloRange(min=Decimal("2.5"), probable=Decimal("3.5"), max=Decimal("5.0"))),
    ]
    )

    # ------------------------------------
    # VULN additive (Q6–Q10) — privacy 0–1
    # (Summed contribution, cap at 1.0)
    # ------------------------------------

    q6 = Question(
    text="LINDDUN: Linkability/Identifiability — hur väl är data/pseudonymer skyddade mot koppling & återidentifiering (pseudonymisering, separation, k-anon-liknande skydd, åtkomst till nycklar)?",
    alternatives=[
        Alternative(text="Mycket starkt skydd (återidentifiering mycket svårt)", weight=MonteCarloRange(min=Decimal("0.00"), probable=Decimal("0.02"), max=Decimal("0.05"))),
        Alternative(text="Starkt skydd",                                         weight=MonteCarloRange(min=Decimal("0.04"), probable=Decimal("0.07"), max=Decimal("0.10"))),
        Alternative(text="Medelskydd",                                           weight=MonteCarloRange(min=Decimal("0.10"), probable=Decimal("0.15"), max=Decimal("0.20"))),
        Alternative(text="Svagt skydd (lätt att länka/identifiera i praktiken)",  weight=MonteCarloRange(min=Decimal("0.18"), probable=Decimal("0.24"), max=Decimal("0.28"))),
        Alternative(text="Mycket svagt (direkta identifierare/bred åtkomst till nycklar)", weight=MonteCarloRange(min=Decimal("0.24"), probable=Decimal("0.28"), max=Decimal("0.30"))),
    ]
    )

    q7 = Question(
    text="LINDDUN: Non-repudiation/Detectability — hur bra är spårbarhet, loggning och kontroll av vem som gjort vad (så att missbruk upptäcks och kan utredas)?",
    alternatives=[
        Alternative(text="Nästan full spårbarhet + aktiv övervakning",        weight=MonteCarloRange(min=Decimal("0.00"), probable=Decimal("0.01"), max=Decimal("0.03"))),
        Alternative(text="God spårbarhet men inte konsekvent överallt",       weight=MonteCarloRange(min=Decimal("0.03"), probable=Decimal("0.06"), max=Decimal("0.10"))),
        Alternative(text="Viss spårbarhet, många blinda fläckar",             weight=MonteCarloRange(min=Decimal("0.08"), probable=Decimal("0.12"), max=Decimal("0.15"))),
        Alternative(text="Låg spårbarhet (svårt att upptäcka/utreda)",        weight=MonteCarloRange(min=Decimal("0.12"), probable=Decimal("0.16"), max=Decimal("0.19"))),
        Alternative(text="Mycket låg/ingen spårbarhet",                      weight=MonteCarloRange(min=Decimal("0.16"), probable=Decimal("0.19"), max=Decimal("0.20"))),
    ]
    )

    q8 = Question(
    text="Solove: Information Processing — i vilken grad finns risk för sekundäranvändning, överbevarande, bristande data-minimering och felaktig aggregering/profilering i flödet?",
    alternatives=[
        Alternative(text="Mycket låg (minimering, retention, purpose limitation sitter)", weight=MonteCarloRange(min=Decimal("0.00"), probable=Decimal("0.01"), max=Decimal("0.04"))),
        Alternative(text="Låg",                                                          weight=MonteCarloRange(min=Decimal("0.03"), probable=Decimal("0.06"), max=Decimal("0.09"))),
        Alternative(text="Medel (viss överinsamling/retention eller otydliga syften)",    weight=MonteCarloRange(min=Decimal("0.08"), probable=Decimal("0.12"), max=Decimal("0.17"))),
        Alternative(text="Hög (profilering/sekundäranvändning vanligt förekommande)",    weight=MonteCarloRange(min=Decimal("0.15"), probable=Decimal("0.20"), max=Decimal("0.23"))),
        Alternative(text="Mycket hög (systematisk/okontrollerad processing som ökar integritetsintrång)", weight=MonteCarloRange(min=Decimal("0.20"), probable=Decimal("0.23"), max=Decimal("0.25"))),
    ]
    )

    q9 = Question(
    text="LINDDUN: Disclosure of information — hur sannolikt är oavsiktlig/otillåten spridning (felkonfig, felaktiga behörigheter, delning med fel mottagare, dataexfiltration)?",
    alternatives=[
        Alternative(text="Mycket låg (starkt skydd + processer, få spridningsvägar)", weight=MonteCarloRange(min=Decimal("0.00"), probable=Decimal("0.01"), max=Decimal("0.03"))),
        Alternative(text="Låg",                                                      weight=MonteCarloRange(min=Decimal("0.02"), probable=Decimal("0.04"), max=Decimal("0.06"))),
        Alternative(text="Medel",                                                    weight=MonteCarloRange(min=Decimal("0.06"), probable=Decimal("0.09"), max=Decimal("0.11"))),
        Alternative(text="Hög",                                                      weight=MonteCarloRange(min=Decimal("0.10"), probable=Decimal("0.13"), max=Decimal("0.14"))),
        Alternative(text="Mycket hög (många vägar + svaga kontroller)",              weight=MonteCarloRange(min=Decimal("0.12"), probable=Decimal("0.14"), max=Decimal("0.15"))),
    ]
    )

    q10 = Question(
    text="LINDDUN: Unawareness/Non-compliance — hur stor är risken att transparens, samtycke/rättslig grund, informationsplikt och registrerades rättigheter inte uppfylls i praktiken?",
    alternatives=[
        Alternative(text="Mycket låg (tydliga notices, DSR-hantering, juridik & processer sitter)", weight=MonteCarloRange(min=Decimal("0.00"), probable=Decimal("0.01"), max=Decimal("0.02"))),
        Alternative(text="Låg",                                                                    weight=MonteCarloRange(min=Decimal("0.01"), probable=Decimal("0.03"), max=Decimal("0.05"))),
        Alternative(text="Medel (luckor i transparens/DSR eller otydlig rättslig grund)",           weight=MonteCarloRange(min=Decimal("0.04"), probable=Decimal("0.06"), max=Decimal("0.07"))),
        Alternative(text="Hög (återkommande brister i notice/DSR/grund)",                           weight=MonteCarloRange(min=Decimal("0.06"), probable=Decimal("0.08"), max=Decimal("0.09"))),
        Alternative(text="Mycket hög (systematiska brister / låg styrning)",                        weight=MonteCarloRange(min=Decimal("0.08"), probable=Decimal("0.09"), max=Decimal("0.10"))),
    ]
    )

    tef = Questionaire(factor="tef", questions=[q1, q2, q3, q4, q5])
    vuln = Questionaire(factor="vuln", questions=[q6, q7, q8, q9, q10])
    LEVEL_1_RANGE = MonteCarloRange(min=Decimal("0.001"), probable=Decimal("0.005"), max=Decimal("0.01"))
    LEVEL_2_RANGE = MonteCarloRange(min=Decimal("0.005"), probable=Decimal("0.015"), max=Decimal("0.025"))
    LEVEL_3_RANGE = MonteCarloRange(min=Decimal("0.015"), probable=Decimal("0.03"),  max=Decimal("0.04"))
    LEVEL_4_RANGE = MonteCarloRange(min=Decimal("0.03"),  probable=Decimal("0.05"),  max=Decimal("0.065"))
    LEVEL_5_RANGE = MonteCarloRange(min=Decimal("0.05"),  probable=Decimal("0.08"),  max=Decimal("0.08"))

    cons = [
    Question(
            text="Hur allvarlig blir konsekvensen för den registrerade av att kunna identifieras eller länkas/profileras?",
            alternatives=[
                Alternative(
                    text="Ingen eller försumbar konsekvens: individen förblir i praktiken icke-identifierbar och uppgifter kan inte meningsfullt länkas.",
                    weight=LEVEL_1_RANGE
                ),
                Alternative(
                    text="Begränsad konsekvens: viss risk för indirekt identifiering men endast i enskilda fall och med begränsad påverkan.",
                    weight=LEVEL_2_RANGE
                ),
                Alternative(
                    text="Påtaglig konsekvens: identifiering eller länkning kan möjliggöra tydlig profilering eller kartläggning med märkbar påverkan.",
                    weight=LEVEL_3_RANGE
                ),
                Alternative(
                    text="Allvarlig konsekvens: direkt identifiering/länkning möjlig för många; kan leda till betydande integritetsintrång eller negativ påverkan.",
                    weight=LEVEL_4_RANGE
                ),
                Alternative(
                    text="Mycket allvarlig konsekvens: systematisk identifiering, spårning eller långvarig profilering med omfattande och varaktig påverkan.",
                    weight=LEVEL_5_RANGE
                ),
            ]
        ),

        Question(
            text="Hur allvarlig blir konsekvensen för den registrerade av att uppgifter röjs eller sprids till obehöriga?",
            alternatives=[
                Alternative(
                    text="Ingen eller försumbar konsekvens: inga personuppgifter eller endast trivial information exponeras utan negativ effekt.",
                    weight=LEVEL_1_RANGE
                ),
                Alternative(
                    text="Begränsad konsekvens: begränsad exponering till få mottagare; mindre obehag eller hanterbar olägenhet.",
                    weight=LEVEL_2_RANGE
                ),
                Alternative(
                    text="Påtaglig konsekvens: exponering kan orsaka tydligt obehag, oro eller social påverkan; viss risk för utnyttjande.",
                    weight=LEVEL_3_RANGE
                ),
                Alternative(
                    text="Allvarlig konsekvens: exponering kan leda till diskriminering, hot, ekonomisk skada eller tydligt stigma.",
                    weight=LEVEL_4_RANGE
                ),
                Alternative(
                    text="Mycket allvarlig konsekvens: omfattande/storskalig spridning eller särskilt känslig exponering med långvarig skada och svår upprättelse.",
                    weight=LEVEL_5_RANGE
                ),
            ]
        ),
        Question(
            text="Hur allvarlig blir konsekvensen för den registrerade av otillåten användning (secondary use) eller behandling utanför förväntat ändamål?",
            alternatives=[
                Alternative(
                    text="Ingen eller försumbar konsekvens: användningen avviker inte meningsfullt från förväntan eller påverkar inte individen.",
                    weight=LEVEL_1_RANGE
                ),
                Alternative(
                    text="Begränsad konsekvens: begränsad avvikelse från ändamål med liten påverkan (t.ex. obetydlig extra behandling).",
                    weight=LEVEL_2_RANGE
                ),
                Alternative(
                    text="Påtaglig konsekvens: användning utanför ändamål påverkar individens integritet, valfrihet eller situation påtagligt.",
                    weight=LEVEL_3_RANGE
                ),
                Alternative(
                    text="Allvarlig konsekvens: systematisk otillåten användning med betydande påverkan (t.ex. beslut, selektion, orättvis behandling).",
                    weight=LEVEL_4_RANGE
                ),
                Alternative(
                    text="Mycket allvarlig konsekvens: omfattande och långvarig otillåten användning som skapar varaktig utsatthet eller mycket svår skada.",
                    weight=LEVEL_5_RANGE
                ),
            ]
        ),

        Question(
            text="Hur allvarlig blir konsekvensen för den registrerade av förlust av kontroll och begränsad möjlighet att utöva sina rättigheter (insyn, rättelse, radering m.m.)?",
            alternatives=[
                Alternative(
                    text="Ingen eller försumbar konsekvens: individen kan fullt ut utöva sina rättigheter utan faktisk påverkan.",
                    weight=LEVEL_1_RANGE
                ),
                Alternative(
                    text="Begränsad konsekvens: mindre hinder eller fördröjning utan bestående negativ effekt.",
                    weight=LEVEL_2_RANGE
                ),
                Alternative(
                    text="Påtaglig konsekvens: individen får tydligt försämrad kontroll/insyn som påverkar trygghet eller handlingsutrymme.",
                    weight=LEVEL_3_RANGE
                ),
                Alternative(
                    text="Allvarlig konsekvens: flera rättigheter blir i praktiken svåra att utöva; individen riskerar påtaglig skada p.g.a. bristande kontroll.",
                    weight=LEVEL_4_RANGE
                ),
                Alternative(
                    text="Mycket allvarlig konsekvens: individen saknar i praktiken möjlighet till upprättelse/korrigering; kontrollförlusten blir varaktig.",
                    weight=LEVEL_5_RANGE
                ),
            ]
        ),

        Question(
            text="Hur allvarlig blir den samlade skadan för den registrerade (materiell och/eller immateriell)?",
            alternatives=[
                Alternative(
                    text="Ingen eller försumbar skada: ingen märkbar olägenhet eller negativ påverkan.",
                    weight=LEVEL_1_RANGE
                ),
                Alternative(
                    text="Begränsad skada: tillfälligt obehag, oro eller administrativ belastning.",
                    weight=LEVEL_2_RANGE
                ),
                Alternative(
                    text="Påtaglig skada: tydlig negativ påverkan på privatliv, relationer, ekonomi eller social situation.",
                    weight=LEVEL_3_RANGE
                ),
                Alternative(
                    text="Allvarlig skada: diskriminering, ekonomisk förlust, hot/utpressning eller betydande social/psykisk påverkan.",
                    weight=LEVEL_4_RANGE
                ),
                Alternative(
                    text="Mycket allvarlig skada: långvarig eller irreversibel påverkan på livssituation (t.ex. varaktig utsatthet, skyddsbehov, djup stigmatisering).",
                    weight=LEVEL_5_RANGE
                ),
            ]
        ),

        Question(
            text="Hur allvarlig blir konsekvensen för den registrerade av intrång i privatliv/personlig sfär (övervakning, kartläggning, oönskad exponering)?",
            alternatives=[
                Alternative(
                    text="Ingen eller försumbar konsekvens: intrånget upplevs inte och ger ingen faktisk påverkan.",
                    weight=LEVEL_1_RANGE
                ),
                Alternative(
                    text="Begränsad konsekvens: begränsat intrång som ger mindre obehag men ingen bestående effekt.",
                    weight=LEVEL_2_RANGE
                ),
                Alternative(
                    text="Påtaglig konsekvens: intrånget påverkar trygghet eller beteende (t.ex. självcensur) på ett märkbart sätt.",
                    weight=LEVEL_3_RANGE
                ),
                Alternative(
                    text="Allvarlig konsekvens: intrånget är omfattande och leder till stress/rädsla eller påtaglig försämring av livskvalitet.",
                    weight=LEVEL_4_RANGE
                ),
                Alternative(
                    text="Mycket allvarlig konsekvens: genomgripande och långvarigt intrång (systematisk övervakning/kartläggning) med varaktig påverkan.",
                    weight=LEVEL_5_RANGE
                ),
            ]
        ),

        Question(
            text="Hur allvarlig blir konsekvensen för den registrerade om känsliga uppgifter (särskilt hälsodata) exponeras eller används på ett sätt som kan skapa stigma eller ökad sårbarhet?",
            alternatives=[
                Alternative(
                    text="Ingen eller försumbar konsekvens: inga känsliga uppgifter berörs eller exponeringen saknar praktisk betydelse.",
                    weight=LEVEL_1_RANGE
                ),
                Alternative(
                    text="Begränsad konsekvens: mindre känslig hälsoinformation eller begränsad exponering med liten risk för stigma.",
                    weight=LEVEL_2_RANGE
                ),
                Alternative(
                    text="Påtaglig konsekvens: exponering kan ge tydlig oro, skam eller påverka viljan att söka vård/vara öppen i vårdsituationer.",
                    weight=LEVEL_3_RANGE
                ),
                Alternative(
                    text="Allvarlig konsekvens: exponering/otillåten användning kan leda till diskriminering, hot eller betydande stigma (t.ex. på arbetsplats/socialt).",
                    weight=LEVEL_4_RANGE
                ),
                Alternative(
                    text="Mycket allvarlig konsekvens: särskilt känslig kontext (t.ex. psykiatri, beroende, skyddade identiteter, våldsutsatthet) med långvarig och svår skada.",
                    weight=LEVEL_5_RANGE
                ),
            ]
        ),
    ]
    conquestions = Questionaire(factor="lm", questions=cons)
    q = Questionaires(tef=tef, vuln=vuln, lm=conquestions)
    json.dump(q.to_dict(), codecs.open('data/questionaires/privacy.json', 'w', encoding='utf-8'), cls=ComplexEncoder)