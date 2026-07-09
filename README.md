# Stryktipsprogram

## Beskrivning

Stryktipsprogram är ett skrivbordsprogram utvecklat i Python och Qt för att hantera och analysera Stryktips.

Programmet gör det möjligt att skapa och administrera information om ligor, lag, säsonger, kuponger, tipssystem och spelade vad. Informationen lagras i en SQLite-databas och presenteras i ett grafiskt användargränssnitt.

Programmet är utvecklat enligt MVC-arkitektur (Model–View–Controller), vilket gör koden lättare att underhålla och vidareutveckla.

> **Observera:** Programmet är fortfarande under aktiv utveckling och både funktioner och gränssnitt kan komma att förändras.

---

## Krav

För att köra programmet krävs:

- Python 3.12 eller senare
- PySide6
- SQLite (ingår i Python)
- Ett operativsystem som stöder PySide6 (Windows, Linux eller macOS)

Installera PySide6 med:

```bash
pip install PySide6
```

---

## Starta programmet

Kör programmets startfil från projektets rotkatalog.

Exempel:

```bash
python main.py
```

eller

```bash
python3 main.py
```

beroende på hur Python är installerat.

---

## Projektstruktur

Projektet är uppdelat enligt MVC:

- **Models** – hanterar data och databasen
- **Views** – användargränssnittet
- **Controllers** – kopplar samman modeller och vyer
- **Widgets** – återanvändbara GUI-komponenter
- **Dialogs** – dialogrutor
- **Misc** – gemensamma hjälpfunktioner

---

## Databas

Programmet använder en SQLite-databas för att lagra all information.

---

## Status

Projektet är under aktiv utveckling. Nya funktioner, förbättringar och omstruktureringar tillkommer kontinuerligt.
