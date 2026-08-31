"""Loading and cleaning of the LendingClub raw data.

Covers every step between reading the raw CSV and the point where only
features that are known at origination remain.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

#: Loan statuses of completed loans; only these carry a known outcome.
COMPLETED_STATUSES = ["Fully Paid", "Charged Off"]

#: Identifiers, free text and date columns that are not usable as features.
IRRELEVANT_COLS = [
    "id",
    "member_id",
    "grade",
    "sub_grade",
    "emp_title",
    "url",
    "zip_code",
    "title",
    "loan_status",  # already used to create the target variable
    "issue_d",
    "earliest_cr_line",
    "last_pymnt_d",
    "last_credit_pull_d",
]

#: Columns that are only filled after the loan was disbursed and has (partly)
#: defaulted or been repaid. They leak the target into the features and were
#: the cause of the unrealistic ROC AUC of 0.9999 (see issue #2).
#: ``last_fico_range_*`` is the FICO score updated after origination and must
#: not be confused with ``fico_range_*`` (origination values), which stay.
POST_OUTCOME_COLS = [
    "total_pymnt",
    "total_pymnt_inv",
    "total_rec_prncp",
    "total_rec_int",
    "total_rec_late_fee",
    "out_prncp",
    "out_prncp_inv",
    "recoveries",
    "collection_recovery_fee",
    "last_pymnt_amnt",
    "next_pymnt_d",
    "last_fico_range_high",
    "last_fico_range_low",
    "pymnt_plan",
    "payment_plan_start_date",
    "deferral_term",
    "orig_projected_additional_accrued_interest",
    "debt_settlement_flag",
    "debt_settlement_flag_date",
]

#: Every ``hardship_*`` and ``settlement_*`` field is filled only after
#: origination. Most are already removed by :func:`rm_nas`, but the prefix
#: deny-list keeps the feature set correct regardless of the NaN threshold or
#: the order of the cleaning steps.
POST_OUTCOME_PREFIXES = ("hardship_", "settlement_")


def load_raw_data(path: str | Path, nrows: int | None = None) -> pd.DataFrame:
    """Load the LendingClub raw CSV.

    :param path: Path to ``accepted_2007_to_2018Q4.csv``.
    :param nrows: Optional row limit, useful for a quick run on a sample.
    :return: The raw data as a DataFrame.
    """
    return pd.read_csv(path, nrows=nrows, low_memory=False)


def add_issue_year(df: pd.DataFrame) -> pd.DataFrame:
    """Parse ``issue_d`` and add the issue year as a separate column.

    :param df: Raw data containing the ``issue_d`` column.
    :return: A copy with ``issue_d`` as datetime and a new ``issue_year``.
    """
    df = df.copy()
    df["issue_d"] = pd.to_datetime(df["issue_d"], format="%b-%Y")
    df["issue_year"] = df["issue_d"].dt.year
    return df


def filter_issue_years(
    df: pd.DataFrame, start_year: int = 2015, end_year: int = 2018
) -> pd.DataFrame:
    """Keep only loans issued within the given year range (inclusive).

    :param df: Data containing the ``issue_year`` column.
    :param start_year: First year to keep.
    :param end_year: Last year to keep.
    :return: The filtered data.
    """
    in_range = df["issue_year"].between(start_year, end_year)
    return df[in_range].copy()


def create_target(df: pd.DataFrame) -> pd.DataFrame:
    """Restrict the data to completed loans and add the binary target.

    ``target`` is 1 for ``Charged Off`` and 0 for ``Fully Paid``.

    :param df: Data containing the ``loan_status`` column.
    :return: The filtered data with the additional ``target`` column.
    """
    df = df[df["loan_status"].isin(COMPLETED_STATUSES)].copy()
    df["target"] = (df["loan_status"] == "Charged Off").astype(int)
    return df


def rm_nas(df: pd.DataFrame, threshold: float = 0.4) -> pd.DataFrame:
    """Drop columns whose share of missing values exceeds ``threshold``.

    :param df: Data to clean.
    :param threshold: Maximum tolerated share of missing values per column.
    :return: The data without the sparsely filled columns.
    """
    per = df.isnull().mean()
    drop_cols = per[per > threshold].index
    return df.drop(columns=drop_cols)


def drop_leakage_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Drop irrelevant columns and every column known only after the outcome.

    :param df: Data to clean.
    :return: The data reduced to features available at origination.
    """
    prefixed = [c for c in df.columns if c.startswith(POST_OUTCOME_PREFIXES)]
    return df.drop(
        columns=IRRELEVANT_COLS + POST_OUTCOME_COLS + prefixed, errors="ignore"
    )
