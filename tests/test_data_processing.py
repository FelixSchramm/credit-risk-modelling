"""Tests for the cleaning steps in :mod:`src.data_processing`."""

import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from src.data_processing import create_target, drop_leakage_columns, rm_nas


def test_rm_nas_drops_only_columns_above_the_threshold():
    """A column with 60% missing goes, one with 20% stays."""
    df = pd.DataFrame(
        {
            "sparse": [1.0, None, None, None, None],
            "dense": [1.0, 2.0, 3.0, 4.0, None],
        }
    )
    assert list(rm_nas(df).columns) == ["dense"]


def test_rm_nas_keeps_a_column_exactly_at_the_threshold():
    """The threshold is exclusive: 40% missing is still acceptable."""
    df = pd.DataFrame({"edge": [1.0, 2.0, 3.0, None, None]})
    assert list(rm_nas(df).columns) == ["edge"]


def test_rm_nas_leaves_complete_data_untouched():
    df = pd.DataFrame({"a": [1, 2], "b": ["x", "y"]})
    assert_frame_equal(rm_nas(df), df)


@pytest.mark.parametrize(
    "df",
    [pd.DataFrame(), pd.DataFrame(columns=["a", "b"])],
    ids=["no rows and no columns", "columns but no rows"],
)
def test_rm_nas_handles_empty_input(df):
    """An empty frame has no missing share to exceed the threshold."""
    assert_frame_equal(rm_nas(df), df)


def test_drop_leakage_columns_removes_post_outcome_and_irrelevant_columns():
    """Post-outcome fields go, features known at origination stay.

    ``fico_range_low`` is the interesting case: it looks like the dropped
    ``last_fico_range_low`` but is the score at origination and must survive.
    """
    df = pd.DataFrame(
        {
            "loan_amnt": [1000],
            "fico_range_low": [700],
            "target": [0],
            "recoveries": [0.0],
            "last_fico_range_low": [650],
            "hardship_type": ["INTEREST ONLY-3 MONTHS DEFERRAL"],
            "settlement_amount": [500.0],
            "grade": ["B"],
            "url": ["https://example.com"],
        }
    )
    result = drop_leakage_columns(df)
    assert list(result.columns) == ["loan_amnt", "fico_range_low", "target"]


def test_drop_leakage_columns_ignores_columns_that_are_absent():
    """Most deny-listed columns are already gone by the time this runs."""
    df = pd.DataFrame({"loan_amnt": [1000], "total_pymnt": [500.0]})
    assert list(drop_leakage_columns(df).columns) == ["loan_amnt"]


def test_create_target_keeps_completed_loans_and_encodes_the_outcome():
    """Running loans have no known outcome and must not become non-defaults."""
    df = pd.DataFrame(
        {"loan_status": ["Fully Paid", "Charged Off", "Current", "Late (31-120 days)"]}
    )
    result = create_target(df)
    assert list(result["loan_status"]) == ["Fully Paid", "Charged Off"]
    assert list(result["target"]) == [0, 1]
