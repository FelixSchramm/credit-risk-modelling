"""Model performance page: ranking (ROC), calibration, score bands, threshold 0.5.

Everything is drawn from the arrays stored in the bundle, no raw data needed.
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from sklearn.calibration import calibration_curve
from sklearn.metrics import roc_curve

from app.ui import PAGES, current_mode, get_bundle, help_text, num, pct, show_chart, t
from src.design import model_color
from src.evaluate import charged_off_metrics

#: Models in display order.
MODELS = ("rf", "scorecard")
#: Neutral colour of the reference lines (a CSS name, so no hex code).
REFERENCE_COLOR = "gray"
#: Bins of the reliability diagram; quantile bins keep every point equally sized.
CALIBRATION_BINS = 10

bundle = get_bundle()
y_test = bundle["y_test"]
mode = current_mode()


def _roc_chart() -> go.Figure:
    """Draw the ROC curves of both models and the coin-toss diagonal.

    :return: The figure.
    """
    fig = go.Figure()
    fig.add_scatter(
        x=[0, 1],
        y=[0, 1],
        mode="lines",
        name=t("performance.roc_diagonal"),
        line={"color": REFERENCE_COLOR, "dash": "dot"},
    )
    for model in MODELS:
        fpr, tpr, _ = roc_curve(y_test, bundle[f"proba_{model}"])
        fig.add_scatter(
            x=fpr,
            y=tpr,
            mode="lines",
            name=t(f"performance.model_{model}"),
            line={"color": model_color(model, mode)},
        )
    fig.update_xaxes(title=t("performance.roc_x"), range=[0, 1])
    fig.update_yaxes(title=t("performance.roc_y"), range=[0, 1])
    return fig


def _calibration_chart() -> go.Figure:
    """Draw the reliability diagram before and after calibration for both models.

    Colour marks the model, line style and label mark before (dashed) and after
    (solid).

    :return: The figure.
    """
    fig = go.Figure()
    fig.add_scatter(
        x=[0, 1],
        y=[0, 1],
        mode="lines",
        name=t("performance.calibration_perfect"),
        line={"color": REFERENCE_COLOR, "dash": "dot"},
    )
    for model in MODELS:
        name = t(f"performance.model_{model}")
        for suffix, stage, dash in (("_raw", "before", "dash"), ("", "after", "solid")):
            observed, predicted = calibration_curve(
                y_test,
                bundle[f"proba_{model}{suffix}"],
                n_bins=CALIBRATION_BINS,
                strategy="quantile",
            )
            fig.add_scatter(
                x=predicted,
                y=observed,
                mode="lines+markers",
                name=t(f"performance.calibration_{stage}", model=name),
                line={"color": model_color(model, mode), "dash": dash},
            )
    fig.update_xaxes(title=t("performance.calibration_x"), range=[0, 1])
    fig.update_yaxes(title=t("performance.calibration_y"), range=[0, 1])
    return fig


def _band_chart(model: str, bands: pd.DataFrame) -> go.Figure:
    """Draw the observed default rate per band as bars, the mean score as line.

    Bars in the model colour, not status colours: the point is the rising
    height, not good or bad.

    :param model: ``"rf"`` or ``"scorecard"``.
    :param bands: The ``bands_*`` table of the bundle.
    :return: The figure.
    """
    fig = go.Figure()
    fig.add_bar(
        x=bands["band"],
        y=bands["default_rate"],
        name=t("performance.band_observed"),
        marker_color=model_color(model, mode),
    )
    fig.add_scatter(
        x=bands["band"],
        y=bands["mean_score"],
        mode="lines+markers",
        name=t("performance.band_mean"),
        line={"color": REFERENCE_COLOR, "dash": "dash"},
    )
    fig.update_xaxes(title=t("performance.band_x"), dtick=1)
    fig.update_yaxes(title=t("performance.band_y"), tickformat=".0%")
    return fig


def _band_table(bands: pd.DataFrame) -> pd.DataFrame:
    """Format the band table for display in the current language.

    :param bands: The ``bands_*`` table of the bundle.
    :return: Strings per cell, with translated column names.
    """
    return pd.DataFrame(
        {
            t("performance.col_band"): bands["band"],
            t("performance.col_n"): bands["n"].map(num),
            t("performance.col_mean_score"): bands["mean_score"].map(pct),
            t("performance.col_default_rate"): bands["default_rate"].map(pct),
        }
    )


def _monotonic_sentence(model: str, bands: pd.DataFrame) -> str:
    """Say in one sentence whether the default rate rises in every band.

    :param model: ``"rf"`` or ``"scorecard"``.
    :param bands: The ``bands_*`` table of the bundle.
    :return: The sentence.
    """
    name = t(f"performance.model_{model}")
    rises = bands["default_rate"].diff().dropna() > 0
    if rises.all():
        return t("performance.monotonic_yes", model=name)
    # ``rises`` is indexed by the row of the higher band; the reversal comes
    # after the band before it.
    first_reversal = int(bands["band"].iloc[rises.idxmin() - 1])
    return t("performance.monotonic_no", model=name, band=first_reversal)


def _report_table() -> pd.DataFrame:
    """Build the classification table at threshold 0.5 for both models.

    :return: One row per model, percentages as text.
    """
    rows = []
    for model in MODELS:
        figures = charged_off_metrics(y_test, bundle[f"proba_{model}"])
        rows.append(
            {
                t("performance.col_model"): t(f"performance.model_{model}"),
                **{
                    t(f"performance.col_{term}"): pct(value)
                    for term, value in figures.items()
                },
            }
        )
    return pd.DataFrame(rows)


st.title(t("performance.title"))
st.write(t("performance.intro"))

st.subheader(t("performance.metrics_title"))
for model in MODELS:
    st.markdown(f"**{t(f'performance.model_{model}')}**")
    metrics = bundle["metrics"][model]
    terms = (("auc", "roc_auc"), ("gini", "gini"), ("ks", "ks"))
    for column, (term, key) in zip(st.columns(len(terms)), terms):
        column.metric(
            t(f"performance.metric_{term}"),
            num(metrics[key], 3),
            help=help_text(term),
            border=True,
        )

st.subheader(t("performance.roc_title"), help=help_text("roc_curve"))
st.write(t("performance.roc_intro"))
show_chart(_roc_chart())

st.subheader(t("performance.calibration_title"), help=help_text("calibration"))
st.markdown(t("performance.calibration_intro"), help=help_text("reliability_diagram"))
show_chart(_calibration_chart())
st.caption(t("performance.calibration_note"))

st.subheader(t("performance.bands_title"), help=help_text("score_band"))
st.write(t("performance.bands_intro"))
for model, column in zip(MODELS, st.columns(len(MODELS))):
    bands = bundle[f"bands_{model}"]
    with column:
        st.markdown(f"**{t(f'performance.model_{model}')}**")
        show_chart(_band_chart(model, bands))
        st.write(_monotonic_sentence(model, bands))
        st.dataframe(_band_table(bands), hide_index=True, width="stretch")

st.subheader(t("performance.report_title"))
st.write(t("performance.report_intro"))
st.dataframe(
    _report_table(),
    hide_index=True,
    width="stretch",
    column_config={
        t(f"performance.col_{term}"): st.column_config.TextColumn(help=help_text(term))
        for term in ("precision", "recall", "f1", "accuracy")
    },
)
st.info(t("performance.report_threshold_note"))
st.page_link(PAGES["cutoff"], label=t("nav.cutoff"))
with st.expander(t("performance.report_text")):
    for model in MODELS:
        st.markdown(f"**{t(f'performance.model_{model}')}**")
        st.code(bundle["metrics"][model]["report"], language=None)
