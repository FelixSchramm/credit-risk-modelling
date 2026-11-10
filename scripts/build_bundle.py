"""Build the model bundle for the dashboard from the raw LendingClub CSV.

Smoke test first, full run afterwards::

    python scripts/build_bundle.py --data 02_data/raw/accepted_2007_to_2018Q4.csv --nrows 100000
    python scripts/build_bundle.py --data 02_data/raw/accepted_2007_to_2018Q4.csv

The script only wires the functions of :mod:`src`: the cleaning chain of the
notebook, then :func:`src.bundle.build_bundle` twice with the same seed. The
first run uses an unlimited ("analysis") forest and only contributes its
metrics; the second run uses the depth-limited ("deployment") forest, which is
the one stored in the bundle. Equal seeds give equal splits, so both forests
are scored on the same test loans. The price is that the scorecard is trained
twice.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import pandas as pd
import shap

# The script lives in scripts/, the src package in the project root.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.bundle import build_bundle, save_bundle
from src.data_processing import (
    add_issue_year,
    create_target,
    drop_leakage_columns,
    filter_issue_years,
    load_raw_data,
    rm_nas,
)

#: Columns the user may enter in the dashboard calculator.
INPUT_FIELDS = [
    "loan_amnt",
    "term",
    "int_rate",
    "annual_inc",
    "dti",
    "fico_range_low",
    "emp_length",
    "purpose",
]


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Run the cleaning chain of the notebook (sections 2 and 3).

    :param df: Raw LendingClub data.
    :return: Cleaned frame with ``target``, ``term`` and ``emp_length`` still
        as text and no missing values.
    """
    df = filter_issue_years(add_issue_year(df), start_year=2015, end_year=2018)
    df = drop_leakage_columns(rm_nas(create_target(df), threshold=0.4))
    return df.dropna()


def time_treeshap(bundle: dict[str, object]) -> float:
    """Time TreeSHAP for one row of the bundled forest.

    :param bundle: Bundle from :func:`src.bundle.build_bundle`.
    :return: Seconds for one ``shap_values`` call (explainer set-up excluded).
    """
    forest = bundle["rf"].calibrated_classifiers_[0].estimator.estimator
    row = pd.DataFrame([bundle["feature_defaults"]])[bundle["feature_names"]]
    row = bundle["scaler"].transform(row)
    explainer = shap.TreeExplainer(forest)
    start = time.perf_counter()
    explainer.shap_values(row)
    return time.perf_counter() - start


def format_metrics(name: str, metrics: dict[str, object]) -> str:
    """Format one model's discrimination metrics as a line.

    :param name: Label of the model.
    :param metrics: Entry of ``bundle["metrics"]``.
    :return: Single line with ROC AUC, Gini and KS.
    """
    return (
        f"  {name:<28} ROC AUC {metrics['roc_auc']:.4f}  "
        f"Gini {metrics['gini']:.4f}  KS {metrics['ks']:.4f}"
    )


def main(argv: list[str] | None = None) -> None:
    """Parse the arguments, build the bundle and print the summary.

    :param argv: Command line arguments; ``None`` reads ``sys.argv``.
    :return: None.
    """
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--data", required=True, help="path to the raw CSV")
    parser.add_argument("--nrows", type=int, help="read only the first N rows")
    parser.add_argument("--out", default="04_models/bundle.joblib")
    parser.add_argument("--max-depth", type=int, default=10)
    parser.add_argument("--min-samples-leaf", type=int, default=100)
    args = parser.parse_args(argv)

    start = time.perf_counter()
    print(f"Loading {args.data} (nrows={args.nrows}) ...", flush=True)
    raw = load_raw_data(args.data, nrows=args.nrows)
    df = clean(raw)
    print(f"Rows: {len(raw):,} raw -> {len(df):,} after cleaning", flush=True)
    del raw

    print("Training the analysis forest (unlimited) and the scorecard ...", flush=True)
    analysis = build_bundle(df, INPUT_FIELDS)
    analysis_metrics = analysis["metrics"]["rf"]
    del analysis  # the unlimited forest is several hundred MB in memory

    print(
        f"Training the deployment forest (max_depth={args.max_depth}, "
        f"min_samples_leaf={args.min_samples_leaf}) and the scorecard ...",
        flush=True,
    )
    bundle = build_bundle(
        df,
        INPUT_FIELDS,
        max_depth=args.max_depth,
        min_samples_leaf=args.min_samples_leaf,
    )
    save_bundle(bundle, args.out)

    print(f"\nn_train {bundle['n_train']:,}  n_test {bundle['n_test']:,}")
    print("Test-set metrics (calibrated):")
    print(format_metrics("analysis forest (unlimited)", analysis_metrics))
    print(format_metrics("deployment forest", bundle["metrics"]["rf"]))
    print(format_metrics("scorecard", bundle["metrics"]["scorecard"]))
    auc_loss = analysis_metrics["roc_auc"] - bundle["metrics"]["rf"]["roc_auc"]
    print(f"ROC AUC lost by the depth limit: {auc_loss:+.4f}")
    size_mb = Path(args.out).stat().st_size / 1e6
    print(f"Bundle size: {size_mb:.1f} MB (target: at most 50 MB)")
    print(f"TreeSHAP, one row: {time_treeshap(bundle):.3f} s (target: below 1 s)")
    print(f"Wall-clock time: {(time.perf_counter() - start) / 60:.1f} min")


if __name__ == "__main__":
    main()
