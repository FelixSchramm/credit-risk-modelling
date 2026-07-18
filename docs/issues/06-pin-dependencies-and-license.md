# Issue 06: Dependencies pinnen und LICENSE ergänzen

**Priorität:** P1 (Struktur/Professionalität)
**Status:** Open
**Betrifft:** `requirements.txt`, neu: `LICENSE`

## Kontext

`requirements.txt` existiert bereits, listet aber Pakete ohne Versionsangabe
(`pandas`, `numpy`, `scikit-learn`, `jupyter`, `matplotlib`, `seaborn`). Das bedeutet: Ein
"Restart & Run All" in einer Umgebung mit neueren Paketversionen kann jederzeit brechen
(z. B. durch API-Änderungen in scikit-learn), ohne dass das im Repo nachvollziehbar wäre.
Außerdem fehlt eine LICENSE-Datei — für ein öffentliches Portfolio-Repo unüblich und
rechtlich unklar (was dürfen Dritte mit dem Code tun?).

## Ziel

Reproduzierbare, versionsfixierte Abhängigkeiten sowie eine klare, offene Lizenz.

## Umsetzungsschritte

1. In der (nach Issue 03/05 final genutzten) Entwicklungsumgebung
   `pip freeze > requirements.txt` ausführen oder gezielt die tatsächlich genutzten
   Top-Level-Pakete mit konkreten Versionen versehen (z. B. `pandas==2.2.2`), statt eines
   vollständigen `pip freeze`-Dumps mit allen transitiven Abhängigkeiten — für ein
   Portfolio-Projekt ist eine kuratierte, lesbare Liste besser als ein automatischer Dump.
2. Neu hinzugekommene Pakete aus anderen Issues ergänzen: `pytest` (Issue 05), `shap`
   (Issue 08), ggf. `scikit-learn`-Erweiterungen für WOE/IV (Issue 09), `flake8`/`ruff`
   (Issue 12).
3. Prüfen, ob ein Wechsel zu `pyproject.toml` (z. B. mit `uv` oder `poetry`) sinnvoll ist —
   optional, `requirements.txt` mit gepinnten Versionen ist ausreichend und einfacher zu
   reviewen.
4. `LICENSE`-Datei im Repo-Root ergänzen. Empfehlung: MIT-Lizenz (üblich für
   Portfolio-/Lernprojekte, erlaubt uneingeschränkte Weiterverwendung mit Attribution).
   Copyright-Zeile mit Namen und aktuellem Jahr.
5. In der README einen kurzen Lizenz-Hinweis/Badge ergänzen (optional, aber üblich).

## Betroffene Dateien

- `requirements.txt`
- Neu: `LICENSE`
- `README.md` (optionaler Lizenz-Hinweis)

## Akzeptanzkriterien / Definition of Done

- [ ] Alle Einträge in `requirements.txt` haben eine feste Versionsangabe.
- [ ] Eine frische virtuelle Umgebung mit `pip install -r requirements.txt` und
      anschließendem Notebook-Lauf funktioniert fehlerfrei.
- [ ] `LICENSE`-Datei ist vorhanden und im Repo sichtbar (z. B. GitHub zeigt die Lizenz im
      Repo-Header an).
