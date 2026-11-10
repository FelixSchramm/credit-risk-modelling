"""Feature engineering: turn the cleaned data into a numeric feature matrix."""

from __future__ import annotations

import pandas as pd


def convert_emp_length(value: str | float) -> int:
    """Convert the ``emp_length`` text into whole years.

    ``< 1 year`` and missing values become 0, ``10+ years`` becomes 10.

    :param value: Raw ``emp_length`` entry, e.g. ``"3 years"``.
    :return: Employment length in years.
    """
    if pd.isna(value) or value == "n/a":
        return 0
    if "< 1 year" in value:
        return 0
    if "10+ years" in value:
        return 10
    return int(value.split()[0])


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Make every column numeric: ``term``, ``emp_length`` and one-hot encoding.

    :param df: Cleaned data with the target column still included.
    :return: A copy in which all features are numeric.
    """
    df = df.copy()
    df["term"] = df["term"].str.extract(r"(\d+)").astype(int)
    df["emp_length"] = df["emp_length"].apply(convert_emp_length)

    categorical_cols = df.select_dtypes(include=["str", "object"]).columns
    return pd.get_dummies(df, columns=categorical_cols, drop_first=True)
