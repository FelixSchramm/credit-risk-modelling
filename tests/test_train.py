"""Tests for the scorecard pipeline in :mod:`src.train`."""

import numpy as np
import pandas as pd

from src.train import train_scorecard


def _scorecard_inputs(n: int = 3000) -> tuple[pd.DataFrame, pd.Series]:
    """Build a frame with one predictive feature and two uninformative ones.

    :param n: Number of rows to generate.
    :return: The feature frame and the target drawn from ``signal``.
    """
    rng = np.random.default_rng(0)
    signal = rng.normal(0, 1, n)
    x = pd.DataFrame(
        {
            "signal": signal,
            "noise": rng.normal(0, 1, n),
            "grade": rng.choice(["A", "B", "C"], n),
        }
    )
    y = pd.Series(rng.binomial(1, 1 / (1 + np.exp(-2 * signal))))
    return x, y


def test_train_scorecard_selects_on_information_value():
    """Only ``signal`` carries information, so the IV filter must keep just it.

    This pins the ``selection_criteria`` wiring rather than optbinning's
    binning: a ``max`` instead of a ``min`` there would invert the selection
    and silently train the regression on the uninformative features.
    """
    x, y = _scorecard_inputs()
    selected = train_scorecard(x, y, categorical_variables=["grade"])
    support = list(selected.named_steps["woe"].get_support(names=True))
    assert support == ["signal"]


def test_train_scorecard_returns_a_fitted_probability_model():
    """``evaluate_model`` scores the scorecard, so it has to predict like one."""
    x, y = _scorecard_inputs()
    y_pred_proba = train_scorecard(x, y, categorical_variables=["grade"]).predict_proba(
        x
    )
    assert y_pred_proba.shape == (len(x), 2)
    assert ((y_pred_proba >= 0) & (y_pred_proba <= 1)).all()
