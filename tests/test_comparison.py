"""Tests of the helpers behind the forest vs. scorecard page."""

import pandas as pd

from src.comparison import better_model, default_min_iv, dropped_features, iv_overview


def _iv_table() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "name": ["a", "b", "c", "d"],
            "dtype": ["numerical"] * 4,
            "n_bins": [3, 5, 2, 4],
            "iv": [0.01, 0.30, 0.05, 0.015],
            "selected": [False, True, True, False],
        }
    )


def test_iv_overview_sorts_descending_and_keeps_four_columns():
    overview = iv_overview(_iv_table())
    assert overview["name"].tolist() == ["b", "c", "d", "a"]
    assert list(overview.columns) == ["name", "n_bins", "iv", "selected"]
    assert overview.index.tolist() == [0, 1, 2, 3]


def test_dropped_features_are_the_unselected_ones_highest_iv_first():
    assert dropped_features(_iv_table()) == ["d", "a"]


def test_default_min_iv_is_the_threshold_of_the_notebook():
    assert default_min_iv() == 0.02


def test_unselected_features_are_those_below_the_threshold_on_the_bundle(bundle):
    overview = iv_overview(bundle["iv_table"])
    below = overview["iv"] < default_min_iv()
    assert (~overview["selected"]).tolist() == below.tolist()


def test_better_model_follows_the_auc_and_gives_ties_to_the_scorecard():
    def metrics(rf, scorecard):
        return {"rf": {"roc_auc": rf}, "scorecard": {"roc_auc": scorecard}}

    assert better_model(metrics(0.72, 0.70)) == "rf"
    assert better_model(metrics(0.70, 0.72)) == "scorecard"
    assert better_model(metrics(0.70, 0.70)) == "scorecard"
