"""Shared fixtures: a small synthetic bundle, built by the real ``build_bundle``."""

import numpy as np
import pandas as pd
import pytest

from src.bundle import build_bundle, save_bundle

FIELDS = [
    "loan_amnt",
    "term",
    "int_rate",
    "annual_inc",
    "dti",
    "fico_range_low",
    "emp_length",
    "purpose",
]


def _loans(n: int = 1500) -> pd.DataFrame:
    """Build a LendingClub-shaped frame whose default risk depends on the rate.

    :param n: Number of rows.
    :return: Cleaned, unencoded frame with a ``target`` column.
    """
    rng = np.random.default_rng(0)
    rate = rng.normal(13, 4, n)
    risk = 1 / (1 + np.exp(-(rate - 15) / 2))
    return pd.DataFrame(
        {
            "loan_amnt": rng.integers(1000, 35000, n),
            "term": rng.choice([" 36 months", " 60 months"], n),
            "int_rate": rate,
            "annual_inc": rng.normal(70000, 20000, n).round(),
            "dti": rng.uniform(0, 35, n),
            "fico_range_low": rng.integers(660, 800, n),
            "emp_length": rng.choice(["< 1 year", "3 years", "10+ years"], n),
            "purpose": rng.choice(["car", "house", "other"], n),
            "issue_year": rng.choice([2015, 2016, 2017], n),
            "target": rng.binomial(1, risk),
        }
    )


@pytest.fixture(scope="session")
def bundle() -> dict:
    """One small bundle shared by all tests of the session."""
    return build_bundle(_loans(), FIELDS)


@pytest.fixture(scope="session")
def bundle_file(bundle, tmp_path_factory) -> str:
    """The shared bundle saved to a temporary file."""
    path = tmp_path_factory.mktemp("bundle") / "bundle.joblib"
    save_bundle(bundle, path)
    return str(path)


@pytest.fixture
def bundle_env(bundle_file, monkeypatch) -> str:
    """Point ``BUNDLE_PATH`` to the synthetic bundle, like the app expects."""
    monkeypatch.setenv("BUNDLE_PATH", bundle_file)
    return bundle_file
