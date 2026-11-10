# Plan: Epic „Recruiter-Dashboard (Streamlit, DE/EN)“

**Status:** Entwurf, wartet auf Freigabe durch Felix. Vor der Freigabe wird auf
GitHub nichts angelegt oder geändert.
**Auftrag:** `plans/2026-11-09_prompt-streamlit-epic.md` (Anforderungen und
Akzeptanzkriterien für N1–N4 und das Epic stehen dort und werden hier nicht
wiederholt; dieser Plan nennt nur Befunde, Abweichungen und die Ergänzungen an
#28–#38).

## 1. Ziel

Ein öffentliches Streamlit-Dashboard, das einem Recruiter für Data-Science-Rollen
im Schweizer Bankensektor in 60 Sekunden zeigt, was gebaut wurde und warum es
fachlich sauber ist: zweisprachig (DE/EN), in Felix' persönlicher CI, mit Glossar,
datenlos (nur Bundle), CI grün.

## 2. Befunde aus dem Lesen (Stand 2026-11-09)

### Repo

- `main` steht auf `693c9ef` und liegt **59 Commits hinter**
  `claude/github-issues-review-3scsqi`. Der Integrations-Branch ist also noch
  nicht nach `main` gemergt. Die CI (`ci.yml`) existiert nur auf dem
  Integrations-Branch.
- `ci.yml` prüft `black --check src tests`. `app/` und `scripts/` wären damit
  nicht formatgeprüft (`ruff check .` erfasst sie).
- `requirements.txt` ist auf Python 3.11 gepinnt (`scikit-learn==1.9.0`,
  `shap==0.51.0`, `optbinning==0.21.0`, `matplotlib==3.11.1`). `tomllib` ist ab
  3.11 in der Standardbibliothek, passt also.
- Die Notebook-Ausgabe enthält die Random-Forest-Werte (AUC 0,7168, Gini 0,4335,
  KS 0,3133, Recall „Charged Off“ 0,29, n = 125.381). **Scorecard-Werte stehen
  nicht in der Ausgabe**, eine Tabelle `comparison` wurde nicht ausgegeben.
- `04_models/` enthält nur `random_forest.joblib` (682 MB). `scaler`,
  `scorecard`, `metrics.json` usw. liegen dort nicht.
- README „Results“ nennt weiterhin keine Messwerte (Aufgabe von #30).

### Referenz-Repo `stock_treemap` (HEAD `2a8d2d3`)

- `ci.json` ist Version 1.3.0, `default_mode: dark`. Die Hex-Werte aus N1
  stimmen mit `.streamlit/config.toml` dort überein.
- `design.py` ist klein (ca. 45 Zeilen): `style_figure(fig)` für Plotly und
  `dashboard_css()`. Zwei Stellen passen nicht 1:1:
  - `separators=",."` ist fest deutsch. Für EN muss das von der Sprache abhängen.
  - `UP`/`DOWN`/`VALUE_COLORS` sind Börsenfarben und werden hier nicht gebraucht.
- Die Schrift wird über `enableStaticServing` mit der URL
  `app/static/Questrial-Regular.ttf` geladen. Streamlit liefert den Ordner
  `static/` **neben dem Einstiegsskript** aus. Hier ist das `app/app.py`, die
  Datei muss also nach `app/static/` (die URL bleibt `app/static/...`).
- Das Glossar dort ist eine Markdown-Datei mit Tabellen, je Abschnitt ein
  `st.expander`. Einsprachig, ohne Tooltips, ohne Suche. Als Vorlage für das
  Aussehen brauchbar, nicht für die Datenhaltung (N3 braucht Schlüssel).
- Versionen dort im Lockfile: `streamlit 1.66.1`, `plotly 7.1.0`.

### API-Prüfung gegen `streamlit==1.66.1` (in einer Wegwerf-Umgebung ausgeführt)

| Annahme | Ergebnis |
|---|---|
| `st.navigation` + `st.Page(..., title=...)` mit Titel je Sprache | funktioniert |
| `st.segmented_control` in der Sidebar | funktioniert |
| `st.query_params["lang"]` beim Start lesen | funktioniert, `?lang=de` rendert deutsch |
| `AppTest`: erste Ausführung je Sprache, `switch_page` auf eine zweite Seite | funktioniert, keine Exception |
| `AppTest`: Seiten-Datei direkt ausführen | funktioniert |
| `AppTest`: Widget-Interaktion **nach** der ersten Ausführung | **eingeschränkt**: nach dem Rerun war die Sidebar im Testbaum leer und der Sprachwechsel kam nicht an |

Folgen für die Issues:

- Der Smoke-Test „jede Seite in beiden Sprachen ohne Exception“ ist machbar
  (Sprache über `at.query_params` setzen, Seite über `switch_page`).
- „Sprachwechsel löscht keine Eingaben“ lässt sich mit `AppTest` in dieser
  Version nicht zuverlässig automatisch prüfen. Das Kriterium bleibt, wird aber
  als manuelle Prüfung formuliert.
- `t()` muss die Sprache selbst aus `st.session_state` / `st.query_params` lesen
  und darf sich nicht darauf verlassen, dass das Einstiegsskript vorher lief.
- Noch zu verifizieren im Issue N2 (nicht getestet, laut Streamlit-Doku): Beim
  Seitenwechsel werden Query-Parameter gelöscht. Dann muss `st.session_state`
  die Quelle der Wahrheit sein und `app.py` schreibt `lang` bei jedem Lauf
  zurück in die URL.

## 3. Issue-Struktur und Reihenfolge

Neue Issues wie im Auftrag: **E** (Epic), **N1** Design-System, **N2**
Zweisprachigkeit, **N3** Glossar, **N4** Startseite. N4 bleibt ein eigenes Issue
und geht nicht in #31 auf: Die Startseite braucht `t()`, Tooltips und CI-Styling,
die erst nach #31 entstehen.

```
#28 → #29 → #31 → N1 → N2 → N3 → N4 → #32 → #33 → #34 → #35 → #36 → #37 → #38
        \                                                                  /
         → #30 (lokal, Felix) ────────────────────────────────────────────
```

**Vorschlag V1 (Abweichung vom Auftrag): #30 blockiert nur noch #38, nicht #31.**
Begründung: #30 braucht Felix und den Rohdatensatz. Hängt #31 daran, steht das
ganze Epic, bis der lokale Lauf erfolgt ist. Der Smoke-Test braucht ohnehin ein
kleines synthetisches Bundle; baut man es mit `build_bundle()` aus #28 auf
synthetischen Daten, läuft es durch denselben Code wie das echte. Damit können
#31 bis #37 dagegen entwickelt werden. Preis: Die Seiten entstehen, ohne dass
jemand die echten Zahlen darin gesehen hat. Die Sichtprüfung mit dem echten
Bundle wandert nach #38.

## 4. Neue Issues: Abweichungen von den Kriterien im Auftrag

Alle nicht genannten Kriterien übernehme ich unverändert.

### N1 Design-System

- Styling-Modul `src/design.py`, übernommen aus `stock_treemap` ohne die
  Börsenfarben; `separators` kommt als Parameter von der Sprache (Standard EN,
  bis N2 da ist).
- Schrift und Lizenztext nach `app/static/` (siehe Befund oben).
  `.streamlit/config.toml` liegt im Repo-Root.
- Ein pytest prüft: `ci.json` lädt, `style_figure` setzt Slot 1 und 2 der
  dunklen Palette, in `app/` steht kein Hex-Code (einfache Regex über die
  Dateien).
- **Vorschlag V2:** Das Kriterium „390 px ohne horizontales Scrollen“ aus N1
  herausnehmen und als manuelle Prüfung nach #38 legen. Bei N1 gibt es noch
  keine Seiten, an denen man es prüfen könnte. Preis: keiner.

### N2 Zweisprachigkeit

- `src/i18n.py` mit `t(key, lang)`, `fmt_number`, `fmt_percent`; Texte in
  `src/locales/de.toml` und `en.toml`. `src/i18n.py` importiert kein Streamlit,
  die Sprache ermittelt eine kleine Funktion in `app/`.
- Fehlender Schlüssel führt zu einem `KeyError`, nicht zu einem stillen
  Platzhalter. So findet der Smoke-Test jeden vergessenen Text.
- Kriterium „Sprachwechsel löscht keine Eingaben“: manuelle Prüfung (siehe
  API-Prüfung).
- Der Smoke-Test aus #31 wird auf beide Sprachen erweitert.

### N3 Glossar

- **Vorschlag V3: Glossartexte liegen in denselben TOML-Dateien** unter
  `[glossary.<key>]` mit `term`, `group`, `what`, `how_to_read`, `limit`,
  optional `formula`. Dann deckt der Schlüssel-Paritätstest aus N2 das Glossar
  mit ab, und es gibt keinen zweiten Lademechanismus. Preis: Die TOML-Dateien
  werden lang (ca. 45 Einträge je Sprache).
- **Vorschlag V4: `how_to_read` und „In diesem Projekt“ sind nur dort Pflicht,
  wo es eine Skala bzw. einen Wert gibt.** Für AUC, Gini, KS, Basisrate, IV usw.
  ja. Für „FINMA“, „Model Card“ oder „Data Leakage“ gibt es keine Skala und
  keinen Bundle-Wert; ein erzwungener vierter Teil wäre Fülltext. „Was ist das?“
  und „Grenze“ bleiben für jeden Eintrag Pflicht. Preis: Die Einträge sehen
  nicht alle gleich aus.
- „In diesem Projekt“: Der Eintrag nennt einen Bundle-Pfad (z. B.
  `metrics.rf.roc_auc`), die Seite setzt den Wert formatiert ein.
- Tooltips: eine Funktion `glossary_help(key, lang)` liefert `what` (die
  Kurzfassung). Der Test „jede angezeigte Kennzahl hat einen Eintrag“ folgt
  daraus ohne eigene Liste: Ein fehlender Schlüssel wirft im Smoke-Test.
- Suche: ein `st.text_input`, das Einträge nach Begriff und Text filtert;
  Gruppen als Überschriften, Einträge als `st.expander`.

### N4 Startseite

- Unverändert. Die URLs (LinkedIn, Lebenslauf, ggf. Website) kommen von Felix
  und stehen als Konstanten an einer Stelle.

### Epic

- Label `epic` wird neu angelegt. Unter-Issues als Checkliste im Epic-Text und
  zusätzlich als GitHub-Sub-Issues, falls die API das im Repo erlaubt.
- DoD wie im Auftrag. Das Größenziel konkretisiert: **Bundle höchstens 50 MB**
  (Vorschlag, „deutlich unter 100 MB“ ist nicht prüfbar).

## 5. Ergänzungen an bestehenden Issues

Jeweils als angehängter Abschnitt `## Ergänzung (Epic #E, 2026-11-09)`. Der
ursprüngliche Text bleibt stehen.

| Issue | Ergänzung |
|---|---|
| #28 | **Vorschlag V5:** Bundle-Vertrag um `proba_rf_raw` und `proba_scorecard_raw` (unkalibrierte Test-Scores, float32) erweitern. #34 Schritt 3 will den Vorher-Nachher-Vergleich zeigen, „falls im Bundle“; jetzt ist der Moment, das festzulegen, weil der Vertrag sich danach nicht mehr ändern soll. Preis: ca. 1 MB. Außerdem festhalten: `rf` ist der kalibrierte Wrapper; für TreeSHAP braucht #33 den inneren Forest. |
| #29 | Messwerte vom 2026-11-09 eintragen (682 MB, Tiefe 46, 3,9 s SHAP je Zeile). Ziele für den Deployment-Forest: Bundle ≤ 50 MB, TreeSHAP für eine Zeile < 1 s. Das Skript gibt beides aus, dazu den AUC-Verlust gegenüber dem unbegrenzten Forest. `black --check` um `scripts` erweitern (steht dort schon als Kriterium). |
| #30 | Voraussetzung für #38 statt für #31 (V1). Hinweis: RF-Werte liegen aus dem Notebook-Lauf vor, Scorecard-Werte nicht. Der Bundle-Lauf bleibt nötig. |
| #31 | Voraussetzung #29 statt #30 (V1). `streamlit==1.66.1` pinnen. Navigation über `st.navigation` / `st.Page` statt automatischer `pages/`; `app/app.py` ist nur Router plus Sidebar. Synthetisches Test-Bundle als Fixture in `tests/conftest.py`, gebaut mit `build_bundle()`. Neuer `tests/test_app_smoke.py`: jede registrierte Seite rendert ohne Exception. `black --check` um `app` erweitern. Der Satz „keine weiteren Abhängigkeiten“ entfällt, falls Felix Plotly wählt. |
| #32–#37 | Vier Zusatzkriterien aus dem Auftrag (Texte über `t()`, CI-Styling, Tooltips aus dem Glossar, Smoke-Test in beiden Sprachen). Voraussetzung zusätzlich N4. Dateinamen englisch ohne Nummer (`app/pages/calculator.py`, `performance.py`, `cutoff.py`, `limits.py`, `comparison.py`), weil Menüname und Reihenfolge jetzt aus `st.navigation` kommen. |
| #33 | Zusätzlich, falls Plotly: Der Waterfall wird aus den SHAP-Werten als `go.Waterfall` gebaut, weil `shap.plots.waterfall` matplotlib mit festen Farben zeichnet und sich nicht an die CI anpassen lässt. Datei ist `app/pages/calculator.py`. |
| #34 | Nutzt `proba_*_raw` aus V5. Falls Plotly: ROC und Kalibrierung über `sklearn.metrics.roc_curve` und `sklearn.calibration.calibration_curve`, nicht über die `Display`-Klassen. |
| #36 | Glossar und Seite verweisen beide auf README „Regulatory context“; keine dritte Fassung der Texte. |
| #38 | Voraussetzung zusätzlich #30. Sichtprüfung mit dem echten Bundle, 390-px-Prüfung (V2), Screenshots oder GIF in DE und EN, URL ins „About“ des Repos. Schritt 5 (Import-Smoke-Test) entfällt, der `AppTest`-Smoke-Test aus #31 deckt ihn ab. „Alle fünf Seiten“ wird zu „alle Seiten“ (mit Start und Glossar sind es sieben). |

## 6. Offene Entscheidungen für Felix

1. **Diagramme:** (a) Plotly oder (b) matplotlib. Empfehlung (a). Zusätzlicher
   Grund aus der Prüfung: `shap`-Plots lassen sich in matplotlib nicht sauber
   auf die CI-Farben bringen, in Plotly baut man den Waterfall in wenigen
   Zeilen selbst. Preis von (a): `plotly==7.1.0` als neue Abhängigkeit, ROC,
   Kalibrierung und Waterfall werden von Hand aus Arrays gezeichnet.
2. **Startsprache:** Empfehlung Englisch.
3. **Hell/Dunkel:** Empfehlung nur dark.
4. **Links für die Startseite:** LinkedIn, Lebenslauf, ggf. Website.
5. **Abarbeitung durch das Relay?** Falls ja, schlage ich die Änderungen an
   `CLAUDE.md` (Arbeitsplan) und `HANDOVER.md` als Diff vor und führe sie erst
   nach Freigabe aus.
6. **Branch-Basis:** `claude/github-issues-review-3scsqi` ist nicht nach `main`
   gemergt. Empfehlung: zuerst den PR nach `main` mergen und die Epic-Branches
   von `main` abzweigen. Dann läuft die CI auch auf `main`, und Streamlit
   Community Cloud kann später direkt von `main` deployen.
7. **Vorschläge V1–V5** annehmen oder ablehnen (V1 #30 entkoppeln, V2 390 px
   nach #38, V3 Glossar in den Sprachdateien, V4 Pflichtteile je Eintrag,
   V5 unkalibrierte Scores im Bundle).

## 7. Vorgehen nach der Freigabe

1. Label `epic` anlegen, Epic-Issue anlegen → Nummer E steht fest.
2. N1–N4 anlegen (Format wie #28–#38, deutsch, je für sich allein umsetzbar),
   mit Verweis auf E.
3. Ergänzungen an #28–#38 anhängen.
4. Epic-Checkliste und Abhängigkeitsgraph mit den echten Nummern füllen.
5. Diesen Plan auf den Stand der Entscheidungen bringen und committen.
6. Felix die Liste geben: angelegte Issues, ergänzte Issues, getroffene Annahmen.
