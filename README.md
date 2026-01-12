# Risk Analysis UI

Risk Analysis UI är ett webbaserat gränssnitt för att **skapa och visa riskanalyser**.
Applikationen används för att dokumentera riskscenarion och stödja strukturerade riskbedömningar.

Tanken är att göra det enkelt att ta fram risker genom att ge användaren möjlighet att välja aktör, hot 
och sårbarhet från dropdowns för att enkelt kunna formulera riskbeskrivningen och sedan via frågeformulär
ta fram värden för sannolikhet, konsekvens och sammantagen risk samtidigt som bakgrunden till värdena
dokumenteras genom att frågorna och svaren lagras tillsammans med riskbeskrivningen.

Applikationen stödjer både diskreta (1-5) och kontinuerliga (förväntad årlig förlust) risknivåer.

---

## Vad kan man göra?

- Skapa, redigera och visa riskanalyser
- Lägga till riskscenarion med:
  - beskrivning av hot, aktör, sårbarhet och tillgång
  - riskbedömning via frågeformulär
- Arbeta stegvis (wizard) innan analysen sparas
- Återanvända standardiserade hot, aktörer och sårbarheter
- Basbeskrivning (namn) på riskscenario kan automatgenereras på formen
```
Risk att {aktör} utnyttjar {sårbarhet} för att realisera {hot} mot {tillgång}.
```

## OBS!

De värden som används i de medföljande frågeformulären under `data/questionaires` är enbart avsedda som exempel.
Värdena har inte tagits fram genom någon djupare analys av sannolikheter eller trösklar för organisationer och måste
därför anpassas utifrån användarens verklighet.
Men de är valda som hyfsat realistiska utgångsvärden.

---

## Under huven

Basen är frågeformulären som består av ett variabelt antal frågor med ett variabelt antal svarsalternativ. 
Varje alternativ har ett intervall kopplat till sig på formen {min, sannolikt, max}. Frågeformulären består av tre delar;
en del för att ta fram hur ofta hotaktören har teoretisk möjlighet att försöka verkställa hotet (kontaktförsök), en del 
för att bedöma sannolikheten att hotet faktiskt verkställs (sårbarhet) och en del för att bedöma konsekvensen om hotet
verkställs.
Anledningen till att intervaller används istället för att ha fasta enskilda värden är för att det alltid kommer finnas
naturliga variatoner och en osäkerhet i bedömningarna. För att ytterligare ta höjd för detta slumpas ett antal 
värden under en PERT-fördelning inom det resulterande intervallet och 90%-kvartilen används för att sätta det slutliga
värdet på risken.

Tankesättet är till stora delar inspirerat och baserat på FAIR (Factor Analysis in Information Risk), men med inställningen
att försöka göra kvalificerade gissningar som är tillräckligt nära verkligheten utan att behöva göra djuplodande
undersökningar för att ta fram nivåerna för respektive faktor.

---

## Teknik (kort)

- Backend: Python + FastAPI
- UI: Server-renderad HTML
- Lagring: JSON-filer

### Körning

```
pip3 install fastapi uvicorn jinja2 python-multipart numpy
python3 app.py
```

#### Förbyggda binärer

Det finns körbara binärer byggda med pyinstall för windows (testat på windows 11, bör fungera på windows 10) och Ubuntu (22.04).
Binärerna kan laddas ned från repots release-sida.
Dessa binärer kräver ingen installation av Python eller liknande.

---

## Status

Detta är ett pågående projekt som kontinuerligt utvecklas.
