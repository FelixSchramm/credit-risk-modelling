"""Tests of the helpers behind the forest vs. scorecard page."""

from src.comparison import better_model, default_min_iv


def test_default_min_iv_is_the_threshold_of_the_notebook():
    assert default_min_iv() == 0.02


def test_unselected_features_are_those_below_the_threshold_on_the_bundle(bundle):
    iv_table = bundle["iv_table"]
    below = iv_table["iv"] < default_min_iv()
    assert (~iv_table["selected"]).tolist() == below.tolist()


def test_better_model_follows_the_auc_and_gives_ties_to_the_scorecard():
    def metrics(rf, scorecard):
        return {"rf": {"roc_auc": rf}, "scorecard": {"roc_auc": scorecard}}

    assert better_model(metrics(0.72, 0.70)) == "rf"
    assert better_model(metrics(0.70, 0.72)) == "scorecard"
    assert better_model(metrics(0.70, 0.70)) == "scorecard"
