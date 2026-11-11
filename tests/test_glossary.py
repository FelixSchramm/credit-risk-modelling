"""Tests of the glossary entries, ``glossary_help`` and ``project_figures``."""

import re

import pytest

from src.glossary import GROUPS, glossary_entries, glossary_help, project_figures
from src.i18n import LANGUAGES

REQUIRED_KEYS = {
    "data": ["target", "data_leakage", "train_test_split", "out_of_time"],
    "models": [
        "random_forest",
        "logistic_regression",
        "scorecard",
        "binning",
        "woe",
        "iv",
        "class_weight",
    ],
    "quality": [
        "roc_curve",
        "auc",
        "gini",
        "ks",
        "confusion_matrix",
        "precision",
        "recall",
        "f1",
        "accuracy",
    ],
    "calibration": [
        "pd",
        "base_rate",
        "calibration",
        "reliability_diagram",
        "isotonic_regression",
    ],
    "explain": [
        "feature_importance",
        "shap",
        "shap_base_value",
        "beeswarm",
        "waterfall",
        "scorecard_points",
    ],
    "economics": [
        "score_band",
        "cutoff",
        "approval_rate",
        "expected_loss",
        "lgd",
        "ead",
    ],
    "regulatory": [
        "basel_irb",
        "ifrs9",
        "finma",
        "model_card",
        "model_validation",
    ],
}
PLACEHOLDER = re.compile(r"\{(\w+)\}")


@pytest.mark.parametrize("lang", LANGUAGES)
def test_every_entry_has_the_required_fields(lang):
    for entry in glossary_entries(lang):
        for field in ("term", "group", "what", "limit"):
            assert entry[field].strip(), (entry["key"], field)
        assert entry["group"] in GROUPS, entry["key"]
        assert len(entry["what"]) <= 400, entry["key"]


@pytest.mark.parametrize("lang", LANGUAGES)
def test_minimum_scope_is_present_in_its_group(lang):
    group_of = {e["key"]: e["group"] for e in glossary_entries(lang)}
    for group, keys in REQUIRED_KEYS.items():
        for key in keys:
            assert group_of.get(key) == group, key


def test_entries_follow_the_group_order():
    groups = [e["group"] for e in glossary_entries("en")]
    assert groups == sorted(groups, key=GROUPS.index)


def test_formula_is_identical_in_both_languages():
    formulas = {
        lang: {e["key"]: e.get("formula") for e in glossary_entries(lang)}
        for lang in LANGUAGES
    }
    assert formulas["en"] == formulas["de"]
    assert (
        formulas["en"]["expected_loss"]
        == r"\mathrm{EL} = \mathrm{PD}\cdot\mathrm{LGD}\cdot\mathrm{EAD}"
    )


@pytest.mark.parametrize("lang", LANGUAGES)
def test_in_project_placeholders_are_supplied_by_the_bundle(lang, bundle):
    figures = project_figures(bundle, lang)
    for entry in glossary_entries(lang):
        for name in PLACEHOLDER.findall(entry.get("in_project", "")):
            assert name in figures, (entry["key"], name)


def test_project_figures_are_formatted_per_language(bundle):
    assert project_figures(bundle, "en")["auc_rf"].count(".") == 1
    assert project_figures(bundle, "de")["auc_rf"].count(",") == 1
    assert project_figures(bundle, "de")["default_rate"].endswith(" %")


def test_glossary_help_returns_the_short_text():
    entry = next(e for e in glossary_entries("de") if e["key"] == "auc")
    assert glossary_help("auc", "de") == entry["what"]


def test_glossary_help_raises_key_error_for_an_unknown_key():
    with pytest.raises(KeyError, match="nope"):
        glossary_help("nope", "en")
