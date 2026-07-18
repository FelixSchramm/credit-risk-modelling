# Issue 03: Notebook-Logik in wiederverwendbare Module unter `src/` auslagern

**Priorität:** P1 (Struktur/Professionalität)
**Status:** Open
**Betrifft:** `01_notebooks/prediction.ipynb`, Umbenennung `03_src/` → `src/`, neu: `src/*.py`

## Kontext

Aktuell besteht das gesamte Projekt aus einem einzigen Jupyter-Notebook
(`01_notebooks/prediction.ipynb`). Es gibt keine wiederverwendbaren Funktionen/Module —
`03_src/` existiert im Repo nur als leerer Platzhalter (`.gitkeep`), obwohl die README
bereits (fälschlich) Dateien wie `03_src/01_process_data.py` beschreibt (siehe Issue 02).

Für ein Portfolio-Repo im Bank-/Data-Science-Kontext wird erwartet, dass Kernlogik in
testbare, importierbare Python-Module ausgelagert ist — nicht nur in Notebook-Zellen.
Das zeigt Software-Engineering-Reife, die über reines Notebook-Prototyping hinausgeht.

## Wichtig: `03_src` ist kein gültiger Python-Package-Name

Python-Modul- und Package-Namen dürfen nicht mit einer Ziffer beginnen —
`import 03_src.data_processing` ist ein Syntaxfehler. Deshalb als erster Schritt:
**`03_src/` in `src/` umbenennen** (`git mv 03_src src`). Das Nummernschema der übrigen
Ordner (`01_notebooks/`, `02_data/`, `04_models/`) kann bleiben — nur der importierbare
Code braucht einen gültigen Namen. Die README (Folder Structure, siehe Issue 02) und die
Pfadangaben in den Issues 05/07/09 beziehen sich dann auf `src/`.

(Alternative, falls das Nummernschema unbedingt vollständig erhalten bleiben soll: ein
Package mit gültigem Namen unterhalb von `03_src/` anlegen, z. B. `03_src/credit_risk/`,
und `03_src` zum `sys.path` hinzufügen. Die Umbenennung nach `src/` ist aber die
einfachere und üblichere Lösung.)

## Ziel

Kernlogik aus dem Notebook in Module unter `src/` extrahieren; das Notebook wird
dadurch schlanker und dient primär noch EDA/Storytelling/Visualisierung, während es die
eigentliche Verarbeitung/das Training über Funktionsaufrufe aus `src/` erledigt.

## Vorgeschlagene Modulstruktur

- `src/data_processing.py`
  - Laden der Rohdaten
  - Fehlende Werte behandeln (inkl. der bestehenden `rm_nas(df, threshold=0.4)`-Funktion
    aus dem Notebook, 1:1 übernehmen und mit Docstring versehen)
  - Leakage-Spalten droppen (Liste aus Issue 01 verwenden, sobald umgesetzt)
- `src/features.py`
  - Feature Engineering (z. B. Encoding kategorialer Variablen, abgeleitete Features)
- `src/train.py`
  - Train/Test-Split
  - Modelltraining (RandomForestClassifier, ggf. später weitere Modelle aus Issue 09)
  - Modell-Persistierung (z. B. `joblib.dump` nach `04_models/`)
- `src/evaluate.py`
  - Metrikberechnung (ROC AUC, Classification Report; später KS/Gini/Kalibrierung aus
    Issue 07)

## Umsetzungsschritte

1. `03_src/` in `src/` umbenennen (`git mv 03_src src`) und eine `__init__.py` anlegen,
   damit `src` ein importierbares Package ist; README-Ordnerstruktur anpassen (Issue 02).
2. Notebook-Zellen durchgehen und Logik den obigen Modulen zuordnen.
3. Jede Funktion mit sprechendem Namen, Type Hints und kurzem Docstring versehen.
4. Module so schreiben, dass sie **ohne Notebook-Kontext importierbar** sind (kein Zugriff
   auf Notebook-globale Variablen, alle Abhängigkeiten als Funktionsparameter).
5. Notebook umbauen: Zu Beginn `from src.data_processing import ...` statt Inline-Code;
   EDA-Zellen (Plots, `describe()`, etc.) bleiben im Notebook. Da das Notebook in
   `01_notebooks/` liegt, das Projekt-Root zum Suchpfad hinzufügen — am einfachsten
   `sys.path.insert(0, "..")` in der ersten Zelle; alternativ das Projekt via
   `pip install -e .` installierbar machen (`pyproject.toml`, siehe Issue 06).
6. Notebook einmal komplett neu durchlaufen lassen ("Restart & Run All"), um sicherzustellen,
   dass der Umbau funktioniert (siehe auch Issue 04).

## Betroffene Dateien

- `01_notebooks/prediction.ipynb`
- Umbenennung: `03_src/` → `src/`
- Neu: `src/__init__.py`, `src/data_processing.py`, `src/features.py`, `src/train.py`,
  `src/evaluate.py` (Namen/Aufteilung können bei Umsetzung sinnvoll angepasst werden)
- `README.md` (Folder Structure, zusammen mit Issue 02)

## Akzeptanzkriterien / Definition of Done

- [ ] `03_src/` existiert nicht mehr; Kernlogik (Datenverarbeitung, Feature Engineering,
      Training, Evaluation) liegt in importierbaren `.py`-Modulen unter `src/`, nicht mehr
      nur im Notebook.
- [ ] Jede öffentliche Funktion hat Type Hints und einen kurzen Docstring.
- [ ] Notebook importiert diese Module und läuft sauber durch.
- [ ] Module lassen sich unabhängig vom Notebook importieren (Voraussetzung für Issue 05,
      Unit-Tests).
