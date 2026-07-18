# Issue 13: Git-Workflow-Empfehlungen für zukünftige Änderungen

**Priorität:** P3 (Politur)
**Status:** Open
**Betrifft:** Arbeitsweise/Prozess, keine konkrete Datei

## Kontext

Die bisherige Git-Historie des Repos besteht aus 9 Commits an zwei aufeinanderfolgenden
Tagen (2025-09-03/04), von einem Autor, ohne Feature-Branches oder Pull Requests. Die
Commit-Messages sind größtenteils wenig aussagekräftig ("Update README.md" mehrfach
hintereinander, "Folder Struture" mit Tippfehler, eine Merge-Message mit einem
versehentlichen `#`-Zeichen: `M#erge branch 'main' of ...`). Das wirkt wie ein schnell
hochgeladenes Projekt statt ein über Zeit gepflegtes Repository — für Bewerbungszwecke ist
eine saubere, nachvollziehbare Historie aber ein zusätzliches (kleines) Glaubwürdigkeitssignal.

Diese Issue ist **kein Code-Fix**, sondern eine Prozessempfehlung für die Umsetzung der
übrigen Issues (01–12) sowie für zukünftige Änderungen an diesem Repo.

## Ziel

Ab sofort (beginnend mit der Umsetzung der Issues 01–12) eine sauberere, aussagekräftigere
Git-Historie führen.

## Empfehlungen

1. **Ein Feature-Branch pro Issue** (oder pro sinnvoll zusammenhängender Gruppe von
   Issues), statt alles direkt auf `main`/einen einzigen Branch zu committen — analog zu
   diesem Dokumentations-PR, der bereits auf einem eigenen Branch liegt.
2. **Aussagekräftige Commit-Messages** im Format `<Kurzbeschreibung im Imperativ>` (z. B.
   `Fix data leakage by dropping post-outcome columns`, nicht `update` oder `fix`).
   Bei Bedarf einen kurzen Body ergänzen, der das *Warum* erklärt.
3. **Pull Requests statt Direct Push** für inhaltliche Änderungen — auch als Einzelperson
   sinnvoll, weil es die Historie in überschaubare, review-bare Einheiten aufteilt und in
   Bewerbungsgesprächen als "so arbeite ich auch im Team" gezeigt werden kann.
4. Commits klein und fokussiert halten (ein Commit = eine logische Änderung), statt große
   Sammel-Commits über mehrere Themen hinweg.
5. Keine nachträgliche Bereinigung der bereits bestehenden alten Historie (kein
   `rebase`/Force-Push auf `main`) — das öffentliche Umschreiben von Historie ist riskant
   und für ein Portfolio-Repo nicht nötig; die alte Historie zeigt lediglich die
   Lernkurve, was in einem Bewerbungskontext auch legitim ist. Der Fokus liegt auf
   *zukünftigen* Commits.

## Betroffene Dateien

Keine — dies ist eine Prozess-/Workflow-Empfehlung.

## Akzeptanzkriterien / Definition of Done

- [ ] Ab der Umsetzung von Issue 01 werden neue, inhaltliche Änderungen über
      Feature-Branches und (wo sinnvoll) Pull Requests eingebracht.
- [ ] Neue Commit-Messages folgen einem klaren, aussagekräftigen Format.
