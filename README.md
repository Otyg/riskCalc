# Risk Analysis UI

Risk Analysis UI är ett webbaserat gränssnitt för att **skapa och visa riskanalyser**.
Applikationen används för att dokumentera riskscenarion och stödja strukturerade riskbedömningar.

UI:t är byggt i Python och körs i webbläsaren.

---

## Vad kan man göra?

- Skapa och visa riskanalyser
- Lägga till riskscenarion med:
  - beskrivning av hot, aktör, sårbarhet och tillgång
  - riskbedömning via manuella värden eller frågeformulär
- Återanvända standardiserade hot, aktörer och sårbarheter
- Arbeta stegvis (wizard) innan analysen sparas

---

## Teknik (kort)

- Backend: Python + FastAPI
- UI: Server-renderad HTML
- Lagring: JSON-filer

### Körning

```
pip3 install fastapi uvicorn jinja2 python-multipart numpy
uvicorn app:app --reload
```
---

## Status

Detta är ett pågående projekt som kontinuerligt utvecklas.
