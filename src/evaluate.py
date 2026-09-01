"""Evaluation metrics for the probability-of-default model."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.base import ClassifierMixin
from sklearn.metrics import classification_report, roc_auc_score

#: Readable class names for the classification report.
TARGET_NAMES = ["Fully Paid (0)", "Charged Off (1)"]


def evaluate_model(
    model: ClassifierMixin, x_test: np.ndarray, y_test: pd.Series
) -> dict[str, object]:
    """Score a fitted model on the test set.

    :param model: Fitted classifier with ``predict`` and ``predict_proba``.
    :param x_test: Scaled test features.
    :param y_test: True test labels.
    :return: Dict with the ``roc_auc`` value and the ``report`` text.
    """
    y_pred_proba = model.predict_proba(x_test)[:, 1]
    y_pred = model.predict(x_test)
    return {
        "roc_auc": roc_auc_score(y_test, y_pred_proba),
        "report": classification_report(y_test, y_pred, target_names=TARGET_NAMES),
    }
