# Issue 12: CI-Setup (GitHub Actions für Lint/Tests)

**Priorität:** P3 (Politur)
**Status:** Open
**Betrifft:** neu: `.github/workflows/`

## Kontext

Aktuell gibt es keinerlei CI/CD-Konfiguration im Repo. Für ein Portfolio-Repo, das
Software-Engineering-Reife zeigen soll, ist eine einfache CI-Pipeline (Linting + Tests bei
jedem Push/PR) ein sichtbares, leicht zu implementierendes Signal — insbesondere in
Kombination mit den Tests aus Issue 05.

**Voraussetzung:** Sinnvoll erst, nachdem Issue 03 (Modularisierung) und Issue 05
(Unit-Tests) umgesetzt sind — vorher gibt es nichts zu linten/testen außer dem Notebook.

## Ziel

Eine minimale GitHub-Actions-Pipeline, die bei jedem Push/PR automatisch Linting und Tests
ausführt und den Status sichtbar macht (grüner Haken / Badge in der README).

## Umsetzungsschritte

1. `.github/workflows/ci.yml` anlegen mit einem einfachen Job:
   - Python-Version festlegen via `actions/setup-python`, mit `cache: pip`, damit nicht
     jeder Lauf alle Pakete neu herunterlädt.
   - `pip install -r requirements.txt`.
   - Linting mit `ruff check .` ausführen (`ruff` ist der aktuelle Standard und ersetzt
     `flake8`/`isort` vollständig — ein einziges, schnelles Tool genügt).
   - `pytest tests/` ausführen (aus Issue 05). Die Tests laufen laut Issue 05 auf kleinen
     synthetischen DataFrames und brauchen daher den großen Rohdatensatz nicht — die CI
     bleibt so ohne Daten-Download lauffähig.
2. Pipeline bei Push auf `main` und bei Pull Requests triggern lassen.
3. Optional: CI-Status-Badge in der README ergänzen
   (`![CI](https://github.com/<user>/<repo>/actions/workflows/ci.yml/badge.svg)`).
4. Sicherstellen, dass die Pipeline aktuell **grün** ist, bevor sie als "erledigt"
   markiert wird (nicht nur vorhanden, sondern auch tatsächlich bestehend).

## Betroffene Dateien

- Neu: `.github/workflows/ci.yml`
- `README.md` (optionales Badge)

## Akzeptanzkriterien / Definition of Done

- [ ] GitHub-Actions-Workflow vorhanden, der bei Push/PR automatisch Linting + Tests
      ausführt.
- [ ] Workflow läuft bei einem Test-Push tatsächlich grün durch.
