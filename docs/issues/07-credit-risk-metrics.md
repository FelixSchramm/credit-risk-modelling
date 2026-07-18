# Issue 07: Credit-Risk-Standardmetriken ergänzen (KS, Gini, Kalibrierung)

**Priorität:** P2 (Fachliche Tiefe — Differenzierung für Banking-Rollen)
**Status:** Open
**Betrifft:** `01_notebooks/prediction.ipynb`, `src/evaluate.py` (sofern Issue 03
bereits umgesetzt)

## Kontext

Aktuell wird das Modell nur mit `roc_auc_score` und `classification_report` bewertet. Im
Credit-Risk-/Banking-Kontext sind das nicht die primär gebräuchlichen Metriken. Wer sich
für eine Rolle im Risikomanagement/Credit Scoring bei einer Bank bewirbt, sollte zeigen,
dass er/sie die dort etablierten Kennzahlen kennt und anwenden kann.

## Ziel

Ergänzung der Standard-Kennzahlen aus dem Credit-Scoring-Bereich, mit kurzer Erklärung
im Notebook, was sie bedeuten und wie sie zu interpretieren sind.

## Umsetzungsschritte

1. **Kolmogorov-Smirnov(KS)-Statistik** berechnen: maximale Differenz zwischen der
   kumulativen Verteilung der vorhergesagten Scores für "Default" vs. "Non-Default".
   Keine Eigenimplementierung nötig — `scipy.stats.ks_2samp` (SciPy ist als
   scikit-learn-Abhängigkeit ohnehin installiert) erledigt das in einer Zeile:
   ```python
   from scipy.stats import ks_2samp
   ks = ks_2samp(y_pred_proba[y_test == 1], y_pred_proba[y_test == 0]).statistic
   ```
2. **Gini-Koeffizient** berechnen: `Gini = 2 * AUC - 1`. Kurz erklären, warum das in der
   Bankenpraxis (Scorecard-Validierung) eine gebräuchliche Umrechnung des AUC ist.
3. **Kalibrierungskurve** (Reliability Diagram) plotten — am einfachsten mit
   `sklearn.calibration.CalibrationDisplay.from_predictions(y_test, y_pred_proba, n_bins=10)`,
   das direkt den fertigen Plot erzeugt (`calibration_curve` liefert alternativ nur die
   Werte, falls ein eigener Plot gewünscht ist). Kurz erklären, warum Kalibrierung für PD-Modelle
   wichtig ist (vorhergesagte Wahrscheinlichkeiten sollen tatsächlichen Ausfallraten
   entsprechen, nicht nur die Rangfolge stimmen — relevant für IFRS9/Provisionierung).
4. Ergebnisse in einer kurzen Markdown-Zelle im Notebook zusammenfassen und einordnen
   (z. B. "KS von X deutet auf ... hin", "Modell ist in den unteren/oberen
   Wahrscheinlichkeitsbändern über-/unterkalibriert").
5. Falls Issue 03 (Modularisierung) bereits umgesetzt ist: KS-, Gini- und
   Kalibrierungs-Berechnung als wiederverwendbare Funktionen in `src/evaluate.py`
   ablegen (inkl. Tests, siehe Issue 05).

## Betroffene Dateien

- `01_notebooks/prediction.ipynb`
- `src/evaluate.py` (falls vorhanden)
- `tests/test_evaluate.py` (falls Issue 05 umgesetzt)

## Akzeptanzkriterien / Definition of Done

- [ ] KS-Statistik und Gini-Koeffizient werden berechnet und im Notebook ausgegeben.
- [ ] Kalibrierungskurve wird geplottet.
- [ ] Jede Metrik hat eine kurze, korrekte fachliche Einordnung im Notebook.
