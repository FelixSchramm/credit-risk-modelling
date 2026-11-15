"""Smoke tests of the Streamlit app with ``streamlit.testing.v1.AppTest``."""

import base64
import json
from pathlib import Path

import numpy as np
import pytest
from sklearn.calibration import calibration_curve
from streamlit.testing.v1 import AppTest

from app.ui import LINKS, PAGES
from src.bundle import load_bundle
from src.i18n import fmt_number, fmt_percent, translate
from src.scoring import cutoff_table, score

ENTRY = str(Path(__file__).resolve().parents[1] / "streamlit_app.py")


@pytest.mark.parametrize("page", list(PAGES))
def test_every_page_renders_without_exception(page, bundle_env):
    at = AppTest.from_file(ENTRY, default_timeout=30).run()
    at.switch_page(PAGES[page]).run()
    assert not at.exception


def test_missing_bundle_shows_a_message_instead_of_an_exception(monkeypatch, tmp_path):
    monkeypatch.setenv("BUNDLE_PATH", str(tmp_path / "missing.joblib"))
    at = AppTest.from_file(ENTRY, default_timeout=30).run()
    assert not at.exception
    assert "scripts/build_bundle.py" in at.error[0].value


@pytest.mark.parametrize("lang", ["en", "de"])
@pytest.mark.parametrize("page", list(PAGES))
def test_every_page_renders_in_both_languages(page, lang, bundle_env):
    at = AppTest.from_file(ENTRY, default_timeout=30)
    at.query_params["lang"] = lang
    at.run()
    at.switch_page(PAGES[page]).run()
    assert not at.exception
    assert at.session_state["lang"] == lang


def test_language_switcher_changes_title_and_query_parameter(bundle_env):
    at = AppTest.from_file(ENTRY, default_timeout=30).run()
    assert at.title[0].value == "Credit risk dashboard"
    assert at.query_params["lang"] == "en"
    at.sidebar.radio(key="lang").set_value("de").run()
    assert not at.exception
    assert at.title[0].value == "Kreditrisiko-Dashboard"
    assert at.query_params["lang"] == "de"


def test_language_survives_a_page_switch(bundle_env):
    at = AppTest.from_file(ENTRY, default_timeout=30)
    at.query_params["lang"] = "de"
    at.run()
    at.switch_page(PAGES["home"]).run()
    assert at.query_params["lang"] == "de"


def test_invalid_language_in_the_url_falls_back_to_english(bundle_env):
    at = AppTest.from_file(ENTRY, default_timeout=30)
    at.query_params["lang"] = "fr"
    at.run()
    assert at.session_state["lang"] == "en"
    assert at.query_params["lang"] == "en"


def test_missing_bundle_message_is_translated(monkeypatch, tmp_path):
    monkeypatch.setenv("BUNDLE_PATH", str(tmp_path / "missing.joblib"))
    at = AppTest.from_file(ENTRY, default_timeout=30)
    at.query_params["lang"] = "de"
    at.run()
    assert at.error[0].value.startswith("Modell-Bundle nicht gefunden")


@pytest.mark.parametrize("lang", ["en", "de"])
def test_glossary_search_reduces_the_entries(lang, bundle_env):
    at = AppTest.from_file(ENTRY, default_timeout=30)
    at.query_params["lang"] = lang
    at.run()
    at.switch_page(PAGES["glossary"]).run()
    assert not at.exception
    all_entries = len(at.expander)
    assert all_entries > 40
    at.text_input(key="glossary_search").set_value("gini").run()
    assert not at.exception
    assert 0 < len(at.expander) < all_entries
    lower_hits = len(at.expander)
    at.text_input(key="glossary_search").set_value("GINI").run()
    assert len(at.expander) == lower_hits
    # "FINMA" appears only in capitals, so the text must be lower-cased as well.
    at.text_input(key="glossary_search").set_value("finma").run()
    assert [expander.label for expander in at.expander] == ["FINMA"]


def test_glossary_search_without_hits_shows_a_message(bundle_env):
    at = AppTest.from_file(ENTRY, default_timeout=30).run()
    at.switch_page(PAGES["glossary"]).run()
    at.text_input(key="glossary_search").set_value("zzzzqqq").run()
    assert not at.exception
    assert len(at.expander) == 0
    assert at.info[0].value == "No entry matches your search."


@pytest.mark.parametrize("lang", ["en", "de"])
def test_start_page_shows_four_tiles_with_bundle_values(lang, bundle_env):
    bundle = load_bundle(bundle_env)
    at = AppTest.from_file(ENTRY, default_timeout=30)
    at.query_params["lang"] = lang
    at.run()
    assert not at.exception
    rf = bundle["metrics"]["rf"]
    expected = [
        fmt_number(rf["roc_auc"], 3, lang),
        fmt_number(rf["gini"], 3, lang),
        fmt_number(rf["ks"], 3, lang),
        fmt_percent(bundle["y_test"].mean(), 1, lang),
    ]
    assert [metric.value for metric in at.metric] == expected
    assert all(metric.help for metric in at.metric)


@pytest.mark.parametrize("lang", ["en", "de"])
def test_start_page_shows_the_demo_notice(lang, bundle_env):
    at = AppTest.from_file(ENTRY, default_timeout=30)
    at.query_params["lang"] = lang
    at.run()
    assert [w.value for w in at.warning] == [translate("home.notice", lang)]


def test_start_page_shows_a_button_for_every_link(bundle_env):
    at = AppTest.from_file(ENTRY, default_timeout=30).run()
    urls = [button.proto.url for button in at.get("link_button")]
    assert urls == list(LINKS.values())
    assert len(urls) == 3


def test_start_page_guide_describes_every_other_page(bundle_env):
    at = AppTest.from_file(ENTRY, default_timeout=30).run()
    captions = [caption.value for caption in at.caption]
    for key in PAGES.keys() - {"home"}:
        assert translate(f"nav_desc.{key}", "en") in captions


def _calculator(lang, bundle_env):
    at = AppTest.from_file(ENTRY, default_timeout=30)
    at.query_params["lang"] = lang
    at.run()
    return at.switch_page(PAGES["calculator"]).run()


@pytest.mark.parametrize("lang", ["en", "de"])
def test_calculator_shows_both_calibrated_pds_and_the_notice(lang, bundle_env):
    bundle = load_bundle(bundle_env)
    at = _calculator(lang, bundle_env)
    assert not at.exception
    defaults = {
        field: spec.get("median", spec.get("default"))
        for field, spec in bundle["input_spec"].items()
    }
    expected = score(defaults, bundle)
    pds = [at.metric[0].value, at.metric[2].value]
    assert pds == [fmt_percent(expected[m], 1, lang) for m in ("rf", "scorecard")]
    # Four result metrics, then the two of the forest explanation.
    assert len(at.metric) == 4 + 2
    assert all(metric.help for metric in at.metric)
    notice = translate(
        "calculator.notice",
        lang,
        n_inputs=fmt_number(len(bundle["input_spec"]), 0, lang),
        n_features=fmt_number(len(bundle["feature_names"]), 0, lang),
    )
    assert [w.value for w in at.warning] == [notice]


def test_calculator_variant_b_starts_as_a_with_the_other_term(bundle_env):
    at = _calculator("en", bundle_env)
    at.number_input(key="a_int_rate").set_value(21.5).run()
    at.selectbox(key="a_purpose").select("car").run()
    at.toggle(key="compare").set_value(True).run()
    assert not at.exception
    fields = ["loan_amnt", "int_rate", "annual_inc", "dti", "fico_range_low"]
    for field in fields + ["emp_length", "purpose"]:
        a, b = at.session_state[f"a_{field}"], at.session_state[f"b_{field}"]
        assert a == b, field
    assert at.session_state["a_term"] == " 36 months"
    assert at.session_state["b_term"] == " 60 months"


def test_calculator_variant_b_shows_the_pd_difference(bundle_env):
    at = _calculator("en", bundle_env)
    at.toggle(key="compare").set_value(True).run()
    at.number_input(key="b_int_rate").set_value(25.0).run()
    assert not at.exception
    assert len(at.metric) == 8 + 2
    assert at.metric[4].delta.startswith("+")
    assert at.metric[4].delta.endswith("pp vs. variant A")


def _charts(at) -> list[dict]:
    """The Plotly figures of the page as dicts (data and layout)."""
    return [json.loads(chart.proto.spec) for chart in at.get("plotly_chart")]


@pytest.mark.parametrize("lang", ["en", "de"])
def test_calculator_explains_the_score_with_two_plotly_charts(lang, bundle_env):
    at = _calculator(lang, bundle_env)
    assert not at.exception
    waterfall, bars = _charts(at)
    assert waterfall["data"][0]["type"] == "waterfall"
    assert bars["data"][0]["type"] == "bar"
    # Direction is readable without colour: signed labels on every step.
    assert all(s.startswith(("+", "-")) for s in waterfall["data"][0]["text"][1:-1])
    assert all(s.startswith(("+", "-")) for s in bars["data"][0]["text"])
    bundle = load_bundle(bundle_env)
    note = translate(
        "calculator.rf_uncalibrated",
        lang,
        base_rate=fmt_percent(bundle["base_rate"], 1, lang),
    )
    assert note in [info.value for info in at.info]


def test_calculator_waterfall_ends_at_base_plus_all_steps(bundle_env):
    waterfall = _charts(_calculator("en", bundle_env))[0]["data"][0]
    base, *steps, total = waterfall["x"]
    assert waterfall["measure"][0] == "absolute" and waterfall["measure"][-1] == "total"
    assert base + sum(steps) == pytest.approx(total)


def test_calculator_explanation_follows_variant_a_in_compare_mode(bundle_env):
    at = _calculator("en", bundle_env)
    before = _charts(at)[1]["data"][0]["x"]
    at.toggle(key="compare").set_value(True).run()
    at.number_input(key="b_int_rate").set_value(20.0).run()
    assert len(_charts(at)) == 2
    assert _charts(at)[1]["data"][0]["x"] == before
    at.number_input(key="a_int_rate").set_value(20.0).run()
    assert _charts(at)[1]["data"][0]["x"] != before


@pytest.mark.parametrize("start, target", [("en", "de"), ("de", "en")])
def test_calculator_input_survives_a_language_switch(start, target, bundle_env):
    at = _calculator(start, bundle_env)
    at.number_input(key="a_int_rate").set_value(21.5).run()
    at.selectbox(key="a_term").select(" 60 months").run()
    at.sidebar.radio(key="lang").set_value(target).run()
    assert not at.exception
    assert at.number_input(key="a_int_rate").value == 21.5
    assert at.selectbox(key="a_term").value == " 60 months"
    assert at.title[0].value == translate("calculator.title", target)


def _performance(lang):
    at = AppTest.from_file(ENTRY, default_timeout=30)
    at.query_params["lang"] = lang
    at.run()
    return at.switch_page(PAGES["performance"]).run()


@pytest.mark.parametrize("lang", ["en", "de"])
def test_performance_page_shows_the_bundle_metrics_with_tooltips(lang, bundle_env):
    bundle = load_bundle(bundle_env)
    at = _performance(lang)
    assert not at.exception
    expected = [
        fmt_number(bundle["metrics"][model][key], 3, lang)
        for model in ("rf", "scorecard")
        for key in ("roc_auc", "gini", "ks")
    ]
    assert [metric.value for metric in at.metric] == expected
    assert all(metric.help for metric in at.metric)


@pytest.mark.parametrize("lang", ["en", "de"])
def test_performance_page_draws_roc_calibration_and_two_band_charts(lang, bundle_env):
    at = _performance(lang)
    charts = [json.loads(chart.proto.spec) for chart in at.get("plotly_chart")]
    assert len(charts) == 4
    assert len(charts[0]["data"]) == 3
    # Per model, before and after differ in line style and label, not only in
    # colour; the colour is the model's own.
    lines = {
        trace["name"]: (trace["line"]["dash"], trace["line"]["color"])
        for trace in charts[1]["data"][1:]
    }
    assert len(lines) == 4
    dashes = sorted(dash for dash, _ in lines.values())
    assert dashes == ["dash", "dash", "solid", "solid"]
    assert len({color for _, color in lines.values()}) == 2
    assert all(chart["layout"]["xaxis"]["title"]["text"] for chart in charts)
    # Monotonicity is shown by bars, not by status colours.
    assert charts[2]["data"][0]["type"] == "bar"


def _decode(array):
    """Decode a plotly array, which the spec ships base64-encoded."""
    raw = base64.b64decode(array["bdata"])
    return np.frombuffer(raw, dtype=array["dtype"])


def test_performance_page_plots_quantile_calibration_points(bundle_env):
    bundle = load_bundle(bundle_env)
    at = _performance("en")
    trace = json.loads(at.get("plotly_chart")[1].proto.spec)["data"][-1]
    observed, predicted = calibration_curve(
        bundle["y_test"], bundle["proba_scorecard"], n_bins=10, strategy="quantile"
    )
    assert _decode(trace["x"]) == pytest.approx(predicted)
    assert _decode(trace["y"]) == pytest.approx(observed)


@pytest.mark.parametrize("lang", ["en", "de"])
def test_performance_page_states_monotonicity_and_the_threshold_caveat(
    lang, bundle_env
):
    bundle = load_bundle(bundle_env)
    at = _performance(lang)
    texts = [markdown.value for markdown in at.markdown]
    for model in ("rf", "scorecard"):
        name = translate(f"performance.model_{model}", lang)
        rates = bundle[f"bands_{model}"]["default_rate"].tolist()
        reversals = [i + 1 for i in range(9) if rates[i + 1] <= rates[i]]
        if reversals:
            expected = translate(
                "performance.monotonic_no", lang, model=name, band=reversals[0]
            )
        else:
            expected = translate("performance.monotonic_yes", lang, model=name)
        assert expected in texts
    assert [info.value for info in at.info] == [
        translate("performance.report_threshold_note", lang)
    ]
    assert len(at.dataframe) == 3


def _cutoff(lang):
    at = AppTest.from_file(ENTRY, default_timeout=30)
    at.query_params["lang"] = lang
    at.run()
    return at.switch_page(PAGES["cutoff"]).run()


def _cutoff_row(bundle, threshold, model="rf", loss=0.6, margin=0.1):
    """The expected table row for one cut-off, computed from the bundle."""
    amount = bundle["input_spec"]["loan_amnt"]["median"]
    table = cutoff_table(
        bundle["y_test"],
        bundle[f"proba_{model}"],
        np.array([threshold]),
        loss,
        margin,
        amount,
    )
    return table.iloc[0]


@pytest.mark.parametrize("lang", ["en", "de"])
def test_cutoff_page_shows_the_table_figures_with_tooltips(lang, bundle_env):
    bundle = load_bundle(bundle_env)
    at = _cutoff(lang)
    assert not at.exception
    row = _cutoff_row(bundle, 0.2)
    shown = [metric.value for metric in at.metric]
    assert shown[0] == fmt_percent(row["approval_rate"], 1, lang)
    assert shown[1] == fmt_number(row["accepted"], 0, lang)
    assert shown[2] == fmt_number(row["rejected"], 0, lang)
    assert shown[4:7] == [
        fmt_number(row[key], 0, lang) for key in ("caught", "missed", "rejected_good")
    ]
    assert all(metric.help for metric in at.metric)
    assert at.warning[0].value == translate("cutoff.notice", lang)


def test_cutoff_page_slider_and_model_change_the_figures(bundle_env):
    bundle = load_bundle(bundle_env)
    at = _cutoff("en")
    before = [metric.value for metric in at.metric]
    at.select_slider(key="cutoff_threshold").set_value(0.1).run()
    row = _cutoff_row(bundle, 0.1)
    assert at.metric[1].value == fmt_number(row["accepted"], 0, "en")
    assert [metric.value for metric in at.metric] != before
    at.radio(key="cutoff_model").set_value("scorecard").run()
    row = _cutoff_row(bundle, 0.1, model="scorecard")
    assert at.metric[1].value == fmt_number(row["accepted"], 0, "en")


def test_cutoff_page_economics_parameters_change_the_net_result(bundle_env):
    bundle = load_bundle(bundle_env)
    at = _cutoff("en")
    at.select_slider(key="cutoff_loss").set_value(0.9).run()
    at.select_slider(key="cutoff_margin").set_value(0.2).run()
    row = _cutoff_row(bundle, 0.2, loss=0.9, margin=0.2)
    expected = translate(
        "cutoff.million_usd", "en", value=fmt_number(row["net_result"] / 1e6, 1, "en")
    )
    assert at.metric[9].value == expected


@pytest.mark.parametrize("lang", ["en", "de"])
def test_cutoff_page_marks_the_optimum_on_a_single_axis(lang, bundle_env):
    bundle = load_bundle(bundle_env)
    at = _cutoff(lang)
    chart = json.loads(at.get("plotly_chart")[0].proto.spec)
    assert "yaxis2" not in chart["layout"]
    curve, _, best = chart["data"]
    assert best["mode"] == "markers+text"
    assert best["text"][0]
    thresholds = np.arange(101) / 100
    table = cutoff_table(
        bundle["y_test"],
        bundle["proba_rf"],
        thresholds,
        0.6,
        0.1,
        bundle["input_spec"]["loan_amnt"]["median"],
    )
    top = table.loc[table["net_result"].idxmax()]
    assert best["x"][0] == pytest.approx(top["threshold"])
    assert best["y"][0] == pytest.approx(top["net_result"] / 1e6)
    assert max(_decode(curve["y"])) == pytest.approx(best["y"][0])


def test_cutoff_page_inputs_survive_a_language_switch(bundle_env):
    # Only EN -> DE: AppTest cannot set a select_slider by value once the option
    # texts use a decimal comma, so the reverse direction cannot be driven.
    at = _cutoff("en")
    at.select_slider(key="cutoff_threshold").set_value(0.35).run()
    at.select_slider(key="cutoff_loss").set_value(0.8).run()
    at.select_slider(key="cutoff_margin").set_value(0.25).run()
    at.radio(key="cutoff_model").set_value("scorecard").run()
    at.sidebar.radio(key="lang").set_value("de").run()
    assert not at.exception
    assert at.select_slider(key="cutoff_threshold").value == 0.35
    assert at.select_slider(key="cutoff_loss").value == 0.8
    assert at.select_slider(key="cutoff_margin").value == 0.25
    assert at.radio(key="cutoff_model").value == "scorecard"
    assert at.title[0].value == translate("cutoff.title", "de")


def test_performance_page_links_to_the_cutoff_page(bundle_env):
    links = [link.proto for link in _performance("en").main.get("page_link")]
    assert [(link.label, link.page) for link in links] == [
        ("Cut-off and loss", "cutoff")
    ]
