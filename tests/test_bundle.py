"""Tests for :mod:`src.bundle`, run on a small synthetic frame."""

import numpy as np
import pandas as pd
import pytest

from src.bundle import (
    build_bundle,
    calibrate,
    input_spec,
    load_bundle,
    save_bundle,
    score_bands,
)
from src.train import train_random_forest

CONTRACT_KEYS = {
    "version",
    "created_at",
    "n_train",
    "n_test",
    "base_rate",
    "feature_names",
    "feature_defaults",
    "scaler",
    "rf",
    "scorecard",
    "scorecard_columns",
    "scorecard_defaults",
    "input_spec",
    "metrics",
    "y_test",
    "proba_rf",
    "proba_scorecard",
    "proba_rf_raw",
    "proba_scorecard_raw",
    "bands_rf",
    "bands_scorecard",
    "iv_table",
}


def _loans(n: int = 1500) -> pd.DataFrame:
    """Build a LendingClub-shaped frame whose default risk depends on ``rate``.

    :param n: Number of rows.
    :return: Unencoded frame with a ``target`` column.
    """
    rng = np.random.default_rng(0)
    rate = rng.normal(12, 4, n)
    risk = 1 / (1 + np.exp(-(rate - 14) / 2))
    return pd.DataFrame(
        {
            "loan_amnt": rng.integers(1000, 35000, n),
            "rate": rate,
            "term": rng.choice([" 36 months", " 60 months"], n),
            "emp_length": rng.choice(["< 1 year", "3 years", "10+ years"], n),
            "purpose": rng.choice(["car", "house", "other"], n),
            "target": rng.binomial(1, risk),
        }
    )


@pytest.fixture(scope="module")
def bundle() -> dict:
    """Build one small bundle that all bundle tests share."""
    return build_bundle(_loans(), fields=["loan_amnt", "purpose"])


def test_score_bands_split_into_equal_ordered_bands():
    bands = score_bands(np.arange(100) % 2, np.arange(100) / 100)
    assert len(bands) == 10
    assert bands["n"].sum() == 100
    assert (bands["n"] == 10).all()
    assert bands["score_min"].iloc[0] == 0
    assert bands["score_max"].iloc[-1] == 0.99
    assert bands["score_max"].iloc[0] < bands["score_min"].iloc[1]


def test_score_bands_report_the_observed_default_rate():
    bands = score_bands([0] * 5 + [1] * 5, np.linspace(0, 1, 10), n_bands=2)
    assert list(bands["default_rate"]) == [0.0, 1.0]


def test_score_bands_handle_equal_scores():
    bands = score_bands([0, 1, 0, 1, 0, 1], np.full(6, 0.3), n_bands=3)
    assert list(bands["n"]) == [2, 2, 2]


def test_score_bands_handle_fewer_rows_than_bands():
    bands = score_bands([0, 1, 1], [0.1, 0.5, 0.9])
    assert len(bands) == 3
    assert bands["n"].sum() == 3


def test_input_spec_distinguishes_numeric_and_categorical():
    df = pd.DataFrame(
        {
            "amount": np.arange(1, 102),
            "purpose": ["b", "a", "b"] * 33 + ["a", "b"],
        }
    )
    spec = input_spec(df, ["amount", "purpose"])
    assert spec["amount"] == {
        "type": "numeric",
        "min": 2.0,
        "max": 100.0,
        "median": 51.0,
    }
    assert spec["purpose"] == {
        "type": "categorical",
        "categories": ["a", "b"],
        "default": "b",
    }


def test_calibrate_moves_probabilities_towards_the_base_rate():
    """The balanced forest overestimates defaults; calibration must undo that."""
    df = _loans(3000)
    x, y = df[["loan_amnt", "rate"]], df["target"]
    model = train_random_forest(x[:1000], y[:1000])
    raw = model.predict_proba(x[2000:])[:, 1]
    calibrated = calibrate(model, x[1000:2000], y[1000:2000]).predict_proba(x[2000:])[
        :, 1
    ]
    assert ((calibrated >= 0) & (calibrated <= 1)).all()
    base_rate = y[2000:].mean()
    assert abs(calibrated.mean() - base_rate) < abs(raw.mean() - base_rate)


def test_bundle_round_trip_keeps_keys_and_column_order(bundle, tmp_path):
    path = tmp_path / "bundle.joblib"
    save_bundle(bundle, path)
    loaded = load_bundle(path)
    assert set(loaded) == CONTRACT_KEYS
    assert loaded["feature_names"] == bundle["feature_names"]
    assert loaded["scorecard_columns"] == bundle["scorecard_columns"]


def test_bundle_contents_are_consistent(bundle):
    assert set(bundle) == CONTRACT_KEYS
    assert set(bundle["metrics"]) == {"rf", "scorecard"}
    assert set(bundle["metrics"]["rf"]) == {"roc_auc", "gini", "ks", "report"}
    assert len(bundle["y_test"]) == bundle["n_test"] == len(bundle["proba_rf_raw"])
    assert bundle["y_test"].dtype == np.int8
    assert bundle["proba_rf"].dtype == np.float32
    assert bundle["scaler"].n_features_in_ == len(bundle["feature_names"])
    assert set(bundle["feature_defaults"]) == set(bundle["feature_names"])
    # Calibrated scores must sit closer to the base rate than the balanced raw ones.
    base_rate = bundle["base_rate"]
    assert abs(bundle["proba_rf"].mean() - base_rate) < abs(
        bundle["proba_rf_raw"].mean() - base_rate
    )
