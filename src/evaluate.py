"""Evaluation metrics for the probability-of-default model."""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import ks_2samp
from sklearn.base import ClassifierMixin
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    precision_recall_fscore_support,
    roc_auc_score,
)

#: Readable class names for the classification report.
TARGET_NAMES = ["Fully Paid (0)", "Charged Off (1)"]


def evaluate_model(
    model: ClassifierMixin, x_test: pd.DataFrame, y_test: pd.Series
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


def charged_off_metrics(
    y_true: pd.Series | np.ndarray, y_proba: np.ndarray, threshold: float = 0.5
) -> dict[str, float]:
    """Precision, recall, F1 of the default class and accuracy at a threshold.

    At ``threshold=0.5`` these are the figures of the stored classification
    report, as numbers instead of text.

    :param y_true: True binary labels (1 = Charged Off).
    :param y_proba: Predicted default probabilities.
    :param threshold: Scores above it are flagged as default (a tie at 0.5 goes to the
        repaid class, like ``predict``).
    :return: Dict with ``precision``, ``recall``, ``f1`` and ``accuracy``.
    """
    y_pred = np.asarray(y_proba) > threshold
    precision, recall, f1, _ = precision_recall_fscore_support(
        y_true, y_pred, labels=[1], zero_division=0
    )
    return {
        "precision": precision[0],
        "recall": recall[0],
        "f1": f1[0],
        "accuracy": accuracy_score(y_true, y_pred),
    }
