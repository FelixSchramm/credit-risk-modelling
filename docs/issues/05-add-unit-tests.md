# Issue 05: Unit-Tests für zentrale Funktionen ergänzen

**Priorität:** P1 (Struktur/Professionalität)
**Status:** Open
**Betrifft:** neu: `tests/`, sowie `03_src/*.py`

## Kontext

Aktuell gibt es im gesamten Repo keinerlei Tests — kein `tests/`-Verzeichnis, kein
`pytest`, kein `unittest`. Für ein Portfolio-Projekt im Bank-/Data-Science-Kontext ist das
ein auffälliger Mangel: Testabdeckung (auch nur für die Kernlogik) signalisiert
Software-Engineering-Reife und Sorgfalt, die über reines Notebook-Prototyping hinausgeht.

**Voraussetzung:** Diese Issue baut auf Issue 03 (Modularisierung) auf — Tests ergeben
erst Sinn, sobald Logik als importierbare Funktionen in `03_src/` vorliegt.

## Ziel

Eine Basis-Testsuite (`pytest`) für die wichtigsten, deterministisch testbaren Funktionen
aus `03_src/` — nicht für das gesamte Notebook, sondern gezielt für die Bausteine, bei
denen ein Test echten Mehrwert hat (Datenverarbeitung, Feature Engineering, Metrikberechnung).

## Umsetzungsschritte

1. `tests/`-Verzeichnis im Repo-Root anlegen, mit `test_data_processing.py`,
   `test_features.py`, `test_evaluate.py` (passend zur Modulstruktur aus Issue 03).
2. `pytest` und ggf. `pytest-cov` zu `requirements.txt` hinzufügen (siehe Issue 06).
3. Für `rm_nas(df, threshold=0.4)` (bzw. dessen Nachfolger in `data_processing.py`)
   mindestens folgende Fälle testen:
   - Spalten mit Missing-Anteil über dem Threshold werden korrekt entfernt.
   - Spalten mit Missing-Anteil unter dem Threshold bleiben erhalten.
   - Edge Case: leerer DataFrame, DataFrame ohne fehlende Werte.
4. Für die Leakage-Spalten-Filterung (aus Issue 01) testen, dass alle bekannten
   Post-Outcome-Spalten zuverlässig entfernt werden, auch wenn nicht alle im
   Input-DataFrame vorhanden sind (kein Fehler bei fehlenden Spalten).
5. Für Feature-Engineering-Funktionen: mit einem kleinen synthetischen Beispiel-DataFrame
   (nicht dem echten, großen Datensatz) prüfen, dass Encodings/abgeleitete Features wie
   erwartet berechnet werden.
6. Für Evaluation-Funktionen (sofern in `evaluate.py` eigene Berechnungen stattfinden,
   z. B. KS-Statistik aus Issue 07): mit bekannten Beispielwerten (y_true, y_pred_proba)
   die korrekte Metrikberechnung verifizieren.
7. `pytest` lokal ausführen und sicherstellen, dass alle Tests grün sind.
8. Kurzen Abschnitt in der README ergänzen: wie man die Tests ausführt
   (`pytest tests/`).

## Betroffene Dateien

- Neu: `tests/test_data_processing.py`, `tests/test_features.py`,
  `tests/test_evaluate.py`
- `requirements.txt`
- `README.md` (Testausführung dokumentieren)

## Akzeptanzkriterien / Definition of Done

- [ ] `tests/`-Verzeichnis mit mindestens 3 Testdateien existiert.
- [ ] Mindestens die `rm_nas`/NA-Filter-Funktion und die Leakage-Spalten-Filterung sind
      mit mehreren Fällen (inkl. Edge Cases) abgedeckt.
- [ ] `pytest` läuft lokal ohne Fehler durch.
- [ ] README beschreibt, wie Tests ausgeführt werden.
