"""Evaluation metrics for the probability-of-default model."""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import ks_2samp
from sklearn.base import ClassifierMixin
from sklearn.metrics import classification_report, roc_auc_score

#: Readable class names for the classification report.
TARGET_NAMES = ["Fully Paid (0)", "Charged Off (1)"]


def evaluate_model(
    model: ClassifierMixin, x_test: np.ndarray, y_test: pd.Series
) -> dict[str, object]:
    """Score a fitted model on the test set.

    Reports the discriminatory power in the two forms a bank expects next to
    each other: ROC AUC with its linear rescaling to the Gini coefficient
    (``2 * AUC - 1``), and the Kolmogorov-Smirnov statistic, i.e. the largest
    gap between the score distributions of defaulted and repaid loans.

    :param model: Fitted classifier with ``predict`` and ``predict_proba``.
    :param x_test: Scaled test features.
    :param y_test: True test labels.
    :return: Dict with ``roc_auc``, ``gini``, ``ks``, the ``report`` text and
        the predicted default probabilities ``y_pred_proba``.
    """
    y_pred_proba = model.predict_proba(x_test)[:, 1]
    y_pred = model.predict(x_test)
    roc_auc = roc_auc_score(y_test, y_pred_proba)
    return {
        "roc_auc": roc_auc,
        "gini": 2 * roc_auc - 1,
        "ks": ks_2samp(y_pred_proba[y_test == 1], y_pred_proba[y_test == 0]).statistic,
        "report": classification_report(y_test, y_pred, target_names=TARGET_NAMES),
        "y_pred_proba": y_pred_proba,
    }
