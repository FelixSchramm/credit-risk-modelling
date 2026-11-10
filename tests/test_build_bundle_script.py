"""End-to-end test of ``scripts/build_bundle.py`` on a synthetic CSV."""

import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd

from src.bundle import load_bundle

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "build_bundle.py"


def _load_script():
    """Import the script by path; ``scripts/`` is not a package.

    :return: The imported module.
    """
    spec = importlib.util.spec_from_file_location("build_bundle_script", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _raw_csv(path: Path, n: int = 2000) -> None:
    """Write a small LendingClub-shaped raw CSV.

    Contains out-of-window loans, unfinished loans, a mostly-empty column and
    a leakage column, so every cleaning step has work to do.

    :param path: Target CSV file.
    :param n: Number of rows.
    """
    rng = np.random.default_rng(0)
    rate = rng.normal(13, 4, n)
    risk = 1 / (1 + np.exp(-(rate - 15) / 2))
    status = np.where(rng.binomial(1, risk) == 1, "Charged Off", "Fully Paid")
    status[:100] = "Current"
    pd.DataFrame(
        {
            "loan_amnt": rng.integers(1000, 35000, n),
            "term": rng.choice([" 36 months", " 60 months"], n),
            "int_rate": rate,
            "annual_inc": rng.normal(70000, 20000, n).round(),
            "dti": rng.uniform(0, 35, n),
            "fico_range_low": rng.integers(660, 800, n),
            "emp_length": rng.choice(["< 1 year", "3 years", "10+ years"], n),
            "purpose": rng.choice(["car", "house", "other"], n),
            "issue_d": rng.choice(["Jan-2014", "Mar-2016", "Jul-2017"], n),
            "loan_status": status,
            "mostly_empty": np.where(rng.random(n) < 0.9, np.nan, 1.0),
            "total_pymnt": rng.uniform(0, 40000, n),
        }
    ).to_csv(path, index=False)


def test_script_builds_a_loadable_bundle_and_reports(tmp_path, capsys):
    csv, out = tmp_path / "raw.csv", tmp_path / "bundle.joblib"
    _raw_csv(csv)
    _load_script().main(
        ["--data", str(csv), "--out", str(out), "--max-depth", "4", "--nrows", "1900"]
    )

    bundle = load_bundle(out)
    forest = bundle["rf"].calibrated_classifiers_[0].estimator.estimator
    assert max(tree.get_depth() for tree in forest.estimators_) <= 4
    # 2014 loans and unfinished loans are dropped: about 2/3 of 1800 remain.
    assert bundle["n_train"] + bundle["n_test"] < 1300

    printed = capsys.readouterr().out
    for expected in (
        "after cleaning",
        "analysis forest (unlimited)",
        "deployment forest",
        "scorecard",
        "ROC AUC lost",
        "Bundle size",
        "TreeSHAP, one row",
        "n_train",
    ):
        assert expected in printed
