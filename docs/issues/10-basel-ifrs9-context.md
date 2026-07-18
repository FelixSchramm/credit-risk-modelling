# Issue 10: Basel/IFRS9-Einordnung ergänzen

**Priorität:** P2 (Fachliche Tiefe — Differenzierung für Banking-Rollen)
**Status:** Open
**Betrifft:** `README.md`, ggf. `01_notebooks/prediction.ipynb`

## Kontext

Das Projekt sagt im Kern eine **Probability of Default (PD)** vorher, ordnet dies aber
nirgends in den regulatorischen Kontext ein, in dem PD-Modelle bei Banken tatsächlich
eingesetzt werden (Basel-Rahmenwerk für Eigenkapitalanforderungen, IFRS9 für
Risikovorsorge/Provisionierung). Ein kurzer, korrekt eingeordneter Abschnitt dazu zeigt
Branchenverständnis, ohne dass das Projekt selbst ein vollständiges
Regulatorik-konformes Modell sein muss.

## Ziel

Ein kompakter, sachlich korrekter Abschnitt (in README und/oder Notebook), der das
Projekt als vereinfachtes PD-Modell einordnet und den Bezug zu Basel/IFRS9 herstellt —
ohne zu behaupten, das Projekt erfülle tatsächliche regulatorische Anforderungen.

## Umsetzungsschritte

1. Kurzen Abschnitt "Regulatorischer Kontext" (oder Teil des Einleitungsabschnitts)
   ergänzen, der erklärt:
   - PD (Probability of Default) ist einer der drei Kernbausteine der
     Basel-Risikogewichtung (neben LGD – Loss Given Default – und EAD – Exposure at
     Default). Dieses Projekt modelliert **nur** PD, nicht LGD/EAD.
   - Unter IFRS9 wird PD u. a. zur Berechnung erwarteter Kreditverluste (Expected Credit
     Loss, ECL) verwendet — insbesondere für die Einstufung in "Stage 1/2/3".
   - Explizit klarstellen: Dies ist ein **Lern-/Portfolio-Projekt** mit einem öffentlichen
     historischen Datensatz, **kein** aufsichtsrechtlich abgenommenes Modell (keine
     Through-the-Cycle/Point-in-Time-Kalibrierung, keine Validierung nach
     Bankenaufsichtsstandards). Diese Ehrlichkeit ist wichtiger als übertriebene Ansprüche.
2. Falls gewünscht, im Notebook an der Stelle der finalen Metriken einen Satz ergänzen,
   der den erzielten AUC/Gini in Bezug zu üblichen Bandbreiten publizierter
   Retail-Credit-Scoring-Modelle setzt (mit Vorsicht formuliert, keine falschen
   Vergleichsansprüche).
3. Sicherstellen, dass keine falschen/übertriebenen regulatorischen Aussagen entstehen
   (z. B. nicht behaupten, das Modell sei "IFRS9-konform").

## Betroffene Dateien

- `README.md`
- optional `01_notebooks/prediction.ipynb`

## Akzeptanzkriterien / Definition of Done

- [ ] Abschnitt erklärt PD/LGD/EAD-Einordnung und den Basel/IFRS9-Bezug korrekt und knapp.
- [ ] Es wird klar kommuniziert, dass es sich um ein Lernprojekt handelt, nicht um ein
      regulatorisch abgenommenes Modell.
