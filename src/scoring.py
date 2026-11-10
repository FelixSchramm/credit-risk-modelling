"""Scoring layer of the dashboard: turn one application into a calibrated PD.

Pure functions on the bundle from :mod:`src.bundle`; no Streamlit import, so
everything here is covered by the tests.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.features import convert_emp_length


def _check_input(user_input: dict[str, object], bundle: dict[str, object]) -> None:
    """Reject unknown fields and categories instead of ignoring them silently.

    :param user_input: Field name to entered value.
    :param bundle: Bundle with ``input_spec``.
    :return: None.
    :raises ValueError: If a field or a category is not part of ``input_spec``.
    """
    spec = bundle["input_spec"]
    unknown = sorted(set(user_input) - set(spec))
    if unknown:
        raise ValueError(f"Unknown input fields: {unknown}; allowed: {sorted(spec)}")
    for field, value in user_input.items():
        categories = spec[field].get("categories")
        if categories is not None and value not in categories:
            raise ValueError(f"Unknown category {value!r} for {field!r}")


def build_feature_vector(
    user_input: dict[str, object], bundle: dict[str, object]
) -> pd.DataFrame:
    """Build the one-row, unscaled feature vector of the forest.

    Everything the user does not enter stays at the portfolio default
    (``feature_defaults``). A categorical input sets its dummy column and
    clears the other dummies of the same group; the reference category (the
    one dropped by ``drop_first``) has no column, so all of its dummies are 0.

    :param user_input: Field name to entered value; ``term`` and ``emp_length``
        as text like in the raw data, e.g. ``" 36 months"``.
    :param bundle: Bundle from :func:`src.bundle.build_bundle`.
    :return: One row with exactly ``bundle["feature_names"]`` as columns.
    :raises ValueError: For an unknown field or category.
    """
    _check_input(user_input, bundle)
    names = bundle["feature_names"]
    values = dict(bundle["feature_defaults"])
    raw_columns = set(bundle["scorecard_columns"])
    for field, value in user_input.items():
        if field == "term":
            values[field] = int(value.split()[0])
        elif field == "emp_length":
            values[field] = convert_emp_length(value)
        elif field in values:
            values[field] = value
        else:
            # Dummy columns look like "<field>_<category>" and are not raw columns.
            for name in names:
                if name.startswith(f"{field}_") and name not in raw_columns:
                    values[name] = name == f"{field}_{value}"
    return pd.DataFrame([values])[names]


def build_scorecard_row(
    user_input: dict[str, object], bundle: dict[str, object]
) -> pd.DataFrame:
    """Build the one-row, unencoded input of the scorecard.

    :param user_input: Field name to entered value, as for
        :func:`build_feature_vector`.
    :param bundle: Bundle from :func:`src.bundle.build_bundle`.
    :return: One row with exactly ``bundle["scorecard_columns"]`` as columns.
    :raises ValueError: For an unknown field or category.
    """
    _check_input(user_input, bundle)
    values = {**bundle["scorecard_defaults"], **user_input}
    return pd.DataFrame([values])[bundle["scorecard_columns"]]


def score(user_input: dict[str, object], bundle: dict[str, object]) -> dict[str, float]:
    """Score one application with both models.

    :param user_input: Field name to entered value.
    :param bundle: Bundle from :func:`src.bundle.build_bundle`.
    :return: Calibrated default probability per model (``"rf"``,
        ``"scorecard"``).
    """
    x_rf = bundle["scaler"].transform(build_feature_vector(user_input, bundle))
    x_scorecard = build_scorecard_row(user_input, bundle)
    return {
        "rf": float(bundle["rf"].predict_proba(x_rf)[0, 1]),
        "scorecard": float(bundle["scorecard"].predict_proba(x_scorecard)[0, 1]),
    }


def percentile_of(proba: float, reference: np.ndarray) -> float:
    """Rank of a score in the test portfolio.

    :param proba: Default probability of the application.
    :param reference: Test-set scores of the same model (``proba_rf`` or
        ``proba_scorecard``).
    :return: Percentage of test loans with a score at or below ``proba``.
    """
    return float((np.asarray(reference) <= proba).mean() * 100)


def band_of(proba: float, bands: pd.DataFrame) -> int:
    """Find the risk band of a score.

    A score between two bands goes to the higher one, a score above the last
    band to the last band.

    :param proba: Default probability of the application.
    :param bands: ``bands_rf`` or ``bands_scorecard`` from the bundle.
    :return: Number of the band (1 is the lowest risk).
    """
    position = np.searchsorted(bands["score_max"].to_numpy(), proba)
    return int(bands["band"].iloc[min(position, len(bands) - 1)])
