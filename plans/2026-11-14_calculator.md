# Plan: applicant calculator (issue #32)

1. `src/scoring.py` (own commit, done): derive `funded_amnt`,
   `funded_amnt_inv`, `fico_range_high` and `installment` from the effective
   inputs for forest and scorecard, so the calculator never scores an
   impossible loan. Tests pin each derivation and one annuity value.
2. `src/locales/{en,de}.toml`: `nav.calculator`, `nav_desc.calculator` and a
   `[calculator]` section (identical keys and placeholders).
3. `app/ui.py`: register `calculator` in `PAGES` (second entry, after home).
4. `app/views/calculator.py`: title, mandatory limitation notice
   (`st.warning`, first element under the title), two columns. Left: inputs
   built from `input_spec` (fixed `key=`s), toggle for a second variant B with
   its own inputs. Right: per model (forest, scorecard) the calibrated PD
   (`help_text("pd")`), the risk band (`help_text("score_band")`) and the
   percentile in the test portfolio; variant B shows the PD difference to A as
   the metric delta. A hint appears when the two models are two or more bands
   apart. All scoring through `score`, `band_of`, `percentile_of`.
5. `tests/test_app_smoke.py`: renders in both languages, PD values match
   `score()`, notice present, delta for variant B, input survives a language
   switch.
6. Verification on the real bundle (plausibility), headless start, screenshot.
7. HANDOVER.md.
