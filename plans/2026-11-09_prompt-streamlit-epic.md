# Prompt für die Planungs-KI: Epic „Recruiter-Dashboard (Streamlit, DE/EN)“

## Deine Rolle

Du bist eine Planungs-KI für das Repo `FelixSchramm/credit-risk-modelling`. Du
**planst zusammen mit Felix** ein Epic für ein Streamlit-Dashboard und legst danach
die zugehörigen GitHub-Issues an. Du schreibst **keinen Anwendungscode**.

Ergebnis am Ende:

1. eine Plandatei `plans/YYYY-MM-DD_streamlit-recruiter-dashboard.md`
   (Repo-Regel: Pläne liegen immer in `plans/` und werden committet),
2. ein Epic-Issue,
3. neue Issues für die Lücken, die unten beschrieben sind,
4. Ergänzungen an den bestehenden Issues #28–#38.

Arbeitsweise:

- Erst lesen, dann planen, dann Felix den Plan und die offenen Entscheidungen
  vorlegen. **Erst nach seiner Freigabe** Issues anlegen oder ändern, denn GitHub
  ist nach außen sichtbar.
- Mein Plan und meine Akzeptanzkriterien unten sind ein Vorschlag, kein Dogma. Wenn
  du eine bessere Idee hast, bring sie ein: als „Vorschlag“ markiert, mit Begründung
  und mit dem Preis, den sie kostet. Maßstab ist `CLAUDE_CODING_RULES.md`, vor allem
  „Simplicity First“: lieber ein Feature weniger als eines, das niemand braucht.

## Zuerst lesen

In diesem Repo:

- `CLAUDE.md`, `CLAUDE_CODING_RULES.md`, `HANDOVER.md`
- `README.md` (vor allem „Results“ und „Regulatory context“), `docs/REPO_REVIEW.md`
- `src/*.py`, `tests/`, `.github/workflows/ci.yml`, `requirements.txt`
- `01_notebooks/prediction.ipynb` (Abschnitte Evaluation, SHAP, Scorecard)
- **Die offenen Issues #28–#38 vollständig** (`gh issue view N`). Sie sind bereits
  ein ausgearbeiteter Plan für dieses Dashboard: Artefakt-Bundle mit Kalibrierung
  (#28), Build-Skript und Deployment-Forest (#29), lokaler Lauf (#30), App-Gerüst und
  Scoring-Layer (#31), fünf Seiten (#32–#37), Deployment (#38). **Dupliziere sie
  nicht.** Deine Aufgabe ist, sie zu einem Epic zusammenzufassen und die neuen
  Anforderungen unten einzuarbeiten.

Im öffentlichen Referenz-Repo `FelixSchramm/stock_treemap`. Dort ist Felix'
persönliche CI (Corporate Identity) bereits in einer Streamlit-App im Einsatz:

- `src/portfolio_dashboard/ci.json`: die Design-Tokens (Farben, Schrift,
  Diagrammregeln, für Farbfehlsichtigkeit geprüfte Paletten)
- `src/portfolio_dashboard/design.py`: Plotly-Styling und CSS auf Basis von `ci.json`
- `.streamlit/config.toml`, `static/Questrial-Regular.ttf`, `static/OFL-Questrial.txt`:
  Theme und Webschrift
- `src/portfolio_dashboard/exploration/glossary.md` und das Rendering in
  `src/portfolio_dashboard/exploration/view.py`: so sieht dort ein Glossar in
  Streamlit aus
- `docs/MOBILE_ACCESSIBILITY.md`
- `.github/workflows/ci.yml`: nur zum Vergleich, dieses Repo behält seine eigene CI

## Stand am 2026-11-09

- Der erste lokale Lauf auf dem echten Datensatz ist erfolgt. Ergebnis des Random
  Forest auf 125.381 Testkrediten: **ROC AUC 0,7168, Gini 0,4335, KS 0,3133**.
  - Die Ausfallrate im Testset liegt bei 21,6 % (27.090 „Charged Off“).
  - Bei der Schwelle 0,5 erkennt das Modell nur 29 % der Ausfälle (Recall).
  - Die Scorecard-Werte aus demselben Lauf stehen, falls vorhanden, in der
    Notebook-Ausgabe (Tabelle `comparison`).
- Der Forest ist unbegrenzt gewachsen: 100 Bäume, im Schnitt 84.911 Knoten und
  Tiefe 46, **682 MB** als Datei. TreeSHAP braucht damit **3,9 s pro Zeile**. Für
  das Dashboard folgt daraus: Der Deployment-Forest aus #29 muss begrenzt werden
  (`max_depth` / `min_samples_leaf`). Zwei Ziele:
  - Das Bundle bleibt deutlich unter 100 MB (GitHub-Limit, knapper RAM auf
    Streamlit Community Cloud).
  - SHAP für einen einzelnen Antrag dauert unter eine Sekunde.
- Beide Modelle sind mit `class_weight="balanced"` trainiert. Ihre Ausgaben sind
  also **keine** Ausfallwahrscheinlichkeiten. #28 löst das per Kalibrierung. Ohne
  Kalibrierung darf keine Zahl als PD angezeigt werden.
- Der Lauf hat eventuell Zwischen-Artefakte in `04_models/` abgelegt (`scaler`,
  `scorecard`, `shap_values`, `predictions`, `metrics.json`). Sie sind gitignored.
  Maßgeblich bleibt der Bundle-Vertrag aus #28. #30 ist weiterhin nötig, weil das
  Bundle den Code aus #28 und #29 braucht.
- Das Relay #2–#13 ist abgeschlossen. Kläre mit Felix, ob
  `claude/github-issues-review-3scsqi` schon nach `main` gemergt ist und von welchem
  Branch die Epic-Branches abzweigen.

## Neue Anforderungen von Felix

1. **Zielgruppe Recruiter** (Data-Science-Rollen im Schweizer Bankensektor). Wer die
   App öffnet, soll in 60 Sekunden verstehen, was gebaut wurde und warum es fachlich
   sauber ist.
2. **Zweisprachig Deutsch/Englisch**, mit einem Button zum Umschalten.
3. **Persönliche CI** aus `stock_treemap` verwenden.
4. **Glossar**, das alle Kennzahlen und Methoden einfach verständlich erklärt.
5. Die bestehende **GitHub-Actions-CI** dieses Repos (#13: ruff, black, pytest)
   nutzen und grün halten. Die CI bleibt datenlos.

## Mein Plan

### Neue Issues (Vorschläge für Titel und Priorität)

- **E: Epic: Recruiter-Dashboard (Streamlit, DE/EN)**
- **N1: Design-System: persönliche CI übernehmen** (P1)
- **N2: Zweisprachigkeit DE/EN mit Sprachumschalter** (P1)
- **N3: Glossar-Seite (DE/EN) und Kennzahlen-Tooltips** (P1)
- **N4: Startseite „Das Projekt in 60 Sekunden“** (P1). Darf in #31 aufgehen, wenn
  du das für schlanker hältst.

### Reihenfolge

```
#28 → #29 → #30 (lokal, Felix) → #31 → N1 → N2 → N3 → N4
    → #32 → #33 → #34 → #35 → #36 → #37 → #38
```

Begründung: CI, Zweisprachigkeit und Glossar müssen **vor** den Seiten #32–#37
fertig sein. Sonst wird jede Seite zweimal angefasst: einmal gebaut und einmal
nachträglich übersetzt und umgefärbt.

### Technische Punkte, die die bestehenden Issues verändern

- **Navigation:** #32–#37 planen Dateien wie `app/pages/1_Antrag_scoren.py`. Bei
  automatisch erkannten `pages/` stammen die Menünamen aus den Dateinamen und lassen
  sich nicht übersetzen. Für ein zweisprachiges Menü braucht es
  `st.navigation([...])` mit `st.Page(..., title=t("..."))`. Das gehört in #31 und
  muss in den Seiten-Issues nachgezogen werden.
- **Diagramm-Bibliothek:** #31 legt matplotlib und Streamlits eingebaute Charts fest
  („keine weiteren Abhängigkeiten“). Das CI-Styling in `stock_treemap` ist aber für
  Plotly geschrieben. Das entscheidet Felix (siehe unten).
- **Logik nach `src/`:** Sprach-Lookup, Glossar-Laden und Zahlenformatierung
  gehören wie die Scoring-Logik (#31) nach `src/`, damit sie getestet und gelintet
  werden.
- **API-Annahmen prüfen:** `st.navigation`, `st.segmented_control`, `st.query_params`
  und `AppTest` gegen die Streamlit-Version prüfen, die gepinnt werden soll, bevor du
  sie in Issues festschreibst.
- **Bestehende Issues nicht umschreiben:** An #28–#38 einen Abschnitt
  `## Ergänzung (Epic #E, YYYY-MM-DD)` mit den zusätzlichen Akzeptanzkriterien
  anhängen. So bleibt der ursprüngliche Text nachvollziehbar.
- **Zusatzkriterien für jede Seite #32–#37:**
  - Alle sichtbaren Texte laufen über `t()`.
  - Alle Charts nutzen das CI-Styling.
  - Jede angezeigte Kennzahl hat einen Tooltip aus dem Glossar.
  - Die Seite rendert im Smoke-Test in beiden Sprachen.

### Akzeptanzkriterien

**N1: Design-System**

- [ ] `ci.json` ist unverändert aus `stock_treemap` übernommen, die Quelle ist mit
      Commit-SHA vermerkt. Es gibt keine neu erfundenen Farben.
- [ ] `.streamlit/config.toml` folgt der CI: dark, `primaryColor #8EBC91`,
      `backgroundColor #0F120F`, `secondaryBackgroundColor #161A17`,
      `textColor #EDEFEA`, Questrial über Static Serving.
- [ ] Die Questrial-Schriftdatei und der OFL-Lizenztext liegen im Repo. Die Lizenz
      ist im README erwähnt.
- [ ] Genau ein Styling-Modul in `src/` liefert Chart-Styling und CSS. Im
      Seiten-Code stehen keine Hex-Codes.
- [ ] Die Farbzuordnung ist in allen Charts gleich: Random Forest = Slot 1 (forest),
      Scorecard = Slot 2 (blue).
- [ ] „Ausfall / kein Ausfall“ ist nie nur über Farbe kodiert, sondern immer auch
      über Beschriftung oder Symbol. Statusfarben kommen nur für Zustände zum Einsatz.
- [ ] Die Chart-Regeln der CI sind eingehalten: nur horizontale Gitterlinien, keine
      Doppelachsen, Titel linksbündig.
- [ ] Bei 390 px Breite ist jede Seite ohne horizontales Scrollen bedienbar.

**N2: Zweisprachigkeit**

- [ ] Der Sprachumschalter DE | EN sitzt oben in der Sidebar, auf jeder Seite an
      derselben Stelle (z. B. `st.segmented_control`).
- [ ] Ein Sprachwechsel löscht keine Eingaben im Rechner (`st.session_state`).
- [ ] Die Sprache steht in `st.query_params["lang"]`. Links wie `…?lang=de` lassen
      sich teilen und öffnen die App direkt auf Deutsch.
- [ ] Alle sichtbaren Texte laufen über `t(key)`: Titel, Labels, Hilfetexte, Achsen,
      Legenden, Fehlermeldungen, Menünamen.
- [ ] Die Übersetzungen liegen in je einer Datei pro Sprache mit gleicher Struktur
      (Vorschlag: TOML, gelesen mit `tomllib` aus der Standardbibliothek). Es wird
      keine i18n-Bibliothek eingesetzt.
- [ ] Ein pytest prüft, dass beide Sprachen dieselben Schlüssel haben und kein Wert
      leer ist.
- [ ] Zahlen folgen der Sprache: DE `0,717` / `21,6 %`, EN `0.717` / `21.6%`.

**N3: Glossar**

- [ ] Das Glossar ist eine eigene Seite „Glossar / Glossary“ im Menü, in beiden
      Sprachen.
- [ ] Jeder Eintrag hat vier Teile:
  1. **Was ist das?** In einfacher Sprache, höchstens drei Sätze, verständlich ohne
     Statistikstudium.
  2. **So liest du es:** Skala und Daumenregel, z. B. „AUC 0,5 = Münzwurf,
     1,0 = perfekt“.
  3. **In diesem Projekt:** der konkrete Wert, aus dem Bundle gelesen statt
     hartcodiert.
  4. **Grenze:** was die Kennzahl nicht aussagt.

  Formeln sind optional und stehen in einem aufklappbaren Bereich.
- [ ] Das Glossar ist gruppiert und durchsuchbar. Mindestumfang:
  - *Daten:* Zielvariable (Charged Off / Fully Paid), Data Leakage,
    Train/Test-Split, Out-of-Time-Validierung
  - *Modelle:* Random Forest, logistische Regression, Scorecard, Binning, WOE, IV,
    `class_weight="balanced"`
  - *Modellgüte:* ROC-Kurve, AUC, Gini, KS, Konfusionsmatrix, Precision, Recall, F1,
    Accuracy (und warum sie bei 22 % Ausfallrate täuscht)
  - *Kalibrierung:* PD, Basisrate, Kalibrierung, Reliability-Diagramm, isotonische
    Regression
  - *Erklärbarkeit:* Feature Importance, SHAP, SHAP-Basiswert, Beeswarm, Waterfall,
    Scorecard-Punkte
  - *Kreditrisiko-Ökonomie:* Score-Band/Dezil, Cut-off, Annahmequote, Expected Loss,
    LGD, EAD
  - *Regulatorik:* Basel IRB, IFRS 9 (Stages, 12-Monats- vs. Lifetime-ECL), FINMA,
    Model Card, Modellvalidierung
- [ ] Es gibt nur eine Quelle für Erklärtexte. Die Tooltips (`help=`) auf allen
      Seiten zeigen die Kurzfassung aus dem Glossar, einen zweiten Erklärtext gibt
      es nicht.
- [ ] Ein pytest prüft, dass jede Kennzahl, die die App anzeigt, einen
      Glossar-Eintrag in DE und EN hat.
- [ ] Die Einträge sind fachlich korrekt:
  - Gini = 2 · AUC − 1
  - KS = größter Abstand der kumulierten Score-Verteilungen von Ausfällen und
    Nicht-Ausfällen
  - EL = PD · LGD · EAD
  - IV-Daumenregeln: < 0,02 nutzlos, 0,02–0,1 schwach, 0,1–0,3 mittel,
    0,3–0,5 stark, > 0,5 Leakage-Verdacht
- [ ] Glossar und README-Abschnitt „Regulatory context“ widersprechen sich nicht.
      Verlinken statt duplizieren, wie in #36.

**N4: Startseite**

- [ ] Ohne Scrollen sind sichtbar: ein Satz zum Problem und Kacheln mit den
      Kennzahlen AUC, Gini, KS und Ausfallrate. Die Werte kommen aus dem Bundle,
      jede Kachel hat einen Tooltip.
- [ ] Ein Abschnitt „Was ich gemacht habe“ in drei bis fünf Punkten, darunter die
      Leakage-Geschichte: Spalten, die erst nach dem Kreditausgang bekannt sind,
      wurden entfernt, deshalb ist die AUC realistisch statt geschönt.
- [ ] Es gibt einen Wegweiser zu allen Seiten.
- [ ] Die Seite verlinkt GitHub-Repo, LinkedIn und Lebenslauf. Die URLs bei Felix
      erfragen, nicht erfinden.
- [ ] Ein Hinweis stellt klar: Demo auf historischen US-Daten (LendingClub), keine
      echte Kreditentscheidung.

**E: Definition of Done des Epics**

- [ ] Alle Unter-Issues sind geschlossen.
- [ ] Die App läuft öffentlich auf Streamlit Community Cloud. Die URL steht im
      README und im „About“ des Repos.
- [ ] Beide Sprachen sind vollständig. Im README liegen Screenshots oder ein GIF in
      DE und EN, als Ersatz, falls die App gerade schläft.
- [ ] Keine unkalibrierte Zahl wird als Ausfallwahrscheinlichkeit angezeigt.
- [ ] Die App braucht keine Rohdaten, nur das Bundle (deutlich unter 100 MB).
- [ ] Die CI ist grün: ruff, black, pytest. Dazu kommt ein Smoke-Test mit
      `streamlit.testing.v1.AppTest`, der jede Seite in beiden Sprachen ohne
      Exception rendert, gegen ein kleines synthetisches Test-Bundle.
- [ ] `CLAUDE_CODING_RULES.md` ist eingehalten (reST-Docstrings, Simplicity First,
      ein Issue = ein Feature-Branch).

### Offene Entscheidungen für Felix (vor dem Anlegen der Issues fragen)

1. **Diagramme.** Zwei Optionen:
   - (a) Plotly und `design.py` aus `stock_treemap` fast 1:1 übernehmen.
     Interaktive Tooltips und derselbe Look wie seine anderen Apps, dafür eine
     zusätzliche Abhängigkeit.
   - (b) matplotlib mit CI-Stil (`stack_matplotlib` steht in `ci.json`). Keine neue
     Abhängigkeit, so wie in #31 geplant.

   *Meine Empfehlung: (a).* Übernehmen ist besser als neu schreiben, und Recruiter
   fahren gern mit der Maus über Charts.
2. **Startsprache.** *Empfehlung: Englisch.* Code und README sind englisch, und
   Data-Rollen in Schweizer Banken arbeiten oft auf Englisch. Deutsch gibt es über
   den Button oder `?lang=de`.
3. **Hell/Dunkel.** *Empfehlung: nur dark*, wie die CI es vorgibt, ohne
   Theme-Umschalter.
4. **Links für die Startseite:** LinkedIn, Lebenslauf, ggf. persönliche Website.
5. **Abarbeitung.** Soll das autonome Relay die Epic-Issues wieder abarbeiten? Dann
   müssen die Reihenfolge des Arbeitsplans in `CLAUDE.md` und der Stand in
   `HANDOVER.md` angepasst werden. Diese Änderung nur vorschlagen, nicht selbst
   durchführen.

## Format der Issues

- Exakt wie #28–#38: auf Deutsch, mit den Kopfzeilen `**Priorität:**`,
  `**Betrifft:**` und `**Voraussetzung:**`. Danach folgen `## Kontext`, `## Ziel`,
  `## Umsetzungsschritte`, ggf. `## Tests`, `## Betroffene Dateien` und
  `## Akzeptanzkriterien / Definition of Done` mit Checkboxen.
- Die Labels P0–P3 wie bisher verwenden, dazu ein Label `epic` für das Epic.
- Jedes Issue muss für sich allein umsetzbar sein, denn eine Worker-Session liest
  nur dieses eine Issue.
- Das Epic verlinkt alle Unter-Issues als Checkliste (oder als GitHub-Sub-Issues,
  falls verfügbar) und enthält den Abhängigkeitsgraphen.
- Gib Felix am Ende eine kurze Liste: angelegte Issues, ergänzte Issues, getroffene
  Annahmen.
