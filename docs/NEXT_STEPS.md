# Next Steps: Folgeprojekt Mortgage-PD (Freddie Mac)

Geplantes zweites Portfolio-Projekt nach Abschluss dieses Repos. Ziel der
Bewerbungsmappe: zwei Kreditrisiko-Projekte, die zusammen Konsumkredite
(dieses Repo, LendingClub) und Hypotheken (neues Projekt, Freddie Mac)
abdecken — Letzteres mit direktem Bezug zum hypothekenlastigen Schweizer
Bankenmarkt (Kantonalbanken, Raiffeisen, UBS).

## Zeitpunkt

**Start erst, wenn dieses Projekt vollständig abgeschlossen ist**, d. h.:

1. Alle Issues #2–#13 sind umgesetzt und gemerged.
2. Der Sammel-PR vom Integrations-Branch nach `main` ist gemerged
   (dabei: Session-Protokoll-Teile aus CLAUDE.md und `docs/handovers/`
   entfernen bzw. nicht mitmergen — internes Arbeitsmaterial).
3. Die Fallback-Routine in Claude Code Web ist deaktiviert.
4. Im README dieses Repos steht ein Ausblick-Satz, z. B.:
   "Next: mortgage PD on Freddie Mac loan-level data (vintage analysis,
   TTC vs. PIT calibration)."

Realistischer Startzeitpunkt bei laufendem Relay: **September/Oktober 2026**.

## Datensatz: Freddie Mac Single-Family Loan-Level Dataset

- **Inhalt:** Loan-Level-Daten zu ca. 55 Mio. US-Hypotheken, Origination
  1999 bis ~2025Q3, mit monatlicher Performance-Historie je Kredit bis zur
  Abwicklung (Delinquency-Status, Prepayment, Default/Disposition).
  Quartalsweise aktualisiert.
- **Zugang:** kostenlos nach Registrierung bei "Clarity Data Intelligence"
  (Freddie Mac): https://freddiemac.com/research/datasets/sf-loanlevel-dataset
  Dort verfügbar: Full Dataset, Standard Dataset nach Jahrgang,
  Non-Standard Dataset, **Sample-Files** (für den Einstieg zwingend die
  Samples nehmen — das Volldataset umfasst mehrere hundert GB).
- **Format:** pro Quartal/Jahrgang zwei Dateitypen:
  1. *Origination file* — statische Merkmale bei Vergabe (FICO, LTV, DTI,
     Zins, Zweck, Bundesstaat, ...). Nur diese Felder sind legitime
     PD-Features (Lehre aus Issue #2 dieses Repos: keine
     Post-Origination-Spalten ins Feature-Set).
  2. *Monthly performance file* — Zeitreihe je Kredit (Saldo,
     Delinquency-Status, Zero-Balance-Code). Hieraus wird das **Label**
     abgeleitet (z. B. Default = 90+ Tage delinquent innerhalb von
     24/36 Monaten nach Origination), niemals ein Feature.
- **Alternative-Kandidaten** (geprüft am 2026-08-28, bewusst nachrangig):
  - *Fannie Mae Single-Family Loan Performance Data* — gleichwertig,
    Freddie Mac ist besser dokumentiert für Einsteiger.
  - *Home Credit — Credit Risk Model Stability* (Kaggle 2024) — moderne
    Konsumkreditdaten mit Fokus Modellstabilität/Drift; gute Wahl, falls
    stattdessen die Monitoring-/Validation-Schiene gezeigt werden soll.
  - *Bondora P2P* (europäisch) und *Amex Default Prediction* (Features
    anonymisiert → für Interpretierbarkeits-Story ungeeignet) — verworfen.

## Was das Projekt zeigen soll (Scope-Skizze)

1. **Data Engineering:** Origination- und Performance-Dateien zu einem
   modellierbaren Datensatz verarbeiten (Label-Definition aus der
   Zeitreihe, Parquet-Pipeline, Arbeit mit Samples statt Volldaten).
2. **PD-Modell** auf reinen Origination-Features (Scorecard + Challenger-
   Modell, wie in diesem Repo etabliert).
3. **Vintage-/Kohortenanalyse:** Ausfallraten je Origination-Jahrgang —
   Finanzkrise 2007–2009, Covid 2020, Zinswende 2022+ sichtbar machen.
4. **TTC vs. PIT:** Diskussion Through-the-Cycle- vs.
   Point-in-Time-Kalibrierung anhand der Jahrgänge (Anschluss an
   Basel/IFRS9-Abschnitt aus Issue #11).
5. **Wiederverwendung des Agenten-Setups:** gleiche Vorgehensweise wie
   hier — erst Repo-Review + Issues, dann CLAUDE.md/CLAUDE_CODING_RULES.md
   (aus diesem Repo übernehmen), HANDOVER.md, Worker/Reviewer-Relay und
   Fallback-Routine.

## Offene Punkte vor dem Start

- [ ] Freddie-Mac-Registrierung anlegen, Nutzungsbedingungen prüfen
      (Redistribution der Rohdaten ist untersagt — Rohdaten daher NICHT
      ins Repo committen, nur Code + aggregierte Ergebnisse).
- [ ] Entscheiden: eigenes neues Repo (empfohlen, z. B.
      `mortgage-risk-modelling`) statt Erweiterung dieses Repos.
- [ ] Sample-Umfang festlegen (z. B. 2–3 Jahrgänge + Sample-Files), damit
      Cloud-Sessions mit Speicher-/RAM-Limits arbeiten können.
