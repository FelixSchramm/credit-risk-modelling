# Issue 04: Notebook-Reproduzierbarkeit herstellen und Kurs-Artefakte entfernen

**Priorität:** P1 (Struktur/Professionalität)
**Status:** Open
**Betrifft:** `01_notebooks/prediction.ipynb`

## Kontext

Das Notebook `01_notebooks/prediction.ipynb` wurde offenbar nie sauber "Restart & Run
All" durchlaufen, bevor es committet wurde: Die `execution_count`-Werte der Zellen sind
nicht-monoton (z. B. Zellreihenfolge 3→11 dann 4→8) und teilweise doppelt (der Wert 18
taucht bei zwei unterschiedlichen Zellen auf). Das ist ein klassisches
Reproduzierbarkeits-Warnsignal: Man kann nicht sicher sein, dass das Notebook von oben
nach unten in der aktuell sichtbaren Reihenfolge tatsächlich lauffähig ist.

Zusätzlich enthält das Notebook Kommentar-Reste, die wie Checklisten-Markierungen aus
einer Kursaufgabe wirken (z. B. `# (g, h, i)`, `# (b)`, `# (q)`, `# (r)`, `# (s)`,
`# (t)`, `# (u)` in mehreren Zellen), sowie mindestens eine offensichtliche
Debug-/Vergessene-Zeile: `df.info` (ohne Klammern aufgerufen — gibt nur die
Methodenreferenz aus, ruft die Methode aber nicht auf).

## Ziel

Ein Notebook, das von oben nach unten sauber durchläuft, dessen `execution_count`-Werte
monoton sind, und das frei von sichtbaren Kursaufgaben-Resten ist — stattdessen mit echten,
erklärenden Markdown-Zellen zu EDA, Feature Engineering, Modellwahl und Evaluation.

## Umsetzungsschritte

1. Nach Umsetzung von Issue 01 (Leakage-Fix) und Issue 03 (Modularisierung): Kernel neu
   starten und das Notebook komplett von oben nach unten ausführen ("Restart & Run All").
   Skriptbar geht das mit dem ohnehin installierten `nbconvert`:
   ```
   jupyter nbconvert --to notebook --execute --inplace 01_notebooks/prediction.ipynb
   ```
   Ein so ausgeführtes Notebook hat automatisch streng monotone `execution_count`-Werte —
   das erste Akzeptanzkriterium ist damit maschinell erfüllbar und prüfbar (für
   parametrisierte Läufe wäre `papermill` die Alternative, hier aber nicht nötig).
2. Alle kryptischen Kommentare wie `# (g, h, i)` etc. entfernen oder durch echte,
   erklärende Kommentare/Markdown-Zellen ersetzen, die beschreiben, *warum* ein Schritt
   gemacht wird (nicht nur *was*).
3. `df.info` → `df.info()` korrigieren (bzw. Zelle ganz entfernen, falls redundant zu
   einer anderen EDA-Zelle).
4. Jede größere Sektion (Load Data, Cleaning, Feature Engineering, Model Training,
   Evaluation) sollte eine kurze Markdown-Zelle davor haben, die Zweck und wichtigste
   Entscheidungen erklärt (z. B. "Warum Random Forest statt Logistic Regression an dieser
   Stelle", "Warum threshold=0.4 für NA-Drop").
5. Sicherstellen, dass keine Zelle Variablen referenziert, die erst später im Notebook
   definiert werden (Out-of-Order-Execution-Check).
6. Vor dem Commit final einmal frisch durchlaufen lassen und die Outputs (Plots, Tabellen)
   im committeten Notebook aktuell halten.

## Betroffene Dateien

- `01_notebooks/prediction.ipynb`

## Akzeptanzkriterien / Definition of Done

- [ ] `execution_count`-Werte sind streng monoton aufsteigend von der ersten bis zur
      letzten Code-Zelle.
- [ ] Keine kryptischen Rubrik-/Kursaufgaben-Kommentare mehr vorhanden.
- [ ] `df.info` ist korrekt als `df.info()` aufgerufen (oder entfernt).
- [ ] Jede Hauptsektion hat eine erklärende Markdown-Zelle.
- [ ] Notebook lässt sich in einer frischen Umgebung (siehe Issue 06,
      `requirements.txt`) von oben nach unten fehlerfrei ausführen.
