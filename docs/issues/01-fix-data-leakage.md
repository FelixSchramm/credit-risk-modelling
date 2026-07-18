# Issue 01: Data Leakage im Kreditausfall-Modell beheben

**Priorität:** P0 (kritisch — vor jeder Bewerbung zwingend zu beheben)
**Status:** Open
**Betrifft:** `01_notebooks/prediction.ipynb`

## Kontext

Dieses Repo ist ein Portfolio-Projekt für Bewerbungen im Bereich Data Science /
Credit Risk bei Banken. Das aktuelle Notebook trainiert einen `RandomForestClassifier`
auf dem LendingClub-Datensatz (`accepted_2007_to_2018Q4.csv`) zur Vorhersage von
"Charged Off"-Krediten und meldet in der README einen **ROC AUC von 0.9999**.

Ein AUC von nahezu 1.0 ist bei diesem Datensatz kein Erfolg, sondern ein bekanntes
Warnsignal für **Data Leakage**: Es gibt in diesem Datensatz mehrere Spalten, die erst
*nachdem* der Ausfall/die Tilgung bereits eingetreten ist, bekannt sind. Wenn diese als
Features im Training verwendet werden, "verrät" das Modell im Grunde das Ziel an sich
selbst.

## Problem

Im Notebook werden aktuell folgende Spalten vor dem Training entfernt:

```python
cols_to_drop = ['id', 'member_id', 'grade', 'sub_grade', 'emp_title', 'url', 'zip_code', 'title',
    'loan_status', 'issue_d', 'earliest_cr_line', 'last_pymnt_d', 'last_credit_pull_d']
```

Das reicht nicht aus. Folgende **Post-Origination-/Post-Outcome-Spalten** sind im Datensatz
vorhanden und werden aktuell **nicht** gedroppt, obwohl sie erst nach Kreditvergabe bzw.
nach (Teil-)Ausfall bekannt sind:

- `total_pymnt`, `total_pymnt_inv`
- `total_rec_prncp`, `total_rec_int`, `total_rec_late_fee`
- `out_prncp`, `out_prncp_inv`
- `recoveries`, `collection_recovery_fee`
- `last_pymnt_amnt`
- `last_fico_range_high`, `last_fico_range_low` — der nach Origination laufend
  aktualisierte FICO-Score; bei ausgefallenen Krediten ist er bereits eingebrochen und
  damit einer der stärksten Leakage-Treiber in diesem Datensatz. **Nicht** zu verwechseln
  mit `fico_range_low`/`fico_range_high` (ohne `last_`): Das sind die Origination-Werte,
  die als legitime Features im Modell bleiben dürfen.
- `debt_settlement_flag`
- alle `hardship_*`-Spalten (z. B. `hardship_amount`, `hardship_payoff_balance_amount`, `hardship_flag`, `hardship_type`, `hardship_status`, ...)
- ggf. weitere `settlement_*`-Spalten (Debt-Settlement-Infos), falls im geladenen Datensatz vorhanden

**Hinweis zur Erwartungshaltung:** Spalten mit sehr hohem Missing-Anteil (viele
`hardship_*`- und `settlement_*`-Felder) werden vermutlich bereits durch den bestehenden
`rm_nas(df, threshold=0.4)`-Filter entfernt. Sie trotzdem explizit in die Drop-Liste
aufzunehmen ist richtig (defensive Deny-List, unabhängig von Filter-Reihenfolge und
Threshold). Die eigentlichen Treiber des 0.9999-AUC sind aber die voll befüllten Spalten
(`total_pymnt`, `recoveries`, `out_prncp`, `last_pymnt_amnt`, `last_fico_range_*`), die
den NaN-Filter überleben.

## Ziel

Ein Modell, das ausschließlich Features verwendet, die **zum Zeitpunkt der
Kreditvergabe** (Origination) bekannt sind — so wie es in der Praxis bei einem echten
PD-Scoring-Modell auch sein muss. Der resultierende AUC wird deutlich niedriger sein
(typisch für Credit-Default-Modelle auf vergleichbaren Datensätzen: grob 0.65–0.75) —
das ist der *korrekte*, glaubwürdige Wert.

## Umsetzungsschritte

1. Alle oben genannten Post-Outcome-Spalten identifizieren (per `df.columns` und
   Kreuzcheck mit der LendingClub-Datendokumentation) und in die Drop-Liste aufnehmen.
2. Zusätzlich systematisch prüfen: Gibt es weitere Spalten, die im Rohdatensatz erst nach
   Origination befüllt werden (z. B. Payment-Plan-Felder, Debt-Settlement-Felder,
   `next_pymnt_d`)? Diese ebenfalls droppen.
3. Modell mit dem bereinigten Feature-Set neu trainieren (gleicher Split/Random State wie
   bisher, damit die Ergebnisse vergleichbar bleiben).
4. Neue Metriken (ROC AUC, Precision/Recall, Confusion Matrix) im Notebook dokumentieren.
5. Im Notebook eine kurze Markdown-Sektion ergänzen, die den ursprünglichen Leakage-Fund
   transparent macht: "Erste Version hatte Leakage über Post-Outcome-Spalten (AUC 0.9999);
   nach Bereinigung realistischer AUC von X.XX." — das zeigt im Bewerbungskontext aktiv
   Verständnis für ein zentrales Credit-Risk-Modellierungsproblem.
6. README (siehe Issue 02) mit dem neuen, korrekten AUC-Wert aktualisieren.

## Betroffene Dateien

- `01_notebooks/prediction.ipynb`
- `README.md` (AUC-Wert, siehe Issue 02)

## Akzeptanzkriterien / Definition of Done

- [ ] Keine Post-Outcome-/Post-Origination-Spalte ist mehr im Feature-Set des Modells.
- [ ] Notebook läuft sauber von oben nach unten durch ("Restart & Run All") und produziert
      reproduzierbar den neuen, realistischen AUC-Wert.
- [ ] Notebook enthält eine kurze, ehrliche Erklärung des ursprünglichen Leakage-Problems
      und der Korrektur.
- [ ] README-Metriken sind konsistent mit dem Notebook-Output.
