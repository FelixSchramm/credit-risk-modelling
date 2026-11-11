"""Streamlit helpers shared by all pages: bundle loading and the page list."""

from __future__ import annotations

import os
from pathlib import Path

import plotly.graph_objects as go
import streamlit as st

from src.bundle import load_bundle
from src.design import style_figure

DEFAULT_BUNDLE_PATH = (
    Path(__file__).resolve().parents[1] / "04_models" / "bundle.joblib"
)

#: All pages: key and file. Navigation, start page and smoke test read this.
PAGES = {"home": "app/views/home.py"}


@st.cache_resource
def _load(path: str) -> dict[str, object]:
    """Read the bundle once per server process, not on every interaction.

    :param path: Bundle file.
    :return: The bundle dict.
    """
    return load_bundle(path)


def get_bundle() -> dict[str, object]:
    """Load the bundle from ``BUNDLE_PATH`` or stop the app with a message.

    :return: The bundle dict.
    """
    path = Path(os.environ.get("BUNDLE_PATH", DEFAULT_BUNDLE_PATH))
    if not path.exists():
        st.error(
            f"Model bundle not found at `{path}`. Build it with "
            "`python scripts/build_bundle.py --data <raw csv>` "
            "or point `BUNDLE_PATH` to an existing file."
        )
        st.stop()
    return _load(str(path))


def current_mode() -> str:
    """Return the active theme mode, ``"dark"`` if it is unknown.

    Known limitation: after a theme change in the Streamlit menu the value
    updates only on the next rerun, so explicitly set series colours keep the
    hue of the previous mode until then. Surfaces, text and grid follow at once.

    :return: ``"light"`` or ``"dark"``.
    """
    return st.context.theme.type or "dark"


def show_chart(fig: go.Figure) -> None:
    """Style a Plotly figure with the design CI and draw it full width.

    This is the only way pages output charts.

    :param fig: Plotly figure.
    """
    st.plotly_chart(style_figure(fig), theme="streamlit", width="stretch")
