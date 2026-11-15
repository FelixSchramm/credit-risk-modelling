"""Model limits page (the model card): what the model can and cannot do.

Mostly text from the locale files. Only today's AUC and the feature importances
come from the bundle; the historic AUC of 0.9999 is a fact quoted as text.
"""

import streamlit as st

from app.ui import LINKS, PAGES, get_bundle, help_text, num, pct, t

#: The regulatory text lives in the README; this page summarises and links.
README_REGULATORY = f"{LINKS['github']}#regulatory-context"

bundle = get_bundle()
# Impurity importance of the inner (uncalibrated) forest, in feature_names order.
forest = bundle["rf"].calibrated_classifiers_[0].estimator.estimator
importance = dict(zip(bundle["feature_names"], forest.feature_importances_))

st.title(t("limits.title"))
st.markdown(t("limits.intro"), help=help_text("model_card"))
st.warning(t("limits.notice"))

st.subheader(t("limits.leakage_title"), help=help_text("data_leakage"))
st.markdown(t("limits.leakage_intro"))
auc_before, auc_after = st.columns(2)
auc_before.metric(
    t("limits.leakage_before_label"),
    t("limits.leakage_before_value"),
    help=help_text("auc"),
    border=True,
)
auc_after.metric(
    t("limits.leakage_after_label"),
    num(bundle["metrics"]["rf"]["roc_auc"], 3),
    help=help_text("auc"),
    border=True,
)
st.markdown(t("limits.leakage_text"))

st.subheader(t("limits.default_title"), help=help_text("target"))
st.markdown(t("limits.default_text"))

st.subheader(t("limits.horizon_title"), help=help_text("pd"))
st.markdown(t("limits.horizon_text"))

st.subheader(t("limits.pd_title"), help=help_text("basel_irb"))
st.markdown(t("limits.pd_text"))
st.markdown(t("limits.pd_ifrs"), help=help_text("ifrs9"))
st.markdown(t("limits.pd_swiss"), help=help_text("finma"))

st.subheader(t("limits.population_title"))
st.markdown(t("limits.population_text"))

with st.container(border=True):
    st.subheader(t("limits.intrate_title"))
    st.warning(t("limits.intrate_notice"))
    st.markdown(t("limits.intrate_why"))
    st.markdown(
        t("limits.intrate_importance", share=pct(importance["int_rate"])),
        help=help_text("feature_importance"),
    )
    st.markdown(t("limits.intrate_clean"))
    st.page_link(PAGES["performance"], label=t("nav.performance"))

st.subheader(t("limits.calculator_title"))
st.markdown(t("limits.calculator_median"))
st.markdown(t("limits.calculator_flat"))
for column, (label, feature) in zip(
    st.columns(3),
    (
        ("calculator_metric_int_rate", "int_rate"),
        ("calculator_metric_dti", "dti"),
        ("calculator_metric_income", "annual_inc"),
    ),
):
    column.metric(
        t(f"limits.{label}"),
        pct(importance[feature]),
        help=help_text("feature_importance"),
        border=True,
    )
st.markdown(t("limits.calculator_year"))

st.subheader(t("limits.not_title"), help=help_text("model_validation"))
st.markdown(t("limits.not_text"))
st.markdown(t("limits.not_closing"))

st.markdown(t("limits.readme_text"))
st.link_button(t("limits.readme_link"), README_REGULATORY)
