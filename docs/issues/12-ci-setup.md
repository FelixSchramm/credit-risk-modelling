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
   - Python-Version festlegen (z. B. via `actions/setup-python`).
   - `pip install -r requirements.txt`.
   - Linting ausführen (z. B. `ruff check .` oder `flake8`) — Tool-Wahl an
     `requirements.txt`/Team-Präferenz anpassen.
   - `pytest tests/` ausführen (aus Issue 05).
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
