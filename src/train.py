"""Train/test split, model training and model persistence."""

from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


def split_and_scale(
    x: pd.DataFrame,
    y: pd.Series,
    test_size: float = 0.3,
    random_state: int = 42,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series, StandardScaler]:
    """Split the data stratified by the target and standardize the features.

    The scaler is fitted on the training set only, so no information from the
    test set enters the training data.

    ``set_output(transform="pandas")`` keeps the scaled features as DataFrames.
    Plain ``StandardScaler`` output would be a numpy array, which drops the
    column names and leaves feature importances and SHAP plots labelled with
    positional indices instead of feature names.

    :param x: Feature matrix.
    :param y: Binary target.
    :param test_size: Share of the data used for the test set.
    :param random_state: Seed for the reproducible split.
    :return: ``x_train``, ``x_test``, ``y_train``, ``y_test`` and the scaler.
    """
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=test_size, random_state=random_state, stratify=y
    )
    scaler = StandardScaler().set_output(transform="pandas")
    return (
        scaler.fit_transform(x_train),
        scaler.transform(x_test),
        y_train,
        y_test,
        scaler,
    )


def train_random_forest(
    x_train: pd.DataFrame, y_train: pd.Series, random_state: int = 42
) -> RandomForestClassifier:
    """Train a random forest on the scaled training data.

    ``class_weight="balanced"`` compensates for the small share of defaults.

    :param x_train: Scaled training features.
    :param y_train: Training target.
    :param random_state: Seed for the reproducible forest.
    :return: The fitted classifier.
    """
    model = RandomForestClassifier(
        n_estimators=100,
        random_state=random_state,
        class_weight="balanced",
        n_jobs=-1,
    )
    model.fit(x_train, y_train)
    return model


def save_model(model: RandomForestClassifier, path: str | Path) -> None:
    """Persist a fitted model to disk.

    :param model: The fitted classifier.
    :param path: Target file, e.g. ``04_models/random_forest.joblib``.
    :return: None.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, path)
