# Plan: Epic „Recruiter-Dashboard (Streamlit, DE/EN)“

**Status:** von Felix am 2026-11-09 freigegeben. Die Issues sind am 2026-11-10
angelegt: Epic #39, neue Issues #40–#43, Ergänzungen an #28–#38.
**Auftrag:** `plans/2026-11-09_prompt-streamlit-epic.md`.
Die Akzeptanzkriterien stehen in den Issues und werden hier nicht wiederholt.
Dieser Plan hält fest, was entschieden und geprüft wurde und wo die Issues vom
Auftrag abweichen.

## 1. Ziel

Ein öffentliches Streamlit-Dashboard, das einem Recruiter für Data-Science-Rollen
im Schweizer Bankensektor in 60 Sekunden zeigt, was gebaut wurde und warum es
fachlich sauber ist: zweisprachig (DE/EN), in Felix' persönlichem Design (hell
und dunkel), mit Glossar, datenlos (nur Bundle), CI-Pipeline grün.

## 2. Entscheidungen von Felix

| Thema | Entscheidung |
|---|---|
| Diagramme | Plotly (`plotly==7.1.0`) |
| Startsprache | Englisch, Deutsch über Umschalter oder `?lang=de` |
| Hell/Dunkel | beide Modi, mit Umschalter |
| Links auf der Startseite | GitHub, LinkedIn, Website |
| Abarbeitung | Relay aus Worker und Reviewer je Issue |
| Branch-Basis | `main` (PR #44 hat den Integrations-Branch am 2026-11-10 gemergt) |
| Vorschläge V1–V5 | angenommen (siehe Abschnitt 6) |
| Bundle-Größe | höchstens 50 MB |

## 3. Issues und Reihenfolge

| Nr. | Titel | Art |
|---|---|---|
| #39 | Epic: Recruiter-Dashboard (Streamlit, DE/EN) | neu |
| #40 | Design-System: persönliche CI übernehmen | neu |
| #41 | Zweisprachigkeit DE/EN mit Sprachumschalter | neu |
| #42 | Glossar-Seite (DE/EN) und Kennzahlen-Tooltips | neu |
| #43 | Startseite „Das Projekt in 60 Sekunden“ | neu |
| #28–#38 | bestehender Dashboard-Plan | je ein Abschnitt „Ergänzung (Epic #39, 2026-11-10)“ |

```
#28 → #29 → #31 → #40 → #41 → #42 → #43 → #32 → #33 → #34 → #35 → #36 → #37 → #38
        \                                                                  /
         └───────────── #30 (lokal, braucht den Rohdatensatz) ────────────┘
```

Alle fünfzehn Issues sind als Sub-Issues am Epic verknüpft.

## 4. Aufbau der App

```
streamlit_app.py            Einstieg: Sprache, Sidebar, Navigation
app/ui.py                   Streamlit-nahe Helfer: Bundle laden, Seitenliste, t(), Zahlen, Charts, Tooltips
app/views/<seite>.py        je Seite eine Datei, nur Darstellung
src/scoring.py              Scoring-Logik (#31)
src/design.py, src/ci.json  Design (#40)
src/i18n.py, src/locales/   Übersetzungen und Zahlenformate (#41)
src/glossary.py             Glossar (#42)
static/                     Webschrift
.streamlit/config.toml      Theme hell und dunkel
```

Logik liegt in `src/` (getestet, ohne Streamlit-Import), Darstellung in `app/`.

## 5. Geprüfte Rahmenbedingungen

Mit einer Wegwerf-App gegen `streamlit==1.66.1` und `plotly==7.1.0` geprüft, im
Browser (Chrome über Playwright) und mit `streamlit.testing.v1.AppTest`.

| Befund | Folge |
|---|---|
| Liegen die Seiten in `pages/` neben dem Einstiegsskript, führt Streamlit bei einem Direktlink auf eine Unterseite nur die Seiten-Datei aus. In `AppTest` passierte dasselbe nach jeder Interaktion. | Seiten liegen in `app/views/`. |
| Bei `streamlit run app/app.py` liegt nur `app/` auf `sys.path`, `import src...` schlägt fehl. | Einstieg ist `streamlit_app.py` im Repo-Root. |
| Query-Parameter werden beim Seitenwechsel gelöscht. | Die Sprache liegt in `st.session_state`, das Einstiegsskript schreibt `lang` bei jedem Lauf in die URL. |
| Ein Widget ohne festes `key=` verliert seinen Wert beim Sprachwechsel, mit `key=` nicht. | Jedes Eingabe-Widget bekommt ein festes `key=`. |
| Beim Verlassen einer Seite und der Rückkehr sind die Eingaben zurückgesetzt. | Bekannt, wird nicht behoben. |
| Mit `[theme.light]` und `[theme.dark]` folgt die App der Systemeinstellung, im Menü oben rechts stehen „System“, „Light“, „Dark“. | Das ist der Umschalter. Einen eigenen Schalter kann die App nicht anbieten. |
| `st.context.theme.type` ändert sich nach einem Wechsel im Menü erst beim nächsten Rerun, in `AppTest` ist es `None`. | Flächen, Schrift und Gitter kommen vom Streamlit-Theme und wechseln sofort. Nur die Serienfarben hängen bis zum nächsten Rerun nach. |
| `st.plotly_chart(fig, theme="streamlit")` übernimmt die Theme-Farben und lässt explizite Layout-Werte und Serienfarben stehen. `chartCategoricalColors` aus der Config kam bei Plotly nicht an. | `src/design.py` setzt nur Diagrammregeln und Serienfarben. |
| Streamlit stellt die Theme-Farben nicht als CSS-Variablen bereit. | Kein eigenes CSS mit Farben. |

**Korrektur gegenüber dem Entwurf vom 2026-11-09:** Dort stand, `AppTest` könne
Interaktionen nach dem ersten Lauf nur eingeschränkt prüfen. Ursache war der
Ordner `pages/` in der Test-App. Mit `app/views/` lassen sich Sprachwechsel und
Seitenwechsel in `AppTest` prüfen. „Sprachwechsel löscht keine Eingaben“ ist
deshalb ein automatischer Test (#32) und keine manuelle Prüfung.

## 6. Abweichungen vom Auftrag

Von Felix angenommen:

- **V1:** #30 blockiert nur #38. #31 bis #37 werden gegen ein synthetisches
  Bundle entwickelt, das mit `build_bundle()` aus #28 gebaut wird.
- **V2:** Die Prüfung bei 390 px Breite liegt in #38, nicht in #40.
- **V3:** Die Glossartexte liegen in denselben TOML-Dateien wie die
  Übersetzungen.
- **V4:** „So liest du es“ und „In diesem Projekt“ sind nur Pflicht, wo es eine
  Skala bzw. einen Wert gibt.
- **V5:** Das Bundle enthält zusätzlich die unkalibrierten Test-Scores
  (`proba_rf_raw`, `proba_scorecard_raw`).

Aus der Prüfung in Abschnitt 5 und beim Schreiben der Issues dazugekommen:

- Einstiegsskript `streamlit_app.py` im Root statt `app/app.py`, Seiten in
  `app/views/` statt `app/pages/`.
- Der Hell/Dunkel-Umschalter ist Streamlits eigenes Menü, kein Schalter in der
  Sidebar.
- Eine Liste `PAGES` in `app/ui.py` speist Navigation, Wegweiser der Startseite
  und Smoke-Test.
- `metrics` im Bundle bezieht sich auf die kalibrierten Scores. Bei der Schwelle
  0,5 ist der Recall dort sehr niedrig; #34 ordnet das ein.
- `--max-depth` und `--min-samples-leaf` sind Parameter von
  `scripts/build_bundle.py` (#29), Startwerte 10 und 100. Die Startwerte sind
  geschätzt, nicht gemessen.
- Der Bundle-Pfad kommt aus der Umgebungsvariable `BUNDLE_PATH`, damit der
  Smoke-Test ein synthetisches Bundle unterschieben kann.

## 7. Annahmen

- Deutsche Zahlen nutzen den Punkt als Tausendertrennzeichen (`125.381`), wie im
  Auftrag geschrieben, nicht das Schweizer Hochkomma.
- Die Kacheln der Startseite zeigen die Werte des Random Forest.
- Kategorienwerte aus den Daten (z. B. `debt_consolidation`) bleiben unübersetzt.
- Die Kennzahlen im Dashboard stammen aus dem Bundle, also vom begrenzten und
  kalibrierten Deployment-Forest. Sie weichen von den Notebook-Werten
  (AUC 0,7168) leicht ab.

## 8. Abarbeitung

Die Cloud-Relay-Werkzeuge stehen in der lokalen Session nicht zur Verfügung, und
für dieses Repo gibt es keine Fallback-Routine mehr. Das Epic wird deshalb lokal
orchestriert: Eine Orchestrator-Session startet je Issue eine Worker-Session und
danach eine Reviewer-Session und mergt den PR, wenn das Review durch und die
CI-Pipeline grün ist. Die Regeln dafür stehen in `CLAUDE.md` unter „Work plan“.

## 9. Offen bei Felix

- URLs für LinkedIn und Website (als Kommentar an #43).
- #38 braucht seinen Account bei Streamlit Community Cloud.
