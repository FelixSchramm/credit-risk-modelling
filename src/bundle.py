"""Artefact bundle: everything the dashboard needs to score and to show the
model quality, written to a single joblib file.

The bundle only collects the results of :mod:`src.features`,
:mod:`src.train` and :mod:`src.evaluate`. The stored test-set scores let the
app draw ROC, calibration and cut-off views without the raw dataset.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.base import ClassifierMixin
from sklearn.calibration import CalibratedClassifierCV
from sklearn.frozen import FrozenEstimator
from sklearn.model_selection import train_test_split

from src.evaluate import evaluate_model
from src.features import engineer_features
from src.train import split_and_scale, train_random_forest, train_scorecard

#: Version of the bundle contract; bump it if the keys change.
BUNDLE_VERSION = 1


def calibrate(
    model: ClassifierMixin, x_calib: pd.DataFrame, y_calib: pd.Series
) -> CalibratedClassifierCV:
    """Calibrate a fitted classifier with isotonic regression.

    ``class_weight="balanced"`` inflates the raw probabilities, so they are not
    default probabilities. The calibration data must be disjoint from the
    training data, otherwise the calibration is biased.

    :param model: Fitted classifier, left unchanged inside the wrapper.
    :param x_calib: Features of the separate calibration split.
    :param y_calib: Target of the calibration split.
    :return: The fitted calibrated classifier.
    """
    calibrated = CalibratedClassifierCV(FrozenEstimator(model), method="isotonic")
    return calibrated.fit(x_calib, y_calib)


def score_bands(
    y_true: pd.Series | np.ndarray, y_proba: np.ndarray, n_bands: int = 10
) -> pd.DataFrame:
    """Split the scores into equally sized bands (deciles by default).

    Ranks are used instead of score quantiles so that tied scores and fewer
    rows than bands still give valid bands.

    :param y_true: True binary labels.
    :param y_proba: Predicted default probabilities.
    :param n_bands: Number of bands; reduced to the row count if larger.
    :return: One row per band, lowest scores first, with ``n``, ``score_min``,
        ``score_max``, ``mean_score`` and the observed ``default_rate``.
    """
    scores = pd.DataFrame(
        {"y": np.asarray(y_true), "score": np.asarray(y_proba, dtype=float)}
    )
    n_bands = min(n_bands, len(scores))
    scores["band"] = (
        pd.qcut(scores["score"].rank(method="first"), n_bands, labels=False) + 1
    )
    bands = scores.groupby("band").agg(
        n=("y", "size"),
        score_min=("score", "min"),
        score_max=("score", "max"),
        mean_score=("score", "mean"),
        default_rate=("y", "mean"),
    )
    return bands.reset_index()


def _defaults(df: pd.DataFrame) -> dict[str, object]:
    """Median for numeric columns, mode for everything else (dummies included).

    :param df: Frame to summarize.
    :return: Default value per column.
    """
    return {
        col: (
            df[col].median()
            if pd.api.types.is_numeric_dtype(df[col])
            and not pd.api.types.is_bool_dtype(df[col])
            else df[col].mode().iloc[0]
        )
        for col in df.columns
    }


def input_spec(df_unencoded: pd.DataFrame, fields: list[str]) -> dict[str, dict]:
    """Describe the user-facing input fields from the portfolio itself.

    The 1 % / 99 % quantiles as limits keep outliers out of the app sliders.

    :param df_unencoded: Cleaned frame before one-hot encoding.
    :param fields: Columns the user may enter.
    :return: Per field ``{"type": "numeric", "min", "max", "median"}`` or
        ``{"type": "categorical", "categories", "default"}``.
    """
    spec: dict[str, dict] = {}
    for field in fields:
        column = df_unencoded[field]
        if pd.api.types.is_numeric_dtype(column):
            low, high = column.quantile([0.01, 0.99])
            spec[field] = {
                "type": "numeric",
                "min": float(low),
                "max": float(high),
                "median": float(column.median()),
            }
        else:
            spec[field] = {
                "type": "categorical",
                "categories": sorted(column.dropna().unique()),
                "default": column.mode().iloc[0],
            }
    return spec


def _as_float32(values: np.ndarray) -> np.ndarray:
    """Shrink score arrays; float32 is precise enough for plots and bands.

    :param values: Score array.
    :return: The same values as float32.
    """
    return np.asarray(values, dtype=np.float32)


def build_bundle(
    df_unencoded: pd.DataFrame, fields: list[str], random_state: int = 42
) -> dict[str, object]:
    """Train, calibrate and evaluate both models and assemble the bundle.

    The test set is split off first (70/30, as in the notebook); 20 % of the
    training part is held back as calibration split. Forest and scorecard see
    the same loans in every split.

    ``bundle["rf"]`` is the calibrated wrapper. TreeSHAP needs the inner
    forest: ``bundle["rf"].calibrated_classifiers_[0].estimator.estimator``.
    ``metrics`` refer to the calibrated scores; at the 0.5 threshold their
    ``report`` shows a low recall because hardly any calibrated score exceeds
    0.5. The ``proba_*_raw`` arrays hold the uncalibrated test scores.
    ``n_train`` counts the whole training part including the calibration split.

    :param df_unencoded: Cleaned frame with the ``target`` column, ``term`` and
        ``emp_length`` still as text, all NaN rows dropped.
    :param fields: Columns the user may enter in the app (for ``input_spec``).
    :param random_state: Seed for splits and forest.
    :return: The bundle dict (see the issue #28 contract).
    """
    x_woe = df_unencoded.drop(columns="target")
    x = engineer_features(df_unencoded).drop(columns="target")
    y = df_unencoded["target"]

    x_train, x_test, y_train, y_test, scaler = split_and_scale(
        x, y, random_state=random_state
    )
    x_fit, x_calib, y_fit, y_calib = train_test_split(
        x_train,
        y_train,
        test_size=0.2,
        random_state=random_state,
        stratify=y_train,
    )
    # The scorecard works on the unencoded frame; the shared index selects the
    # same loans for both models.
    categorical = list(x_woe.select_dtypes(include=["str", "object"]).columns)
    scorecard_raw = train_scorecard(x_woe.loc[x_fit.index], y_fit, categorical)
    rf_raw = train_random_forest(x_fit, y_fit, random_state=random_state)

    rf = calibrate(rf_raw, x_calib, y_calib)
    scorecard = calibrate(scorecard_raw, x_woe.loc[x_calib.index], y_calib)

    x_woe_test = x_woe.loc[x_test.index]
    scores = {
        "rf": evaluate_model(rf, x_test, y_test),
        "scorecard": evaluate_model(scorecard, x_woe_test, y_test),
    }
    metrics = {
        name: {k: v for k, v in result.items() if k != "y_pred_proba"}
        for name, result in scores.items()
    }
    proba_rf = scores["rf"]["y_pred_proba"]
    proba_scorecard = scores["scorecard"]["y_pred_proba"]
    iv_table = scorecard_raw.named_steps["woe"].summary()
    iv_table = iv_table[["name", "dtype", "n_bins", "iv", "selected"]]
    return {
        "version": BUNDLE_VERSION,
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "n_train": len(x_train),
        "n_test": len(x_test),
        "base_rate": float(y.mean()),
        "feature_names": list(x.columns),
        "feature_defaults": _defaults(x),
        "scaler": scaler,
        "rf": rf,
        "scorecard": scorecard,
        "scorecard_columns": list(x_woe.columns),
        "scorecard_defaults": _defaults(x_woe),
        "input_spec": input_spec(df_unencoded, fields),
        "metrics": metrics,
        "y_test": y_test.to_numpy(dtype=np.int8),
        "proba_rf": _as_float32(proba_rf),
        "proba_scorecard": _as_float32(proba_scorecard),
        "proba_rf_raw": _as_float32(rf_raw.predict_proba(x_test)[:, 1]),
        "proba_scorecard_raw": _as_float32(
            scorecard_raw.predict_proba(x_woe_test)[:, 1]
        ),
        "bands_rf": score_bands(y_test, proba_rf),
        "bands_scorecard": score_bands(y_test, proba_scorecard),
        "iv_table": iv_table.sort_values("iv", ascending=False),
    }


def save_bundle(bundle: dict[str, object], path: str | Path) -> None:
    """Write the bundle compressed to disk and print the file size.

    :param bundle: Dict from :func:`build_bundle`.
    :param path: Target file, e.g. ``04_models/bundle.joblib``.
    :return: None.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(bundle, path, compress=3)
    print(f"Bundle written to {path} ({path.stat().st_size / 1e6:.1f} MB)")


def load_bundle(path: str | Path) -> dict[str, object]:
    """Load a bundle written by :func:`save_bundle`.

    :param path: Bundle file.
    :return: The bundle dict.
    """
    return joblib.load(path)
