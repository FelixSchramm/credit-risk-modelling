"""Cut-off page: what a decision threshold means in loans and in money.

Everything is computed from the arrays in the bundle (``src.scoring.cutoff_table``),
the page only renders. The money part is an illustration of the logic: LGD and EAD
are not modelled, one loan amount stands for all loans.
"""

import math

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from app.ui import current_mode, get_bundle, help_text, num, pct, show_chart, t
from src.design import model_color
from src.scoring import cutoff_table

#: Models in display order.
MODELS = ("rf", "scorecard")
#: Selectable cut-offs 0.00 to 1.00. The curve is drawn on the same grid.
THRESHOLDS = [i / 100 for i in range(101)]
#: Start values: a cut-off in the range where calibrated scores matter, a loss
#: of 60% of the loan per default and a margin of 10% per good loan.
DEFAULT_THRESHOLD = 0.2
LOSS_SHARES = [i / 100 for i in range(0, 101, 5)]
DEFAULT_LOSS_SHARE = 0.6
MARGIN_SHARES = [i / 100 for i in range(51)]
DEFAULT_MARGIN_SHARE = 0.1

#: Neutral colour of the reference line (a CSS name, so no hex code).
REFERENCE_COLOR = "gray"

bundle = get_bundle()
y_test = bundle["y_test"]
# The bundle has no per-loan amounts of the test set, so one typical amount
# stands for every loan (the EAD placeholder).
loan_amount = bundle["input_spec"]["loan_amnt"]["median"]


def _show(metrics: list[tuple[str, str, str]]) -> None:
    """Draw one row of bordered metrics.

    :param metrics: Per tile the key of its label, its value text and the
        glossary key of its tooltip.
    """
    for column, (key, value, term) in zip(st.columns(len(metrics)), metrics):
        column.metric(
            t(f"cutoff.metric_{key}"), value, help=help_text(term), border=True
        )


def _million(value: float) -> str:
    """Format a USD amount in millions in the current language.

    :param value: Amount in USD.
    :return: E.g. ``"12.3 million USD"``.
    """
    return t("cutoff.million_usd", value=num(value / 1e6, 1))


def _net_result_chart(
    model: str, curve: pd.DataFrame, threshold: float, best: pd.Series
) -> go.Figure:
    """Draw the net result over the cut-off with the best cut-off marked.

    The optimum carries a marker and a label, not only a colour. One y axis
    only: the curve is the single quantity.

    :param model: ``"rf"`` or ``"scorecard"``.
    :param curve: Output of ``cutoff_table`` over all cut-offs.
    :param threshold: Selected cut-off.
    :param best: Row of ``curve`` with the highest net result.
    :return: The figure.
    """
    mode = current_mode()
    fig = go.Figure()
    fig.add_scatter(
        x=curve["threshold"],
        y=curve["net_result"] / 1e6,
        mode="lines",
        name=t("cutoff.chart_curve"),
        line={"color": model_color(model, mode)},
    )
    fig.add_scatter(
        x=[threshold, threshold],
        y=[curve["net_result"].min() / 1e6, curve["net_result"].max() / 1e6],
        mode="lines",
        name=t("cutoff.chart_selected"),
        line={"color": REFERENCE_COLOR, "dash": "dot"},
    )
    fig.add_scatter(
        x=[best["threshold"]],
        y=[best["net_result"] / 1e6],
        mode="markers+text",
        name=t("cutoff.chart_best_name"),
        marker={"color": model_color(model, mode), "size": 12, "symbol": "diamond"},
        text=[
            t(
                "cutoff.chart_best",
                threshold=num(best["threshold"], 2),
                value=_million(best["net_result"]),
            )
        ],
        textposition="top center",
        cliponaxis=False,
    )
    fig.update_xaxes(title=t("cutoff.chart_x"), range=[0, 1])
    fig.update_yaxes(title=t("cutoff.chart_y"))
    return fig


st.title(t("cutoff.title"))
st.write(t("cutoff.intro"))
st.warning(t("cutoff.notice"))

st.subheader(t("cutoff.controls_title"))
model = st.radio(
    t("cutoff.model_label"),
    MODELS,
    key="cutoff_model",
    horizontal=True,
    format_func=lambda name: t(f"cutoff.model_{name}"),
)
threshold = st.select_slider(
    t("cutoff.threshold_label"),
    options=THRESHOLDS,
    value=DEFAULT_THRESHOLD,
    key="cutoff_threshold",
    format_func=lambda value: num(value, 2),
    help=help_text("cutoff"),
)
loss_column, margin_column = st.columns(2)
loss_share = loss_column.select_slider(
    t("cutoff.loss_label"),
    options=LOSS_SHARES,
    value=DEFAULT_LOSS_SHARE,
    key="cutoff_loss",
    format_func=lambda value: pct(value, 0),
    help=help_text("lgd"),
)
margin_share = margin_column.select_slider(
    t("cutoff.margin_label"),
    options=MARGIN_SHARES,
    value=DEFAULT_MARGIN_SHARE,
    key="cutoff_margin",
    format_func=lambda value: pct(value, 0),
    help=t("cutoff.margin_help"),
)

curve = cutoff_table(
    y_test,
    bundle[f"proba_{model}"],
    THRESHOLDS,
    loss_share,
    margin_share,
    loan_amount,
)
row = curve.iloc[THRESHOLDS.index(threshold)]

st.subheader(t("cutoff.portfolio_title"), help=help_text("confusion_matrix"))
st.write(
    t(
        "cutoff.portfolio_intro",
        n=num(len(y_test)),
        defaults=num(y_test.sum()),
        base_rate=pct(y_test.mean()),
    )
)
default_rate = row["default_rate_accepted"]
_show(
    [
        ("approval_rate", pct(row["approval_rate"]), "approval_rate"),
        ("accepted", num(row["accepted"]), "approval_rate"),
        ("rejected", num(row["rejected"]), "cutoff"),
        (
            "default_rate_accepted",
            (
                t("cutoff.none_accepted")
                if math.isnan(default_rate)
                else pct(default_rate)
            ),
            "base_rate",
        ),
    ]
)
_show(
    [
        ("caught", num(row["caught"]), "confusion_matrix"),
        ("missed", num(row["missed"]), "confusion_matrix"),
        ("rejected_good", num(row["rejected_good"]), "confusion_matrix"),
    ]
)
_show(
    [
        ("precision", pct(row["precision"]), "precision"),
        ("recall", pct(row["recall"]), "recall"),
    ]
)

best = curve.loc[curve["net_result"].idxmax()]
st.subheader(t("cutoff.money_title"), help=help_text("expected_loss"))
st.write(t("cutoff.money_intro", amount=num(loan_amount)))
_show(
    [
        ("net_result", _million(row["net_result"]), "expected_loss"),
        ("loan_amount", t("cutoff.usd", value=num(loan_amount)), "ead"),
        ("best_cutoff", num(best["threshold"], 2), "cutoff"),
        ("best_net_result", _million(best["net_result"]), "expected_loss"),
    ]
)
show_chart(_net_result_chart(model, curve, threshold, best))

st.subheader(t("cutoff.reading_title"))
st.write(t("cutoff.reading"))
