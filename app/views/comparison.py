"""Forest vs. scorecard page: metrics, how the scorecard works, IV, the practice question.

The numbers come from the bundle. The conclusion text is chosen from the two
AUCs, so it cannot go stale when the bundle is rebuilt.
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from app.ui import PAGES, current_mode, get_bundle, help_text, num, show_chart, t
from src.design import model_color

#: Models in display order.
MODELS = ("rf", "scorecard")
#: Glossary term, bundle key of each metric.
METRICS = (("auc", "roc_auc"), ("gini", "gini"), ("ks", "ks"))

bundle = get_bundle()
mode = current_mode()


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
