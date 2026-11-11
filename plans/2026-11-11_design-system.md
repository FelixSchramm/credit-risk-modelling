# Plan: design system (issue #40, epic #39)

1. Copy `ci.json`, `Questrial-Regular.ttf` and `OFL-Questrial.txt` unchanged
   from `FelixSchramm/stock_treemap` at commit 02a9c98; verify the git blob
   SHAs from the issue.
2. `.streamlit/config.toml`: static serving, Questrial via `fontFaces`,
   `[theme.light]` and `[theme.dark]` with values from `ci.json` only.
3. `src/design.py` (no Streamlit): `series_color`, `model_color`,
   `style_figure`. No background, font or grid colours: those come from the
   Streamlit theme so they follow the light/dark switch at once.
4. `app/ui.py`: `current_mode()` and `show_chart()`.
5. `tests/test_design.py` plus an `AppTest.from_function` test of `show_chart`.
6. Pin `plotly==7.1.0`; README design section and layout block; HANDOVER.
7. Verify: pytest, black, ruff, headless start with font URL check.
