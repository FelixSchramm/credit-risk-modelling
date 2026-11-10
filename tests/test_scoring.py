"""Tests for :mod:`src.scoring` against the synthetic bundle of ``conftest.py``."""

import numpy as np
import pandas as pd
import pytest

from src.scoring import (
    band_of,
    build_feature_vector,
    build_scorecard_row,
    percentile_of,
    score,
)


def _purpose_dummies(bundle: dict) -> list[str]:
    return [n for n in bundle["feature_names"] if n.startswith("purpose_")]


def test_vector_has_exactly_the_feature_names_in_order(bundle):
    vector = build_feature_vector({"loan_amnt": 5000}, bundle)
    assert list(vector.columns) == bundle["feature_names"]
    assert len(vector) == 1


def test_column_order_does_not_depend_on_the_order_of_the_defaults(bundle):
    shuffled = {
        "feature_defaults": dict(reversed(bundle["feature_defaults"].items())),
        "scorecard_defaults": dict(reversed(bundle["scorecard_defaults"].items())),
    }
    changed = {**bundle, **shuffled}
    vector = build_feature_vector({"purpose": "house"}, changed)
    row = build_scorecard_row({"purpose": "house"}, changed)
    assert list(vector.columns) == bundle["feature_names"]
    assert list(row.columns) == bundle["scorecard_columns"]


def test_unspecified_fields_keep_the_defaults(bundle):
    vector = build_feature_vector({"loan_amnt": 5000}, bundle)
    row = vector.iloc[0]
    for name, default in bundle["feature_defaults"].items():
        if name != "loan_amnt":
            assert row[name] == default
    assert row["loan_amnt"] == 5000
    assert "issue_year" in vector.columns


def test_text_inputs_are_converted_like_in_training(bundle):
    row = build_feature_vector(
        {"term": " 60 months", "emp_length": "< 1 year"}, bundle
    ).iloc[0]
    assert row["term"] == 60
    assert row["emp_length"] == 0


def test_categorical_input_sets_exactly_one_dummy(bundle):
    dummies = _purpose_dummies(bundle)
    assert len(dummies) == 2  # three categories, drop_first removed one
    for category in ("car", "house", "other"):
        row = build_feature_vector({"purpose": category}, bundle).iloc[0]
        active = [n for n in dummies if row[n]]
        if f"purpose_{category}" in dummies:
            assert active == [f"purpose_{category}"]
        else:
            assert active == []  # reference category: no column of its own


def test_categorical_input_clears_a_dummy_that_is_set_by_default(bundle):
    # In the real portfolio the mode of a dummy can be 1; the input must win.
    dummies = _purpose_dummies(bundle)
    defaults = {**bundle["feature_defaults"], **{n: True for n in dummies}}
    row = build_feature_vector(
        {"purpose": "car"}, {**bundle, "feature_defaults": defaults}
    ).iloc[0]
    assert not row[dummies].any()  # "car" is the reference category


def test_unknown_field_or_category_raises(bundle):
    for build in (build_feature_vector, build_scorecard_row):
        with pytest.raises(ValueError, match="Unknown input fields"):
            build({"loan_amount": 5000}, bundle)
        with pytest.raises(ValueError, match="Unknown category"):
            build({"purpose": "yacht"}, bundle)


def test_scorecard_row_keeps_raw_categories_and_column_order(bundle):
    row = build_scorecard_row({"purpose": "car", "term": " 60 months"}, bundle)
    assert list(row.columns) == bundle["scorecard_columns"]
    assert row.iloc[0]["purpose"] == "car"
    assert row.iloc[0]["term"] == " 60 months"
    assert row.iloc[0]["annual_inc"] == bundle["scorecard_defaults"]["annual_inc"]


def test_score_returns_probabilities_for_both_models(bundle):
    result = score({"int_rate": 12.0, "purpose": "house"}, bundle)
    assert set(result) == {"rf", "scorecard"}
    assert all(0 <= p <= 1 for p in result.values())


def test_higher_interest_rate_does_not_lower_the_scorecard_pd(bundle):
    low = score({"int_rate": 6.0}, bundle)["scorecard"]
    high = score({"int_rate": 25.0}, bundle)["scorecard"]
    assert high > low


def test_higher_interest_rate_does_not_lower_the_forest_pd(bundle):
    # Without the scaler the forest compares raw values with scaled thresholds
    # and returns the same score for every rate.
    low = score({"int_rate": 6.0}, bundle)["rf"]
    high = score({"int_rate": 25.0}, bundle)["rf"]
    assert high > low


def test_percentile_of_counts_scores_at_or_below():
    reference = np.array([0.1, 0.2, 0.3, 0.4])
    assert percentile_of(0.3, reference) == 75.0
    assert percentile_of(0.0, reference) == 0.0
    assert percentile_of(0.9, reference) == 100.0


def test_band_of_covers_bands_gaps_and_extremes():
    bands = pd.DataFrame({"band": [1, 2, 3], "score_max": [0.1, 0.3, 0.6]})
    assert band_of(0.05, bands) == 1
    assert band_of(0.1, bands) == 1
    assert band_of(0.2, bands) == 2  # between score_max of band 1 and 2
    assert band_of(0.9, bands) == 3  # above the last band
