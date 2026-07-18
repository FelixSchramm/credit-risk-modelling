# Issue 03: Notebook-Logik in wiederverwendbare Module unter `03_src/` auslagern

**Priorität:** P1 (Struktur/Professionalität)
**Status:** Open
**Betrifft:** `01_notebooks/prediction.ipynb`, neu: `03_src/*.py`

## Kontext

Aktuell besteht das gesamte Projekt aus einem einzigen Jupyter-Notebook
(`01_notebooks/prediction.ipynb`). Es gibt keine wiederverwendbaren Funktionen/Module —
`03_src/` existiert im Repo nur als leerer Platzhalter (`.gitkeep`), obwohl die README
bereits (fälschlich) Dateien wie `03_src/01_process_data.py` beschreibt (siehe Issue 02).

Für ein Portfolio-Repo im Bank-/Data-Science-Kontext wird erwartet, dass Kernlogik in
testbare, importierbare Python-Module ausgelagert ist — nicht nur in Notebook-Zellen.
Das zeigt Software-Engineering-Reife, die über reines Notebook-Prototyping hinausgeht.

## Ziel

Kernlogik aus dem Notebook in Module unter `03_src/` extrahieren; das Notebook wird
dadurch schlanker und dient primär noch EDA/Storytelling/Visualisierung, während es die
eigentliche Verarbeitung/das Training über Funktionsaufrufe aus `03_src/` erledigt.

## Vorgeschlagene Modulstruktur

- `03_src/data_processing.py`
  - Laden der Rohdaten
  - Fehlende Werte behandeln (inkl. der bestehenden `rm_nas(df, threshold=0.4)`-Funktion
    aus dem Notebook, 1:1 übernehmen und mit Docstring versehen)
  - Leakage-Spalten droppen (Liste aus Issue 01 verwenden, sobald umgesetzt)
- `03_src/features.py`
  - Feature Engineering (z. B. Encoding kategorialer Variablen, abgeleitete Features)
- `03_src/train.py`
  - Train/Test-Split
  - Modelltraining (RandomForestClassifier, ggf. später weitere Modelle aus Issue 09)
  - Modell-Persistierung (z. B. `joblib.dump` nach `04_models/`)
- `03_src/evaluate.py`
  - Metrikberechnung (ROC AUC, Classification Report; später KS/Gini/Kalibrierung aus
    Issue 07)

## Umsetzungsschritte

1. Notebook-Zellen durchgehen und Logik den obigen Modulen zuordnen.
2. Jede Funktion mit sprechendem Namen, Type Hints und kurzem Docstring versehen.
3. Module so schreiben, dass sie **ohne Notebook-Kontext importierbar** sind (kein Zugriff
   auf Notebook-globale Variablen, alle Abhängigkeiten als Funktionsparameter).
4. Notebook umbauen: Zu Beginn `from src.data_processing import ...` (o. Ä., je nach
   gewähltem Package-Layout/`sys.path`-Setup) statt Inline-Code; EDA-Zellen (Plots,
   `describe()`, etc.) bleiben im Notebook.
5. Sicherstellen, dass `03_src/` als Python-Package importierbar ist (z. B. `__init__.py`
   oder Ausführung über ein Projekt-Root-relatives Setup — konsistent mit dem, was in
   Issue 06 für Dependency-Management/Projektstruktur festgelegt wird).
6. Notebook einmal komplett neu durchlaufen lassen ("Restart & Run All"), um sicherzustellen,
   dass der Umbau funktioniert (siehe auch Issue 04).

## Betroffene Dateien

- `01_notebooks/prediction.ipynb`
- Neu: `03_src/data_processing.py`, `03_src/features.py`, `03_src/train.py`,
  `03_src/evaluate.py` (Namen/Aufteilung können bei Umsetzung sinnvoll angepasst werden)

## Akzeptanzkriterien / Definition of Done

- [ ] Kernlogik (Datenverarbeitung, Feature Engineering, Training, Evaluation) liegt in
      importierbaren `.py`-Modulen unter `03_src/`, nicht mehr nur im Notebook.
- [ ] Jede öffentliche Funktion hat Type Hints und einen kurzen Docstring.
- [ ] Notebook importiert diese Module und läuft sauber durch.
- [ ] Module lassen sich unabhängig vom Notebook importieren (Voraussetzung für Issue 05,
      Unit-Tests).
