# Plan: issue #30, full training run and model bundle

1. Run `scripts/build_bundle.py` on the full raw CSV (in the background, log to file).
2. Evaluate in order: ROC AUC above about 0.80 means leakage (abort, no bundle);
   bundle at most 50 MB and TreeSHAP below 1 s; depth-limit cost at most 0.005 ROC AUC.
   Tighten or loosen `--max-depth` / `--min-samples-leaf` if needed, at most three full runs.
3. Commit `04_models/bundle.joblib` (narrow `.gitignore` exception, no Git LFS).
4. If the final parameters differ from the defaults, align the script defaults and README.
5. README: fill "Results" with the measured values, update "Repository layout".
6. HANDOVER.md: new subsection "Issue #30 - bundle run" with commands and complete output.
7. pytest, black, ruff; push; open the PR against `main`.
