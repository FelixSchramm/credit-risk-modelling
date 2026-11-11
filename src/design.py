"""Design tokens and Plotly chart rules of the personal design CI.

Source: ``FelixSchramm/stock_treemap``, commit
``02a9c982127ba6a0e70cb090e9889d8dcb6e21fd`` (``ci.json`` is copied unchanged).

This module has no Streamlit import. It sets series colours and the chart
rules that do not depend on the mode. Background, font and grid colours come
from the Streamlit theme (``.streamlit/config.toml``) so that they follow the
light/dark switch at once.

Rules that cannot be enforced in code, to be kept on every page:

* no dual axes (index to 100 or use two stacked panels),
* at most seven series,
* "default / no default" is never encoded by colour alone,
* status colours only for states, never as series colours.
"""

from __future__ import annotations

import json
from pathlib import Path

import plotly.graph_objects as go

CI = json.loads((Path(__file__).parent / "ci.json").read_text(encoding="utf-8"))

#: Fixed assignment of models to slots of the categorical palette.
_MODEL_SLOTS = {"rf": 1, "scorecard": 2}


def series_color(slot: int, mode: str) -> str:
    """Return the colour of a slot of the categorical palette.

    :param slot: Slot number, 1 to 7.
    :param mode: ``"dark"`` or ``"light"``.
    :return: Hex colour.
    """
    return CI["color"]["categorical"][mode][slot - 1]["hex"]


def model_color(model: str, mode: str) -> str:
    """Return the colour that every chart uses for a model.

    :param model: ``"rf"`` (random forest) or ``"scorecard"``.
    :param mode: ``"dark"`` or ``"light"``.
    :return: Hex colour.
    :raises KeyError: For an unknown model.
    """
    return series_color(_MODEL_SLOTS[model], mode)


def style_figure(fig: go.Figure, separators: str = ".,") -> go.Figure:
    """Apply the mode-independent chart rules of the design CI in place.

    Horizontal grid lines only, left-aligned title, legend top left without
    frame, line width and bar corner radius from ``ci.json``.

    :param fig: Plotly figure.
    :param separators: Decimal and thousands separator, e.g. ``".,"``.
    :return: The same figure.
    """
    chart = CI["chart"]
    fig.update_layout(
        xaxis_showgrid=False,
        yaxis_showgrid=True,
        title_x=0,
        title_xanchor="left",
        legend={
            "orientation": "h",
            "x": 0,
            "xanchor": "left",
            "y": 1.02,
            "yanchor": "bottom",
            "borderwidth": 0,
        },
        separators=separators,
    )
    fig.update_traces(line_width=chart["line_width_px"], selector={"type": "scatter"})
    fig.update_traces(
        marker_cornerradius=chart["bar_corner_radius_px"], selector={"type": "bar"}
    )
    return fig
