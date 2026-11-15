# Plan: model performance page (issue #34)

1. `app/views/performance.py`, registered in `PAGES` after `calculator`;
   `nav.performance` and `nav_desc.performance` in both locale files.
2. Sections (all texts via `t()`, numbers via `num()` / `pct()`, tooltips via
   `help_text`, charts via `show_chart`, colours via `model_color`):
   - Metrics: AUC, Gini, KS per model as `st.metric` (tooltips `auc`, `gini`,
     `ks`). The magnitude ranges stay in the glossary, not repeated here.
   - ROC curve of both models (`sklearn.metrics.roc_curve`) plus the diagonal.
   - Calibration (`sklearn.calibration.calibration_curve`, quantile bins):
     before (raw scores, dashed, label "before") and after (calibrated, solid,
     label "after") per model, colour by model; diagonal as reference.
   - Score bands: bar chart of the observed default rate per decile (bars, not
     status colours) with the mean score as marker line, a table from
     `bands_*`, one sentence on monotonicity (`is_monotonic_increasing`),
     model chosen by a radio with a fixed key.
   - Classification report: precision, recall, F1, accuracy per model as a
     table parsed from the stored report is avoided; the report text is shown
     as code, with the note that 0.5 is no sensible threshold for calibrated
     scores and a pointer to the cut-off page (#35).
3. No new `src/` logic: ROC, calibration, bands and monotonicity are direct
   library or pandas calls on bundle arrays (bands already come from
   `bands_*`). Glossary keys all exist in both languages.
4. Tests: smoke tests in both languages (metrics equal the bundle, charts
   present, monotonicity statement, start page guide lists the page).
5. Real bundle: band table and metrics for the PR, headless start, screenshots.
