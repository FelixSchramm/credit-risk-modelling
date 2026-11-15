# Plan: explanation of the single score (issue #33)

1. `src/scoring.py` (own commit, tests in a second commit):
   - `forest_explainer(bundle)`: `shap.TreeExplainer` on the inner forest
     `bundle["rf"].calibrated_classifiers_[0].estimator.estimator`. SHAP
     explains the uncalibrated forest score, not the shown calibrated PD.
   - `explain_forest(user_input, bundle, explainer)`: SHAP values of the
     positive class for the one application, plus the base value.
   - `explain_scorecard(user_input, bundle)`: per selected feature the WOE of
     the applicant's bin (`BinningProcess.transform(metric="woe")`) times the
     logistic coefficient, plus the intercept. Contribution in log-odds, not in
     scaled points: the bundle has no points scaling and the log-odds are what
     the regression adds up.
   - `top_contributions(table, n, rest_label)`: the n largest by absolute size,
     the rest summed into one row.
2. Tests: additivity (base + SHAP = uncalibrated forest probability;
   intercept + contributions = scorecard log-odds), top-n and rest sum.
3. Glossary: `shap`, `shap_base_value`, `waterfall`, `scorecard_points` and
   `woe` already exist in both languages; nothing to add.
4. `app/views/calculator.py`: below the results (variant A only), tabs forest
   and scorecard, then a short comparison. Forest: Plotly `go.Waterfall` via
   `show_chart`, with the notes on "uncalibrated" and the base value near 0.5
   (`class_weight="balanced"`). Scorecard: horizontal bars in
   `model_color("scorecard", ...)`, direction visible by sign and axis label.
   Explainer in `@st.cache_resource` in the page. Texts in both locale files.
5. Smoke tests in both languages, then real-bundle timing and additivity,
   headless start, screenshots, HANDOVER.md.
