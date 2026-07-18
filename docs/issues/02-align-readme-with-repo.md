# Issue 02: README an tatsächlichen Repo-Inhalt angleichen

**Priorität:** P0 (kritisch — vor jeder Bewerbung zwingend zu beheben)
**Status:** Open
**Betrifft:** `README.md`

## Kontext

Dieses Repo ist ein Portfolio-Projekt für Bewerbungen bei Banken / im Bereich Data
Science. Eine README, die etwas anderes beschreibt als tatsächlich im Repo liegt, ist im
Bewerbungskontext besonders schädlich: Ein Reviewer öffnet das Repo, findet die in der
README genannten Dateien nicht — und der erste Eindruck ist "unfertig" oder
"unglaubwürdig", noch bevor er den eigentlichen Code beurteilt.

## Problem

Die aktuelle README beschreibt im Abschnitt "Folder Structure" (sinngemäß) folgende
Dateien, die im Repo **nicht existieren**:

- `01_notebooks/1.0-eda-and-prototyping.ipynb` — tatsächlich vorhanden ist nur
  `01_notebooks/prediction.ipynb`
- `03_src/01_process_data.py` — `03_src/` enthält nur eine `.gitkeep`-Datei
- `03_src/02_train_model.py` — ebenfalls nicht vorhanden
- `04_models/random_forest_v1.joblib` — `04_models/` enthält nur eine `.gitkeep`-Datei

Außerdem fehlt eine "How to run"-Anleitung: Es ist nicht dokumentiert, dass der Rohdatensatz
separat von Kaggle heruntergeladen und unter `02_data/raw/` abgelegt werden muss, welche
Python-Version/Umgebung nötig ist, oder wie man das Notebook ausführt.

## Ziel

Eine README, die **1:1 dem tatsächlichen Repo-Zustand entspricht** (nachdem die anderen
Issues — insbesondere Issue 03 "Modularize src" — umgesetzt wurden) und die es einer
fremden Person erlaubt, das Projekt ohne Rückfragen nachzuvollziehen und lokal auszuführen.

## Umsetzungsschritte

1. Diese Issue sollte **nach** Issue 01 (Data Leakage) und idealerweise nach Issue 03
   (Modularisierung) umgesetzt werden, damit die README die finale Struktur beschreibt
   und nicht erneut veraltet.
2. Abschnitt "Folder Structure" so aktualisieren, dass er exakt die vorhandenen Dateien
   auflistet (Notebook-Name, ggf. neue `.py`-Module aus `03_src/`, ggf. Modell-Artefakt in
   `04_models/`, falls dort tatsächlich etwas abgelegt wird).
3. Abschnitt "How to run" ergänzen:
   - Link/Hinweis, woher der Rohdatensatz stammt (Kaggle, LendingClub) und wo er abgelegt
     werden muss (`02_data/raw/`).
   - `pip install -r requirements.txt` bzw. Setup-Befehle.
   - Befehl(e) zum Ausführen des Notebooks bzw. der Pipeline-Skripte.
4. Ergebnis-/Metrik-Abschnitt mit dem korrigierten AUC-Wert aus Issue 01 aktualisieren.
5. Kurzen Link/Verweis auf `docs/REPO_REVIEW.md` ist **nicht** nötig — die README richtet
   sich an externe Leser (Recruiter, Interviewer), das Review-Dokument ist internes
   Arbeitsmaterial.

## Betroffene Dateien

- `README.md`

## Akzeptanzkriterien / Definition of Done

- [ ] Jede in der README genannte Datei/jeder genannte Pfad existiert tatsächlich im Repo.
- [ ] Eine Person ohne Vorwissen kann anhand der README das Projekt lokal aufsetzen und
      ausführen.
- [ ] Metriken in der README stimmen mit dem tatsächlichen Notebook-Output überein.
