# Repo-Review: Credit_Risk_Modelling

**Ziel dieses Reviews:** Einschätzung, ob dieses Repository so, wie es aktuell ist, in
Bewerbungen (insbesondere bei Banken / für Data-Science-Rollen im Finanzsektor) gezeigt
werden kann, plus konkrete, priorisierte Verbesserungsvorschläge.

**Stand:** Review basiert auf dem Repo-Zustand vom 2026-07-18, Branch `main`
(Commit `411e226`). Aktuell besteht das Projekt im Kern aus einem einzelnen Notebook
(`01_notebooks/prediction.ipynb`) und einer README, die eine Projektstruktur beschreibt,
die im Repo so nicht existiert.

Die einzelnen Verbesserungspunkte sind als eigenständige GitHub-Issues (#2–#14) angelegt —
jedes Issue ist so geschrieben, dass ein neuer Agent (oder eine Person ohne Vorwissen zu
dieser Diskussion) es direkt umsetzen kann.

## Stärken

- README beschreibt Business-Ziel, Datenquelle und Methodik in verständlicher Prosa.
- Öffentlicher, bekannter Datensatz (LendingClub 2007–2018Q4) korrekt referenziert statt
  Rohdaten ins Repo zu committen — `.gitignore` schließt `02_data/raw/` und `04_models/`
  sauber aus.
- Stratifizierter Train/Test-Split, `class_weight="balanced"` für Klassenungleichgewicht
  berücksichtigt.
- Keine Secrets, keine Zugangsdaten, keine hartcodierten `C:\Users\...`-Pfade.
- Kein PII/sensible Echtdaten im Repo.

## Schwächen (nach Schweregrad)

1. **Vermutlicher Data Leakage → ROC AUC 0.9999.** Der Leakage-Spalten-Drop entfernt zwar
   `grade`, `sub_grade`, Datumsspalten etc., aber **nicht** Post-Outcome-Felder wie
   `total_pymnt`, `out_prncp`, `recoveries`, `last_pymnt_amnt`, `last_fico_range_high/low`,
   `hardship_*`. Diese sind erst
   nach Kreditausfall/-tilgung bekannt. Ein AUC von 0.9999 ist im Credit-Risk-Kontext ein
   Warnsignal, kein Erfolg — genau das würde ein Bank-Interviewer sofort erkennen.
2. **README ist inkonsistent mit dem tatsächlichen Repo-Inhalt.** Sie listet
   `01_notebooks/1.0-eda-and-prototyping.ipynb`, `03_src/01_process_data.py`,
   `03_src/02_train_model.py`, `04_models/random_forest_v1.joblib` — keine dieser Dateien
   existiert. `03_src/` und `04_models/` enthalten nur `.gitkeep`. Wirkt unfertig/unehrlich.
3. **Kein modularer Code.** Alles steckt in einem Notebook; keine wiederverwendbaren
   Funktionen/Module, keine Pipeline. Für Banking-DS-Rollen wird produktionsnaher,
   modularer Code erwartet.
4. **Keine Tests.** Kein `tests/`-Verzeichnis, kein pytest.
5. **Fehlende Credit-Risk-Standardmetriken/Interpretierbarkeit.** Nur ROC AUC +
   Classification Report. Keine KS-Statistik, kein Gini, keine Kalibrierungskurve, kein
   SHAP/Feature-Importance mit Business-Interpretation — im Bank-Kontext (Basel/IFRS9)
   Standard.
6. **Notebook nicht sauber reproduzierbar.** Execution-Counts sind nicht-monoton/doppelt →
   Notebook wurde nie "Restart & Run All" durchlaufen, bevor es committet wurde.
7. **Reste von Kurs-/Rubrik-Artefakten.** Kryptische Kommentare wie `# (g, h, i)`, `# (b)`,
   `# (q)` wirken wie Checklisten-Reste einer Kursaufgabe, nicht wie polierte Eigenarbeit.
   Zudem `df.info` ohne Klammern (Debug-Rest).
8. **Fehlende Projekt-Hygiene.** Kein Pinning in `requirements.txt`, keine
   `pyproject.toml`/`environment.yml`, keine CI (GitHub Actions), keine LICENSE, keine
   "How to run"-Anleitung in der README.
9. **Git-Historie wenig aussagekräftig.** 9 Commits an zwei aufeinanderfolgenden Tagen,
   ein Autor, Messages wie
   "Update README.md" (×4), Tippfehler in Merge-Message. Wirkt wie schnell hochgeladen statt
   gepflegt.
10. **Kleinkram:** `.DS_Store`-Dateien versehentlich eingecheckt; globales
    `warnings.filterwarnings('ignore')` kann echte Warnungen verstecken.

## Priorisierte Verbesserungsvorschläge

**P0 — Glaubwürdigkeit (vor jeder Bewerbung zwingend):**
- [#2 — Data Leakage beheben](https://github.com/FelixSchramm/Credit_Risk_Modelling/issues/2)
- [#3 — README an tatsächlichen Repo-Inhalt angleichen](https://github.com/FelixSchramm/Credit_Risk_Modelling/issues/3)

**P1 — Struktur/Professionalität:**
- [#4 — Code in Module unter `src/` auslagern (Umbenennung von `03_src/`)](https://github.com/FelixSchramm/Credit_Risk_Modelling/issues/4)
- [#5 — Notebook-Reproduzierbarkeit herstellen](https://github.com/FelixSchramm/Credit_Risk_Modelling/issues/5)
- [#6 — Unit-Tests ergänzen](https://github.com/FelixSchramm/Credit_Risk_Modelling/issues/6)
- [#7 — Dependencies pinnen, LICENSE ergänzen](https://github.com/FelixSchramm/Credit_Risk_Modelling/issues/7)

**P2 — Fachliche Tiefe (Differenzierung für Banking-Rollen):**
- [#8 — Credit-Risk-Standardmetriken ergänzen (KS, Gini, Kalibrierung)](https://github.com/FelixSchramm/Credit_Risk_Modelling/issues/8)
- [#9 — Modell-Interpretierbarkeit (SHAP/Feature Importance)](https://github.com/FelixSchramm/Credit_Risk_Modelling/issues/9)
- [#10 — Scorecard-Vergleichsmodell (Logistic Regression + WOE/IV)](https://github.com/FelixSchramm/Credit_Risk_Modelling/issues/10)
- [#11 — Basel/IFRS9-Einordnung ergänzen](https://github.com/FelixSchramm/Credit_Risk_Modelling/issues/11)

**P3 — Politur:**
- [#12 — Repo-Hygiene (.DS_Store, warnings)](https://github.com/FelixSchramm/Credit_Risk_Modelling/issues/12)
- [#13 — CI-Setup (GitHub Actions)](https://github.com/FelixSchramm/Credit_Risk_Modelling/issues/13)
- [#14 — Git-Workflow-Empfehlungen](https://github.com/FelixSchramm/Credit_Risk_Modelling/issues/14)

## Wichtiger Hinweis zu diesem PR

Dieser Pull Request enthält **ausschließlich Dokumentation** (`docs/REPO_REVIEW.md`
sowie ein PR-Template unter `.github/pull_request_template.md`). Es werden keine
funktionalen Änderungen an Notebook, README, `requirements.txt` oder Modellcode
vorgenommen. Die Umsetzung der einzelnen Punkte ist als Folge-Arbeit über die
GitHub-Issues #2–#14 vorgesehen.

## Lebenszyklus dieses Dokuments

Die ursprünglich unter `docs/issues/` geführten Umsetzungs-Briefings wurden in echte
GitHub-Issues (#2–#14) überführt und aus diesem PR entfernt — im Issue-Tracker gehören
sie hin und lassen sich pro Punkt abhaken und schließen.

Dieses Review-Dokument selbst ist **internes Arbeitsmaterial**: Es dient als Übersicht
und Priorisierung während der Umsetzung und sollte nach Abarbeitung der P0-/P1-Punkte
ebenfalls aus dem Repo entfernt werden — in einem öffentlichen Portfolio-Repo ist die
Selbstkritik sonst für genau die Zielgruppe sichtbar (Recruiter, Interviewer), an die
sich das Repo richtet. Die Git-Historie dokumentiert die Arbeitsweise weiterhin
nachvollziehbar.
