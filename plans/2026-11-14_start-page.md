# Plan: start page "Das Projekt in 60 Sekunden" (issue #43)

1. `src/locales/en.toml`, `de.toml`: fill `[home]` (problem sentence, section
   "what I did" with five points, guide title, links, notice) and add
   `[nav_desc]` with one sentence per page. Identical keys and placeholders.
2. `app/ui.py`: constant `LINKS` (key to URL), the single place for external
   URLs. Only GitHub is set; LinkedIn and website follow once the owner
   provides them (not invented).
3. `app/views/home.py`: problem sentence, four `st.metric(border=True)` tiles
   (AUC, Gini, KS of the forest, default rate of the test set) from the
   bundle with `num()`/`pct()` and `help_text()`, notice, "what I did", guide
   built from `PAGES` (`st.page_link`, `nav_desc.<key>`), link buttons.
4. `tests/test_app_smoke.py`: both languages render, four tiles match the
   bundle values, guide lists every page except home.
5. HANDOVER.md: state, pitfalls, open URL point.
