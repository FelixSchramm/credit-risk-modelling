# Plan: issue #29, `scripts/build_bundle.py` and the deployment forest

Goal: one command turns the raw LendingClub CSV into `04_models/bundle.joblib`
and prints everything needed to decide on the bundle size.

1. `train_random_forest` and `build_bundle` get `max_depth` and
   `min_samples_leaf` (default `None` / `1`, i.e. unchanged behaviour).
2. `scripts/build_bundle.py` (argparse: `--data`, `--nrows`, `--out`,
   `--max-depth` 10, `--min-samples-leaf` 100). It only wires existing
   functions: `load_raw_data` to `dropna` (the notebook's cleaning chain),
   then `build_bundle` twice with the same seed.
   - Run 1, unlimited forest ("analysis forest"): only its metrics are kept,
     then it is freed (the unlimited forest is several hundred MB in RAM).
   - Run 2, depth-limited forest ("deployment forest"): saved as the bundle.
   Cost of the simple design: the scorecard is trained twice. Same seed means
   identical splits, so both forests are scored on the same test rows.
3. Output: row counts after cleaning, metrics of both forests and the
   scorecard, n_train/n_test, ROC AUC difference, bundle size, TreeSHAP time
   for one row of the deployment forest, wall-clock time. Progress lines
   after each step.
4. Test: write a small synthetic LendingClub-shaped CSV, run `main`, reload
   the bundle with `load_bundle`, check the printed output and the depth limit.
5. README section "Build the model bundle", layout block; `ci.yml` black
   covers `scripts`; `HANDOVER.md` updated.
