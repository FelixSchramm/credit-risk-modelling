"""Tests for the metric computation in :mod:`src.evaluate`."""

import numpy as np
import pandas as pd

from src.evaluate import evaluate_model


class FixedProbaModel:
    """Stand-in for a fitted classifier with known predicted probabilities.

    ``evaluate_model`` only calls ``predict_proba`` and ``predict``, so the
    metrics can be checked against hand-computed values instead of against
    whatever a model trained on synthetic data happens to produce.
    """

    def __init__(self, y_pred_proba: list[float]) -> None:
        """:param y_pred_proba: Default probability per test row."""
        self.y_pred_proba = np.asarray(y_pred_proba)

    def predict_proba(self, x_test: pd.DataFrame) -> np.ndarray:
        """:param x_test: Ignored; the probabilities are fixed at construction.
        :return: The two-column probability matrix sklearn models return.
        """
        return np.column_stack([1 - self.y_pred_proba, self.y_pred_proba])

    def predict(self, x_test: pd.DataFrame) -> np.ndarray:
        """:param x_test: Ignored; see :meth:`predict_proba`.
        :return: The 0.5-threshold labels sklearn classifiers predict.
        """
        return (self.y_pred_proba >= 0.5).astype(int)


def _evaluate(y_true: list[int], y_pred_proba: list[float]) -> dict[str, object]:
    """Run :func:`evaluate_model` on hand-picked scores.

    :param y_true: True labels.
    :param y_pred_proba: Predicted default probability per row.
    :return: The metrics dict.
    """
    x_test = pd.DataFrame({"feature": range(len(y_true))})
    return evaluate_model(FixedProbaModel(y_pred_proba), x_test, pd.Series(y_true))


def test_perfect_separation_scores_the_maximum():
    """Every defaulted loan scored above every repaid one: AUC, Gini and KS 1."""
    result = _evaluate([0, 0, 0, 1, 1, 1], [0.1, 0.2, 0.3, 0.7, 0.8, 0.9])
    assert result["roc_auc"] == 1.0
    assert result["gini"] == 1.0
    assert result["ks"] == 1.0


def test_overlapping_scores_match_the_hand_computed_values():
    """Three of the four default/non-default pairs are ranked correctly.

    Scores are 0.1 and 0.6 for the repaid loans, 0.4 and 0.9 for the defaulted
    ones, so AUC is 3/4 and Gini 2 * 0.75 - 1. The score distributions differ
    most below 0.4 and above 0.6, in both cases by one of two observations, so
    KS is 0.5.
    """
    result = _evaluate([0, 0, 1, 1], [0.1, 0.6, 0.4, 0.9])
    assert result["roc_auc"] == 0.75
    assert result["gini"] == 0.5
    assert result["ks"] == 0.5


def test_predicted_probabilities_are_handed_out_unchanged():
    """The notebook plots and explains these, so they must be the raw scores."""
    result = _evaluate([0, 1], [0.25, 0.75])
    assert list(result["y_pred_proba"]) == [0.25, 0.75]


def test_metrics_are_positional_for_a_non_zero_based_index():
    """``y_test`` arrives from ``train_test_split`` with the original index.

    The KS split masks a numpy array with a pandas Series, which uses the
    values rather than the labels; this test fails if that ever changes.
    """
    x_test = pd.DataFrame({"feature": range(4)})
    y_test = pd.Series([0, 0, 1, 1], index=[7, 42, 13, 99])
    result = evaluate_model(FixedProbaModel([0.1, 0.6, 0.4, 0.9]), x_test, y_test)
    assert result["roc_auc"] == 0.75
    assert result["ks"] == 0.5
