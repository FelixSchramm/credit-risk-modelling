# Issue 11: Repo-Hygiene (.DS_Store entfernen, Warnings gezielt behandeln)

**Priorität:** P3 (Politur)
**Status:** Open
**Betrifft:** Repo-Root, `02_data/`, `01_notebooks/prediction.ipynb`, `.gitignore`

## Kontext

Kleinere, aber leicht sichtbare Hygiene-Probleme:

1. Zwei `.DS_Store`-Dateien (macOS-Metadaten) sind versehentlich ins Repo committet
   worden: im Repo-Root und unter `02_data/`. Solche Dateien gehören nie ins Git-Repo.
2. Im Notebook wird global `warnings.filterwarnings('ignore')` gesetzt. Das unterdrückt
   **alle** Warnungen ab diesem Punkt, inklusive potenziell relevanter Hinweise (z. B.
   pandas `SettingWithCopyWarning`, die auf echte Bugs hindeuten können).

## Ziel

Ein sauberes Repo ohne OS-Metadatendateien, und ein bewussterer, engerer Umgang mit
Warning-Unterdrückung.

## Umsetzungsschritte

1. `.DS_Store` zu `.gitignore` hinzufügen (falls noch nicht vorhanden).
2. Bestehende `.DS_Store`-Dateien aus dem Repo entfernen:
   ```
   git rm --cached .DS_Store 02_data/.DS_Store
   ```
   (Pfade ggf. an tatsächlichen Fundort anpassen.)
3. `warnings.filterwarnings('ignore')` im Notebook durch gezielte Unterdrückung ersetzen,
   z. B.:
   - Nur bestimmte Warnungskategorien/Module unterdrücken (`category=FutureWarning`,
     `module="sklearn.*"`), statt global alles.
   - Alternativ: Unterdrückung nur lokal um die konkrete Zelle/den konkreten Aufruf herum
     (z. B. mit `with warnings.catch_warnings(): warnings.simplefilter(...)`).
4. Kurz prüfen, ob durch das Entfernen der globalen Unterdrückung neue, bisher
   verschluckte Warnungen sichtbar werden, die auf echte Probleme hindeuten (z. B.
   Chained-Assignment-Warnungen bei DataFrame-Operationen) — falls ja, als eigenen Punkt
   notieren/beheben.

## Betroffene Dateien

- `.gitignore`
- `01_notebooks/prediction.ipynb`
- ggf. Repo-Historie (`.DS_Store`-Dateien)

## Akzeptanzkriterien / Definition of Done

- [ ] Keine `.DS_Store`-Datei mehr im Repo (weder getrackt noch künftig committbar).
- [ ] `warnings.filterwarnings('ignore')` ist nicht mehr global am Notebook-Anfang gesetzt,
      sondern gezielt/lokal eingesetzt.
