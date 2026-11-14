"""Calculator page: score one application (optionally two variants) with both models.

Only UI and calls into :mod:`src.scoring`; no model or feature logic here.
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from app.ui import current_mode, get_bundle, help_text, num, pct, show_chart, t
from src.design import model_color
from src.features import convert_emp_length
from src.scoring import (
    band_of,
    explain_forest,
    explain_scorecard,
    forest_explainer,
    percentile_of,
    score,
    top_contributions,
)

#: Input step per numeric field; the bounds and defaults come from ``input_spec``.
STEPS = {
    "loan_amnt": 500.0,
    "int_rate": 0.25,
    "annual_inc": 1000.0,
    "dti": 0.5,
    "fico_range_low": 5.0,
}
#: Two models this many risk bands apart get a hint that this is a finding.
DIVERGENCE_BANDS = 2
#: Inputs shown one by one in the explanation charts; the rest is summed up.
TOP_N = 10

bundle = get_bundle()


def _input(field: str, spec: dict[str, object], variant: str) -> object:
    """Draw the widget of one input field.

    :param field: Field name in ``input_spec``.
    :param spec: Its ``input_spec`` entry (bounds and default, or categories).
    :param variant: ``"a"`` or ``"b"``; part of the fixed widget key.
    :return: The entered value.
    """
    label = t(f"calculator.label_{field}")
    key = f"{variant}_{field}"
    if "categories" not in spec:
        return st.number_input(
            label,
            spec["min"],
            spec["max"],
            spec["median"],
            STEPS[field],
            key=key,
            format="%.2f" if field in ("int_rate", "dti") else "%.0f",
        )
    categories = spec["categories"]
    if field == "emp_length":
        categories = sorted(categories, key=convert_emp_length)
    # Categories are data values and stay untranslated; strip only the padding
    # (" 36 months") that the raw column carries.
    return st.selectbox(
        label,
        categories,
        categories.index(spec["default"]),
        format_func=str.strip,
        key=key,
    )


def _start_variant_b() -> None:
    """Start variant B as a copy of A with the other term (the typical what-if).

    Runs as ``on_change`` of the compare toggle, before the page reruns.
    """
    for field in bundle["input_spec"]:
        st.session_state[f"b_{field}"] = st.session_state[f"a_{field}"]
    terms = bundle["input_spec"]["term"]["categories"]
    st.session_state["b_term"] = next(
        term for term in terms if term != st.session_state["a_term"]
    )


def _results(
    user_input: dict[str, object], reference: dict[str, float] | None
) -> dict[str, float]:
    """Show the calibrated PD, band and percentile of both models.

    :param user_input: The application, one value per ``input_spec`` field.
    :param reference: Scores of variant A; if given, the PD shows the
        difference to it.
    :return: The scores of this application per model.
    """
    scores = score(user_input, bundle)
    bands = {}
    for column, model in zip(st.columns(2), scores):
        proba = scores[model]
        band_table = bundle[f"bands_{model}"]
        bands[model] = band_of(proba, band_table)
        delta = None
        if reference is not None:
            diff = (proba - reference[model]) * 100
            sign = "+" if diff > 0 else ""
            delta = t("calculator.delta_pp", value=f"{sign}{num(diff, 1)}")
        with column:
            st.markdown(f"**{t(f'calculator.model_{model}')}**")
            st.metric(
                t("calculator.metric_pd"),
                pct(proba),
                delta,
                delta_color="inverse",
                help=help_text("pd"),
                border=True,
            )
            st.metric(
                t("calculator.metric_band"),
                t("calculator.band_value", band=bands[model], n_bands=len(band_table)),
                help=help_text("score_band"),
                border=True,
            )
            share = percentile_of(proba, bundle[f"proba_{model}"]) / 100
            st.caption(t("calculator.percentile", share=pct(share, 0)))
    if abs(bands["rf"] - bands["scorecard"]) >= DIVERGENCE_BANDS:
        st.info(t("calculator.models_differ"))
    return scores


@st.cache_resource
def _explainer(created_at: str):
    """Build the TreeSHAP explainer once per bundle, not on every input change.

    :param created_at: ``created_at`` of the bundle; the cache key (the bundle
        dict itself is not hashable).
    :return: The explainer of the inner forest.
    """
    return forest_explainer(bundle)


def _signed(value: float, decimals: int) -> str:
    """Format a number with an explicit plus sign, so direction is not colour only.

    :param value: Number.
    :param decimals: Digits after the decimal mark.
    :return: E.g. ``"+0.012"`` or ``"-0.340"``.
    """
    return ("+" if value > 0 else "") + num(value, decimals)


def _labels(table: pd.DataFrame) -> list[str]:
    """Build the ``feature: value`` axis labels (just the name for the summed row).

    :param table: Table with ``feature`` and, except for the summed row,
        ``value``.
    :return: One label per row.
    """
    labels = []
    for feature, value in zip(table["feature"], table.get("value", [])):
        if pd.isna(value):
            labels.append(feature)
        elif isinstance(value, str):
            labels.append(f"{feature}: {value.strip()}")
        else:
            labels.append(f"{feature}: {num(value, 0 if value == int(value) else 2)}")
    return labels


def _waterfall(table: pd.DataFrame, base: float) -> go.Figure:
    """Draw the SHAP waterfall of the forest from the base value to the raw score.

    :param table: Output of :func:`src.scoring.explain_forest`.
    :param base: Base value of the explainer.
    :return: The figure; styling is done by ``show_chart``.
    """
    top = top_contributions(table, TOP_N, t("calculator.rest", n=len(table) - TOP_N))
    steps = top["contribution"].to_numpy()
    total = base + steps.sum()
    levels = base + steps.cumsum()
    color = model_color("rf", current_mode())
    fig = go.Figure(
        go.Waterfall(
            orientation="h",
            y=[
                t("calculator.rf_base_label"),
                *_labels(top),
                t("calculator.rf_total_label"),
            ],
            x=[base, *steps, total],
            measure=["absolute", *["relative"] * len(top), "total"],
            text=[
                num(base, 3),
                *[_signed(step, 3) for step in steps],
                num(total, 3),
            ],
            textposition="outside",
            cliponaxis=False,
            increasing={"marker": {"color": color}},
            decreasing={"marker": {"color": color}},
            totals={"marker": {"color": color}},
        )
    )
    # Zoom to the steps: from zero the bars would be hairlines next to a 0.5 base.
    low, high = min(base, levels.min(), total), max(base, levels.max(), total)
    pad = (high - low) * 0.25 or 0.01
    fig.update_xaxes(title=t("calculator.rf_axis"), range=[low - pad, high + pad])
    fig.update_yaxes(autorange="reversed")
    return fig


def _contribution_bars(table: pd.DataFrame) -> go.Figure:
    """Draw the scorecard contributions as horizontal bars.

    :param table: Output of :func:`src.scoring.explain_scorecard`.
    :return: The figure; styling is done by ``show_chart``.
    """
    top = top_contributions(table, TOP_N, t("calculator.rest", n=len(table) - TOP_N))
    contributions = top["contribution"]
    fig = go.Figure(
        go.Bar(
            orientation="h",
            y=_labels(top),
            x=contributions,
            text=[_signed(value, 2) for value in contributions],
            textposition="outside",
            cliponaxis=False,
            marker_color=model_color("scorecard", current_mode()),
            hovertext=[
                "" if pd.isna(woe) else t("calculator.sc_hover", woe=num(woe, 2))
                for woe in top["woe"]
            ],
            hoverinfo="text",
        )
    )
    fig.update_xaxes(title=t("calculator.sc_axis"))
    fig.update_yaxes(autorange="reversed")
    return fig


def _explain(application: dict[str, object]) -> None:
    """Show why variant A got its scores: SHAP for the forest, WOE for the scorecard.

    :param application: The entered application of variant A.
    """
    st.subheader(t("calculator.explain_title"))
    if compare:
        st.caption(t("calculator.explain_for_a"))
    st.caption(t("calculator.explain_feature_note"))
    forest_tab, scorecard_tab = st.tabs(
        [t("calculator.tab_rf"), t("calculator.tab_scorecard")], key="explain_tabs"
    )
    with forest_tab:
        table, base = explain_forest(
            application, bundle, _explainer(bundle["created_at"])
        )
        st.subheader(t("calculator.rf_title"), help=help_text("waterfall"))
        st.markdown(t("calculator.rf_read"))
        st.info(t("calculator.rf_uncalibrated", base_rate=pct(bundle["base_rate"])))
        base_column, score_column = st.columns(2)
        base_column.metric(
            t("calculator.rf_metric_base"),
            num(base, 3),
            help=help_text("shap_base_value"),
            border=True,
        )
        score_column.metric(
            t("calculator.rf_metric_score"),
            num(base + table["contribution"].sum(), 3),
            help=help_text("shap"),
            border=True,
        )
        show_chart(_waterfall(table, base))
    with scorecard_tab:
        table, intercept = explain_scorecard(application, bundle)
        total = table["contribution"].sum()
        st.subheader(t("calculator.sc_title"), help=help_text("scorecard_points"))
        st.markdown(t("calculator.sc_read"), help=help_text("woe"))
        st.info(t("calculator.sc_uncalibrated"))
        show_chart(_contribution_bars(table))
        st.caption(
            t(
                "calculator.sc_sum",
                intercept=num(intercept, 2),
                total=num(total, 2),
                log_odds=num(intercept + total, 2),
            )
        )
    st.subheader(t("calculator.compare_title"))
    st.markdown(t("calculator.compare_text"))


st.title(t("calculator.title"))
# Mandatory notice, directly under the title so it is visible without scrolling.
st.warning(
    t(
        "calculator.notice",
        n_inputs=num(len(bundle["input_spec"])),
        n_features=num(len(bundle["feature_names"])),
    )
)

inputs_column, results_column = st.columns([1, 2])
with inputs_column:
    st.subheader(t("calculator.inputs_title"))
    compare = st.toggle(
        t("calculator.compare"), key="compare", on_change=_start_variant_b
    )
    variants = ["a", "b"] if compare else ["a"]
    applications = {}
    for variant in variants:
        if compare:
            st.markdown(f"**{t(f'calculator.variant_{variant}')}**")
        applications[variant] = {
            field: _input(field, spec, variant)
            for field, spec in bundle["input_spec"].items()
        }
    st.caption(t("calculator.derived"))

with results_column:
    st.subheader(t("calculator.results_title"))
    reference = None
    for variant, application in applications.items():
        if compare:
            st.markdown(f"**{t(f'calculator.variant_{variant}')}**")
        scores = _results(application, reference)
        reference = reference or scores

st.divider()
_explain(applications["a"])
