# Plan: issue #28, artefact bundle with calibration

Goal: `src/bundle.py` writes everything the Streamlit app needs (models,
scaler, column order, defaults, UI spec, test-set scores, metrics) into one
joblib file. It only bundles results of the existing `src/` functions.

1. `calibrate(model, x_calib, y_calib)`: isotonic `CalibratedClassifierCV`
   around `FrozenEstimator` (scikit-learn 1.9, no `cv="prefit"`).
2. `score_bands(y_true, y_proba, n_bands=10)`: rank-based deciles via
   `pd.qcut` so ties and fewer rows than bands do not break it.
3. `input_spec(df_unencoded, fields)`: numeric fields get 1 %/99 % quantiles and
   the median, others the category list and the mode.
4. `build_bundle(df, fields)`: split with `split_and_scale`, carve a calibration
   split out of the training part, fit forest and scorecard on the rest,
   calibrate both on the calibration split, evaluate on the test set with
   `evaluate_model`, assemble the contract dict (including `proba_*_raw`).
5. `save_bundle` / `load_bundle`: `joblib`, `compress=3`, print file size.
6. `tests/test_bundle.py` on a small synthetic frame (no raw data), README
   layout block and `HANDOVER.md` updated.
