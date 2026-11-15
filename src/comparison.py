"""Helpers of the forest vs. scorecard page (no Streamlit import).

The page text must follow the numbers, so the decision that depends on them
(which model separates better) and the threshold live here where they can be
tested.
"""

from __future__ import annotations

import inspect

from src.train import train_scorecard


def default_min_iv() -> float:
    """Return the IV threshold the scorecard was trained with.

    The bundle does not store ``min_iv``, and ``build_bundle`` uses the default
    of :func:`src.train.train_scorecard`; reading the default keeps one source.

    :return: The Information Value a feature needs to be kept.
    """
    return inspect.signature(train_scorecard).parameters["min_iv"].default


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
