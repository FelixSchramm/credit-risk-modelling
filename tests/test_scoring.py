"""Tests for :mod:`src.scoring` against the synthetic bundle of ``conftest.py``."""

import numpy as np
import pandas as pd
import pytest

from src.evaluate import charged_off_metrics
from src.scoring import (
    band_of,
    build_feature_vector,
    build_scorecard_row,
    cutoff_table,
    explain_forest,
    explain_scorecard,
    forest_explainer,
    percentile_of,
    score,
    top_contributions,
)


def _purpose_dummies(bundle: dict) -> list[str]:
    return [n for n in bundle["feature_names"] if n.startswith("purpose_")]


COUPLED = ["funded_amnt", "funded_amnt_inv", "installment", "fico_range_high"]


@pytest.fixture
def coupled_bundle(bundle) -> dict:
    """The synthetic bundle with the four coupled columns, as in the real one."""
    zeros = dict.fromkeys(COUPLED, 0.0)
    return {
        **bundle,
        "feature_names": bundle["feature_names"] + COUPLED,
        "feature_defaults": {**bundle["feature_defaults"], **zeros},
        "scorecard_columns": bundle["scorecard_columns"] + COUPLED,
        "scorecard_defaults": {**bundle["scorecard_defaults"], **zeros},
    }


def _coupled_rows(user_input: dict, bundle: dict) -> list[pd.Series]:
    """Forest vector and scorecard row of one application."""
    return [
        build_feature_vector(user_input, bundle).iloc[0],
        build_scorecard_row(user_input, bundle).iloc[0],
    ]


def test_vector_has_exactly_the_feature_names_in_order(bundle):
    vector = build_feature_vector({"loan_amnt": 5000}, bundle)
    assert list(vector.columns) == bundle["feature_names"]
    assert len(vector) == 1


def test_column_order_does_not_depend_on_the_order_of_the_defaults(bundle):
    shuffled = {
        "feature_defaults": dict(reversed(bundle["feature_defaults"].items())),
        "scorecard_defaults": dict(reversed(bundle["scorecard_defaults"].items())),
    }
    changed = {**bundle, **shuffled}
    vector = build_feature_vector({"purpose": "house"}, changed)
    row = build_scorecard_row({"purpose": "house"}, changed)
    assert list(vector.columns) == bundle["feature_names"]
    assert list(row.columns) == bundle["scorecard_columns"]


def test_unspecified_fields_keep_the_defaults(bundle):
    vector = build_feature_vector({"loan_amnt": 5000}, bundle)
    row = vector.iloc[0]
    for name, default in bundle["feature_defaults"].items():
        if name != "loan_amnt":
            assert row[name] == default
    assert row["loan_amnt"] == 5000
    assert "issue_year" in vector.columns


def test_text_inputs_are_converted_like_in_training(bundle):
    row = build_feature_vector(
        {"term": " 60 months", "emp_length": "< 1 year"}, bundle
    ).iloc[0]
    assert row["term"] == 60
    assert row["emp_length"] == 0


def test_categorical_input_sets_exactly_one_dummy(bundle):
    dummies = _purpose_dummies(bundle)
    assert len(dummies) == 2  # three categories, drop_first removed one
    for category in ("car", "house", "other"):
        row = build_feature_vector({"purpose": category}, bundle).iloc[0]
        active = [n for n in dummies if row[n]]
        if f"purpose_{category}" in dummies:
            assert active == [f"purpose_{category}"]
        else:
            assert active == []  # reference category: no column of its own


def test_categorical_input_clears_a_dummy_that_is_set_by_default(bundle):
    # In the real portfolio the mode of a dummy can be 1; the input must win.
    dummies = _purpose_dummies(bundle)
    defaults = {**bundle["feature_defaults"], **{n: True for n in dummies}}
    row = build_feature_vector(
        {"purpose": "car"}, {**bundle, "feature_defaults": defaults}
    ).iloc[0]
    assert not row[dummies].any()  # "car" is the reference category


def test_unknown_field_or_category_raises(bundle):
    for build in (build_feature_vector, build_scorecard_row):
        with pytest.raises(ValueError, match="Unknown input fields"):
            build({"loan_amount": 5000}, bundle)
        with pytest.raises(ValueError, match="Unknown category"):
            build({"purpose": "yacht"}, bundle)


def test_scorecard_row_keeps_raw_categories_and_column_order(bundle):
    row = build_scorecard_row({"purpose": "car", "term": " 60 months"}, bundle)
    assert list(row.columns) == bundle["scorecard_columns"]
    assert row.iloc[0]["purpose"] == "car"
    assert row.iloc[0]["term"] == " 60 months"
    assert row.iloc[0]["annual_inc"] == bundle["scorecard_defaults"]["annual_inc"]


def test_funded_amounts_follow_the_loan_amount(coupled_bundle):
    for row in _coupled_rows({"loan_amnt": 7500}, coupled_bundle):
        assert row["funded_amnt"] == row["funded_amnt_inv"] == 7500


def test_fico_range_high_is_low_plus_four(coupled_bundle):
    for row in _coupled_rows({"fico_range_low": 720}, coupled_bundle):
        assert row["fico_range_high"] == 724


def test_installment_is_the_annuity_for_both_terms(coupled_bundle):
    # 12,000 at 12.74 % over 36 months costs 402.83 a month (the real bundle's
    # median installment 373.77 is a median of different loans, not this one);
    # the 60-month loan is checked by paying it off: the balance ends at zero.
    user_input = {"loan_amnt": 12000, "int_rate": 12.74, "term": " 36 months"}
    for row in _coupled_rows(user_input, coupled_bundle):
        assert row["installment"] == pytest.approx(402.83, abs=0.005)
    user_input["term"] = " 60 months"
    for row in _coupled_rows(user_input, coupled_bundle):
        monthly_rate = 0.1274 / 12
        balance = 12000.0
        for _ in range(60):
            balance = balance * (1 + monthly_rate) - row["installment"]
        assert balance == pytest.approx(0, abs=1e-6)


def test_coupled_columns_use_the_defaults_for_missing_inputs(coupled_bundle):
    defaults = coupled_bundle["scorecard_defaults"]
    for row in _coupled_rows({"purpose": "car"}, coupled_bundle):
        assert row["funded_amnt"] == defaults["loan_amnt"]
        assert row["fico_range_high"] == defaults["fico_range_low"] + 4


def test_coupled_columns_are_left_alone_if_the_bundle_has_none(bundle):
    assert "funded_amnt" not in build_feature_vector({"loan_amnt": 5000}, bundle)


def test_score_returns_probabilities_for_both_models(bundle):
    result = score({"int_rate": 12.0, "purpose": "house"}, bundle)
    assert set(result) == {"rf", "scorecard"}
    assert all(0 <= p <= 1 for p in result.values())


def test_higher_interest_rate_does_not_lower_the_scorecard_pd(bundle):
    low = score({"int_rate": 6.0}, bundle)["scorecard"]
    high = score({"int_rate": 25.0}, bundle)["scorecard"]
    assert high > low


def test_higher_interest_rate_does_not_lower_the_forest_pd(bundle):
    # Without the scaler the forest compares raw values with scaled thresholds
    # and returns the same score for every rate.
    low = score({"int_rate": 6.0}, bundle)["rf"]
    high = score({"int_rate": 25.0}, bundle)["rf"]
    assert high > low


def test_percentile_of_counts_scores_at_or_below():
    reference = np.array([0.1, 0.2, 0.3, 0.4])
    assert percentile_of(0.3, reference) == 75.0
    assert percentile_of(0.0, reference) == 0.0
    assert percentile_of(0.9, reference) == 100.0


def test_band_of_covers_bands_gaps_and_extremes():
    bands = pd.DataFrame({"band": [1, 2, 3], "score_max": [0.1, 0.3, 0.6]})
    assert band_of(0.05, bands) == 1
    assert band_of(0.1, bands) == 1
    assert band_of(0.2, bands) == 2  # between score_max of band 1 and 2
    assert band_of(0.9, bands) == 3  # above the last band


HIGH_RISK = {"int_rate": 22.0, "term": " 60 months", "dti": 30.0}


@pytest.fixture(scope="module")
def explainer(bundle):
    return forest_explainer(bundle)


@pytest.mark.parametrize("user_input", [{}, HIGH_RISK])
def test_forest_shap_values_add_up_to_the_uncalibrated_probability(
    user_input, bundle, explainer
):
    table, base = explain_forest(user_input, bundle, explainer)
    forest = bundle["rf"].calibrated_classifiers_[0].estimator.estimator
    x = bundle["scaler"].transform(build_feature_vector(user_input, bundle))
    assert base + table["contribution"].sum() == pytest.approx(
        forest.predict_proba(x)[0, 1]
    )


def test_forest_explanation_lists_every_feature_with_its_unscaled_value(
    bundle, explainer
):
    table, _ = explain_forest(HIGH_RISK, bundle, explainer)
    assert list(table["feature"]) == bundle["feature_names"]
    assert table.set_index("feature").loc["int_rate", "value"] == 22.0


def test_forest_shap_blames_the_interest_rate_for_a_high_rate(bundle, explainer):
    low, _ = explain_forest({"int_rate": 8.0}, bundle, explainer)
    high, _ = explain_forest({"int_rate": 22.0}, bundle, explainer)
    contribution = lambda table: table.set_index("feature").loc["int_rate"][
        "contribution"
    ]
    assert contribution(high) > 0 > contribution(low)


@pytest.mark.parametrize("user_input", [{}, HIGH_RISK])
def test_scorecard_contributions_add_up_to_the_log_odds(user_input, bundle):
    table, intercept = explain_scorecard(user_input, bundle)
    pipeline = bundle["scorecard"].calibrated_classifiers_[0].estimator.estimator
    row = build_scorecard_row(user_input, bundle)
    assert intercept + table["contribution"].sum() == pytest.approx(
        pipeline.decision_function(row)[0]
    )


def test_scorecard_contribution_is_coefficient_times_woe(bundle):
    table, _ = explain_scorecard(HIGH_RISK, bundle)
    logit = bundle["scorecard"].calibrated_classifiers_[0].estimator.estimator[-1]
    assert np.allclose(table["contribution"], logit.coef_[0] * table["woe"])


def test_scorecard_explanation_keeps_raw_values_of_kept_features(bundle):
    table, _ = explain_scorecard(HIGH_RISK, bundle)
    kept = bundle["scorecard"].calibrated_classifiers_[0].estimator.estimator[0]
    assert list(table["feature"]) == list(kept.get_support(names=True))
    assert table.set_index("feature").loc["int_rate", "value"] == 22.0


def test_scorecard_high_rate_raises_the_risk_contribution(bundle):
    low, _ = explain_scorecard({"int_rate": 8.0}, bundle)
    high, _ = explain_scorecard({"int_rate": 22.0}, bundle)
    contribution = lambda table: table.set_index("feature").loc["int_rate"][
        "contribution"
    ]
    assert contribution(high) > 0 > contribution(low)


def test_top_contributions_keeps_the_largest_and_sums_the_rest():
    table = pd.DataFrame(
        {"feature": list("abcde"), "contribution": [0.1, -0.5, 0.2, 0.05, -0.3]}
    )
    top = top_contributions(table, 2, "rest")
    assert list(top["feature"]) == ["b", "e", "rest"]
    assert top["contribution"].iloc[-1] == pytest.approx(0.1 + 0.2 + 0.05)
    assert top["contribution"].sum() == pytest.approx(table["contribution"].sum())


def test_top_contributions_without_remainder_adds_no_row():
    table = pd.DataFrame({"feature": ["a", "b"], "contribution": [0.1, -0.2]})
    top = top_contributions(table, 5, "rest")
    assert list(top["feature"]) == ["b", "a"]


def _toy_cutoff_table(thresholds=(0.0, 0.25, 0.5, 1.0)):
    """Eight loans, four defaults, ties at 0.5."""
    proba = np.array([0.1, 0.2, 0.2, 0.5, 0.5, 0.6, 0.8, 0.9])
    y = np.array([0, 0, 1, 0, 1, 1, 1, 0])
    return y, proba, cutoff_table(y, proba, np.array(thresholds), 0.5, 0.1, 1000)


def test_cutoff_table_counts_match_a_direct_count():
    y, proba, table = _toy_cutoff_table()
    for _, row in table.iterrows():
        reject = proba > row["threshold"]
        assert row["rejected"] == reject.sum()
        assert row["accepted"] == (~reject).sum()
        assert row["caught"] == (y[reject] == 1).sum()
        assert row["missed"] == (y[~reject] == 1).sum()
        assert row["rejected_good"] == (y[reject] == 0).sum()


def test_cutoff_table_conserves_loans_and_defaults():
    y, _, table = _toy_cutoff_table()
    assert (table["accepted"] + table["rejected"] == len(y)).all()
    assert (table["caught"] + table["missed"] == y.sum()).all()
    assert (table["caught"] + table["rejected_good"] == table["rejected"]).all()


def test_cutoff_table_ties_go_to_the_accepted_part():
    _, _, table = _toy_cutoff_table()
    at_half = table.set_index("threshold").loc[0.5]
    assert at_half["rejected"] == 3
    assert at_half["accepted"] == 5


def test_cutoff_table_rates_and_edges():
    y, _, table = _toy_cutoff_table()
    rows = table.set_index("threshold")
    assert rows.loc[0.0, "approval_rate"] == 0.0
    assert np.isnan(rows.loc[0.0, "default_rate_accepted"])
    assert rows.loc[0.0, "recall"] == 1.0
    assert rows.loc[1.0, "approval_rate"] == 1.0
    assert rows.loc[1.0, "default_rate_accepted"] == y.mean()
    assert rows.loc[1.0, "precision"] == 0.0
    assert rows.loc[1.0, "recall"] == 0.0
    assert rows.loc[0.25, "default_rate_accepted"] == pytest.approx(1 / 3)


def test_cutoff_table_net_result_by_hand():
    _, _, table = _toy_cutoff_table()
    rows = table.set_index("threshold")
    # Accept all: 4 good loans earn 100 each, 4 defaults lose 500 each.
    assert rows.loc[1.0, "net_result"] == 4 * 100 - 4 * 500
    # Reject all: nothing earned, nothing lost.
    assert rows.loc[0.0, "net_result"] == 0
    # Threshold 0.5 accepts 0.1, 0.2, 0.2, 0.5, 0.5: 3 good loans, 2 defaults.
    assert rows.loc[0.5, "net_result"] == 3 * 100 - 2 * 500


def test_cutoff_table_matches_charged_off_metrics(bundle):
    y, proba = bundle["y_test"], bundle["proba_rf"]
    table = cutoff_table(y, proba, np.array([0.1, 0.3, 0.5]), 0.6, 0.1, 10_000)
    for _, row in table.iterrows():
        expected = charged_off_metrics(y, proba, row["threshold"])
        assert row["precision"] == pytest.approx(expected["precision"])
        assert row["recall"] == pytest.approx(expected["recall"])
        assert row["accepted"] + row["rejected"] == len(y)
