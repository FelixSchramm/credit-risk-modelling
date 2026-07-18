# Repo-Review: Credit_Risk_Modelling

**Ziel dieses Reviews:** Einschätzung, ob dieses Repository so, wie es aktuell ist, in
Bewerbungen (insbesondere bei Banken / für Data-Science-Rollen im Finanzsektor) gezeigt
werden kann, plus konkrete, priorisierte Verbesserungsvorschläge.

**Stand:** Review basiert auf dem Repo-Zustand vom 2026-07-18, Branch `main`
(Commit `411e226`). Aktuell besteht das Projekt im Kern aus einem einzelnen Notebook
(`01_notebooks/prediction.ipynb`) und einer README, die eine Projektstruktur beschreibt,
die im Repo so nicht existiert.

Die einzelnen Verbesserungspunkte sind als eigenständige Umsetzungs-Issues unter
[`docs/issues/`](./issues/) abgelegt — jede Datei ist so geschrieben, dass ein neuer Agent
(oder eine Person ohne Vorwissen zu dieser Diskussion) sie direkt umsetzen kann.

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
- [Data Leakage beheben](./issues/01-fix-data-leakage.md)
- [README an tatsächlichen Repo-Inhalt angleichen](./issues/02-align-readme-with-repo.md)

**P1 — Struktur/Professionalität:**
- [Code in Module unter `src/` auslagern (Umbenennung von `03_src/`)](./issues/03-modularize-src.md)
- [Notebook-Reproduzierbarkeit herstellen](./issues/04-notebook-reproducibility.md)
- [Unit-Tests ergänzen](./issues/05-add-unit-tests.md)
- [Dependencies pinnen, LICENSE ergänzen](./issues/06-pin-dependencies-and-license.md)

**P2 — Fachliche Tiefe (Differenzierung für Banking-Rollen):**
- [Credit-Risk-Standardmetriken ergänzen (KS, Gini, Kalibrierung)](./issues/07-credit-risk-metrics.md)
- [Modell-Interpretierbarkeit (SHAP/Feature Importance)](./issues/08-model-interpretability.md)
- [Scorecard-Vergleichsmodell (Logistic Regression + WOE/IV)](./issues/09-scorecard-comparison.md)
- [Basel/IFRS9-Einordnung ergänzen](./issues/10-basel-ifrs9-context.md)

**P3 — Politur:**
- [Repo-Hygiene (.DS_Store, warnings)](./issues/11-repo-hygiene.md)
- [CI-Setup (GitHub Actions)](./issues/12-ci-setup.md)
- [Git-Workflow-Empfehlungen](./issues/13-git-workflow.md)

## Wichtiger Hinweis zu diesem PR

Dieser Pull Request enthält **ausschließlich Dokumentation** (`docs/REPO_REVIEW.md`,
`docs/issues/*.md` sowie ein PR-Template unter `.github/pull_request_template.md`).
Es werden keine funktionalen Änderungen an Notebook, README, `requirements.txt` oder
Modellcode vorgenommen. Die Umsetzung der einzelnen Punkte ist als Folge-Arbeit über die
jeweiligen Issue-Dateien vorgesehen.

## Lebenszyklus dieser Dokumente

`docs/REPO_REVIEW.md` und `docs/issues/*` sind **internes Arbeitsmaterial** — in einem
öffentlichen Portfolio-Repo sind sie aber für genau die Zielgruppe sichtbar (Recruiter,
Interviewer), an die sich das Repo richtet. Deshalb:

- Nach dem Merge die Issue-Dateien idealerweise in echte GitHub-Issues überführen (dort
  gehören sie hin und sie lassen sich abhaken/schließen).
- Spätestens nach Abarbeitung der P0-/P1-Punkte das `docs/`-Verzeichnis wieder aus dem
  Repo entfernen. Die Git-Historie dokumentiert die Arbeitsweise weiterhin nachvollziehbar;
  als dauerhafter, prominenter Repo-Inhalt würde die Selbstkritik dem erklärten Ziel
  (überzeugender erster Eindruck) entgegenwirken.
