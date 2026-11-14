"""Calculator page: score one application (optionally two variants) with both models.

Only UI and calls into :mod:`src.scoring`; no model or feature logic here.
"""

import streamlit as st

from app.ui import get_bundle, help_text, num, pct, t
from src.features import convert_emp_length
from src.scoring import band_of, percentile_of, score

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
    # Variant B starts with the other term: the typical what-if is 36 vs. 60.
    default = categories[-1] if field == "term" and variant == "b" else spec["default"]
    # Categories are data values and stay untranslated; strip only the padding
    # (" 36 months") that the raw column carries.
    return st.selectbox(
        label,
        categories,
        categories.index(default),
        format_func=str.strip,
        key=key,
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
    compare = st.toggle(t("calculator.compare"), key="compare")
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
