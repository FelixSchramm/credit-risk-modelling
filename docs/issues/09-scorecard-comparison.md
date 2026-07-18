# Issue 09: Scorecard-Vergleichsmodell (Logistic Regression + WOE/IV)

**Priorität:** P2 (Fachliche Tiefe — Differenzierung für Banking-Rollen, optional)
**Status:** Open
**Betrifft:** `01_notebooks/prediction.ipynb`, ggf. `src/train.py` (siehe Issue 03)

## Kontext

Aktuell wird ausschließlich ein `RandomForestClassifier` verwendet. In der klassischen
Bankenpraxis (Credit Scoring, insbesondere für regulatorisch geprüfte PD-Modelle) ist der
Industriestandard nach wie vor häufig eine **Scorecard** auf Basis von **Logistic
Regression** mit **Weight-of-Evidence (WOE)**-transformierten Features und **Information
Value (IV)** zur Feature-Selektion — vor allem wegen der geforderten Nachvollziehbarkeit/
Interpretierbarkeit gegenüber Aufsichtsbehörden. Ein Vergleich zwischen diesem klassischen
Ansatz und dem "moderneren" Random-Forest-Modell zeigt gezieltes Branchenwissen und ist ein
starkes Differenzierungsmerkmal in Bewerbungen bei Banken.

Dies ist als **optionaler, aber empfohlener** Ausbau markiert (P2) — sinnvoll, sobald die
P0/P1-Punkte umgesetzt sind.

## Ziel

Ein zweites, klassisches Modell (Logistic Regression auf WOE-transformierten Features) als
Vergleich zum Random Forest, inklusive kurzer Diskussion der Trade-offs
(Interpretierbarkeit vs. Vorhersagekraft, regulatorische Akzeptanz).

## Umsetzungsschritte

1. Für die wichtigsten kategorialen und numerischen Features WOE-Bins berechnen (z. B.
   mit einem etablierten Paket wie `optbinning` oder einer eigenen, einfachen
   Implementierung — je nach Aufwand).
2. Information Value (IV) je Feature berechnen und zur Feature-Selektion nutzen (übliche
   Daumenregel: IV < 0.02 = kaum prädiktiv, IV > 0.5 = verdächtig stark → möglicher
   Leakage-Kandidat, siehe Issue 01).
3. Logistic-Regression-Modell auf den WOE-transformierten Features trainieren.
4. Metriken (AUC, KS, Gini — siehe Issue 07) für beide Modelle (Random Forest vs.
   Logistic-Regression-Scorecard) nebeneinander vergleichen.
5. Kurze Diskussion im Notebook ergänzen: Wann würde man in der Praxis welches Modell
   wählen (Interpretierbarkeit/regulatorische Anforderungen vs. reine Modellgüte)?

## Betroffene Dateien

- `01_notebooks/prediction.ipynb`
- `src/train.py` (falls Issue 03 bereits umgesetzt)
- `requirements.txt` (ggf. `optbinning` oder vergleichbares Paket)

## Akzeptanzkriterien / Definition of Done

- [ ] WOE/IV-basierte Feature-Transformation und -Selektion ist nachvollziehbar umgesetzt.
- [ ] Logistic-Regression-Scorecard-Modell ist trainiert und mit denselben Metriken wie
      das Random-Forest-Modell evaluiert.
- [ ] Notebook enthält eine kurze, fachlich fundierte Gegenüberstellung beider Ansätze.
