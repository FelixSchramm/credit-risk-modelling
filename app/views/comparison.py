"""Forest vs. scorecard page: metrics, how the scorecard works, IV, the practice question.

The numbers come from the bundle. The conclusion text is chosen from the two
AUCs, so it cannot go stale when the bundle is rebuilt.
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from app.ui import PAGES, current_mode, get_bundle, help_text, num, show_chart, t
from src.comparison import better_model, default_min_iv
from src.design import model_color

#: Models in display order.
MODELS = ("rf", "scorecard")
#: Glossary term, bundle key of each metric.
METRICS = (("auc", "roc_auc"), ("gini", "gini"), ("ks", "ks"))

bundle = get_bundle()
mode = current_mode()
iv_sorted = bundle["iv_table"].sort_values("iv", ascending=False, ignore_index=True)


def _metrics_table() -> pd.DataFrame:
    """Build the metric table, one row per model.

    :return: Numbers as text, with translated column names.
    """
    return pd.DataFrame(
        [
            {
                t("comparison.col_model"): t(f"comparison.model_{model}"),
                **{
                    t(f"comparison.col_{term}"): num(bundle["metrics"][model][key], 3)
                    for term, key in METRICS
                },
            }
            for model in MODELS
        ]
    )


def _metrics_chart() -> go.Figure:
    """Draw the three metrics as grouped bars, one bar per model.

    The models are told apart by colour and by the legend label.

    :return: The figure.
    """
    fig = go.Figure()
    for model in MODELS:
        values = [bundle["metrics"][model][key] for _, key in METRICS]
        fig.add_bar(
            x=[t(f"comparison.col_{term}") for term, _ in METRICS],
            y=values,
            text=[num(value, 3) for value in values],
            name=t(f"comparison.model_{model}"),
            marker_color=model_color(model, mode),
        )
    fig.update_xaxes(title=t("comparison.chart_x"))
    fig.update_yaxes(title=t("comparison.chart_y"), range=[0, 1])
    return fig


def _iv_table() -> pd.DataFrame:
    """Format the IV table for display, sorted by IV, with translated columns.

    :return: One row per candidate feature.
    """
    return pd.DataFrame(
        {
            t("comparison.col_feature"): iv_sorted["name"],
            t("comparison.col_bins"): iv_sorted["n_bins"].map(num),
            t("comparison.col_iv"): iv_sorted["iv"].map(lambda iv: num(iv, 3)),
            t("comparison.col_selected"): iv_sorted["selected"],
        }
    )


st.title(t("comparison.title"))
st.markdown(t("comparison.intro"))
for model, term, column in zip(MODELS, ("random_forest", "scorecard"), st.columns(2)):
    with column.container(border=True):
        st.markdown(f"**{t(f'comparison.model_{model}')}**", help=help_text(term))
        st.caption(t(f"comparison.model_{model}_text"))

st.subheader(t("comparison.metrics_title"))
st.markdown(t("comparison.metrics_intro", n_test=num(bundle["n_test"])))
st.dataframe(
    _metrics_table(),
    hide_index=True,
    width="stretch",
    column_config={
        t(f"comparison.col_{term}"): st.column_config.TextColumn(help=help_text(term))
        for term, _ in METRICS
    },
)
show_chart(_metrics_chart())
st.caption(t("comparison.metrics_more"))
st.page_link(PAGES["performance"], label=t("nav.performance"))

st.subheader(t("comparison.mechanics_title"), help=help_text("scorecard"))
st.markdown(t("comparison.woe_text"), help=help_text("woe"))
st.markdown(t("comparison.binning_text"), help=help_text("binning"))
st.markdown(t("comparison.woe_why"))

min_iv = num(default_min_iv(), 2)
dropped = iv_sorted.loc[~iv_sorted["selected"], "name"]
st.subheader(t("comparison.iv_title"), help=help_text("iv"))
st.markdown(t("comparison.iv_text", min_iv=min_iv))
st.markdown(f"**{t('comparison.iv_reading')}** {t('glossary.iv.how_to_read')}")
st.caption(t("comparison.iv_leakage"))
st.dataframe(
    _iv_table(),
    hide_index=True,
    width="stretch",
    height=400,
    column_config={
        t("comparison.col_bins"): st.column_config.TextColumn(
            help=help_text("binning")
        ),
        t("comparison.col_iv"): st.column_config.TextColumn(help=help_text("iv")),
    },
)
st.markdown(
    t(
        "comparison.dropped_text",
        n_dropped=num(len(dropped)),
        n_total=num(len(bundle["iv_table"])),
        min_iv=min_iv,
    )
)
with st.expander(t("comparison.dropped_expander")):
    st.markdown(", ".join(f"`{name}`" for name in dropped))
st.markdown(f"**{t('comparison.iv_notes_title')}**")
st.markdown(f"- {t('comparison.iv_note_int_rate')}")
st.markdown(f"- {t('comparison.iv_note_fico')}")
st.page_link(PAGES["limits"], label=t("nav.limits"))

st.subheader(t("comparison.practice_title"))
auc = {model: bundle["metrics"][model]["roc_auc"] for model in MODELS}
st.info(
    t(
        f"comparison.conclusion_{better_model(bundle['metrics'])}",
        auc_rf=num(auc["rf"], 3),
        auc_scorecard=num(auc["scorecard"], 3),
        gap=num(abs(auc["rf"] - auc["scorecard"]), 3),
    )
)
st.markdown(t("comparison.practice_scorecard"), help=help_text("scorecard"))
st.markdown(t("comparison.practice_forest"), help=help_text("random_forest"))
st.markdown(t("comparison.practice_robust"))
st.markdown(t("comparison.practice_summary"))
