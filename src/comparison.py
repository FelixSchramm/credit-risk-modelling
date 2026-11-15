"""Helpers of the forest vs. scorecard page (no Streamlit import).

The page text must follow the numbers, so the one decision that depends on
them (which model separates better) and the reading of the IV table live here
where they can be tested.
"""

from __future__ import annotations

import inspect

import pandas as pd

from src.train import train_scorecard


def default_min_iv() -> float:
    """Return the IV threshold the scorecard was trained with.

    The bundle does not store ``min_iv``, and ``build_bundle`` uses the default
    of :func:`src.train.train_scorecard`; reading the default keeps one source.

    :return: The Information Value a feature needs to be kept.
    """
    return inspect.signature(train_scorecard).parameters["min_iv"].default


def iv_overview(iv_table: pd.DataFrame) -> pd.DataFrame:
    """Sort the IV table by Information Value, highest first.

    :param iv_table: ``bundle["iv_table"]`` with the columns ``name``,
        ``n_bins``, ``iv`` and ``selected``.
    :return: Those four columns, sorted, with a fresh index.
    """
    columns = ["name", "n_bins", "iv", "selected"]
    return iv_table[columns].sort_values("iv", ascending=False, ignore_index=True)


def dropped_features(iv_table: pd.DataFrame) -> list[str]:
    """List the features that fell below the ``min_iv`` threshold.

    :param iv_table: ``bundle["iv_table"]``.
    :return: Feature names, highest IV first.
    """
    overview = iv_overview(iv_table)
    return overview.loc[~overview["selected"], "name"].tolist()


def better_model(metrics: dict[str, dict[str, float]]) -> str:
    """Name the model with the higher ROC AUC on the test loans.

    A tie goes to the scorecard: a scorecard that matches the forest is the
    better model, because it is the simpler one (notebook section 7).

    :param metrics: ``bundle["metrics"]``.
    :return: ``"rf"`` or ``"scorecard"``.
    """
    if metrics["rf"]["roc_auc"] > metrics["scorecard"]["roc_auc"]:
        return "rf"
    return "scorecard"
