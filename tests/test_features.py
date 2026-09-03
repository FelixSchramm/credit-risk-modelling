"""Tests for the feature engineering in :mod:`src.features`."""

import numpy as np
import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from src.features import convert_emp_length, engineer_features


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("< 1 year", 0),
        ("1 year", 1),
        ("3 years", 3),
        ("10+ years", 10),
        (np.nan, 0),
    ],
)
def test_convert_emp_length(value, expected):
    assert convert_emp_length(value) == expected


def test_engineer_features_makes_every_column_numeric():
    """``term`` and ``emp_length`` become numbers, the rest is one-hot encoded.

    ``drop_first=True`` keeps only the ``RENT`` dummy: ``OWN`` is the reference
    category and is implied by all dummies being false.
    """
    df = pd.DataFrame(
        {
            "term": [" 36 months", " 60 months"],
            "emp_length": ["3 years", "10+ years"],
            "home_ownership": ["RENT", "OWN"],
            "target": [0, 1],
        }
    )
    expected = pd.DataFrame(
        {
            "term": [36, 60],
            "emp_length": [3, 10],
            "target": [0, 1],
            "home_ownership_RENT": [True, False],
        }
    )
    assert_frame_equal(engineer_features(df), expected)
