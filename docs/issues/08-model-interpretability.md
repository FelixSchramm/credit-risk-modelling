# Issue 08: Modell-Interpretierbarkeit (SHAP / Feature Importance)

**Priorität:** P2 (Fachliche Tiefe — Differenzierung für Banking-Rollen)
**Status:** Open
**Betrifft:** `01_notebooks/prediction.ipynb`

## Kontext

Aktuell liefert das Notebook keine Erklärung dazu, *welche* Features den größten Einfluss
auf die Vorhersage haben. Im Bank-/Credit-Risk-Kontext ist Modell-Interpretierbarkeit
besonders wichtig: Kreditentscheidungen müssen oft begründbar sein (regulatorisch,
Kundenkommunikation), und "Black-Box"-Modelle ohne Erklärung werden kritisch gesehen.
Für ein Bewerbungs-Portfolio ist das ein naheliegender Punkt, um zu zeigen, dass man diese
Anforderung kennt.

## Ziel

Nachvollziehbare Erklärung, welche Features das Modell am stärksten treiben, inklusive
fachlicher Einordnung (ergibt das Muster ökonomisch/geschäftlich Sinn?).

## Umsetzungsschritte

1. `shap`-Paket zu `requirements.txt` hinzufügen (siehe Issue 06).
2. Feature Importances des `RandomForestClassifier` (`.feature_importances_`) als
   Balkendiagramm der Top-N (z. B. 15) wichtigsten Features darstellen.
3. Zusätzlich SHAP-Werte berechnen (z. B. `shap.TreeExplainer` für den Random Forest) und
   mindestens einen SHAP-Summary-Plot erzeugen, der Richtung und Stärke des Einflusses
   pro Feature zeigt (nicht nur absolute Wichtigkeit wie bei `feature_importances_`).
4. Für 2–3 der wichtigsten Features eine kurze fachliche Einordnung im Notebook ergänzen:
   Ergibt der beobachtete Zusammenhang (z. B. höheres `dti` (Debt-to-Income) → höhere
   Ausfallwahrscheinlichkeit) ökonomisch Sinn? Das zeigt Domänenverständnis, nicht nur
   technische Umsetzung.
5. Optional: ein Einzelfall-Beispiel mit einem SHAP-Force-/Waterfall-Plot erklären ("Warum
   hat das Modell für diesen einzelnen Kredit eine hohe Ausfallwahrscheinlichkeit
   vorhergesagt?") — sehr anschaulich für ein Portfolio.

## Betroffene Dateien

- `01_notebooks/prediction.ipynb`
- `requirements.txt`

## Akzeptanzkriterien / Definition of Done

- [ ] Feature-Importance-Plot vorhanden.
- [ ] SHAP-Summary-Plot vorhanden.
- [ ] Mindestens 2–3 Features sind fachlich (nicht nur technisch) eingeordnet.
