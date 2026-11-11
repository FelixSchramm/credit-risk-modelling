"""Streamlit helpers shared by all pages: bundle, page list, texts and numbers.

Rules for every page: all visible text goes through ``t()``, all numbers
through ``num()`` and ``pct()``, and every input widget gets a fixed ``key=``.
Without a key a widget is recreated when the language changes (its label
changes) and loses its value.
"""

from __future__ import annotations

import os
from pathlib import Path

import plotly.graph_objects as go
import streamlit as st

from src.bundle import load_bundle
from src.design import style_figure
from src.glossary import glossary_help
from src.i18n import (
    DEFAULT_LANGUAGE,
    LANGUAGES,
    SEPARATORS,
    fmt_number,
    fmt_percent,
    translate,
)

DEFAULT_BUNDLE_PATH = (
    Path(__file__).resolve().parents[1] / "04_models" / "bundle.joblib"
)

#: All pages: key and file. Navigation, start page and smoke test read this.
PAGES = {"home": "app/views/home.py", "glossary": "app/views/glossary.py"}


@st.cache_resource
def _load(path: str) -> dict[str, object]:
    """Read the bundle once per server process, not on every interaction.

    :param path: Bundle file.
    :return: The bundle dict.
    """
    return load_bundle(path)


def init_language() -> None:
    """Set the language on the first run of a session.

    Taken from the ``lang`` query parameter if valid, else the default. Later
    runs keep the value in ``st.session_state`` (the switcher widget owns it),
    because query parameters are cleared when the user changes the page.
    """
    if "lang" not in st.session_state:
        requested = st.query_params.get("lang")
        st.session_state["lang"] = (
            requested if requested in LANGUAGES else DEFAULT_LANGUAGE
        )


def current_lang() -> str:
    """Return the language of this session.

    :return: ``"en"`` or ``"de"``.
    """
    init_language()
    return st.session_state["lang"]


def t(key: str, **values: object) -> str:
    """Translate a key into the current language.

    :param key: Dot-notation key, e.g. ``"nav.home"``.
    :param values: Values for the ``{name}`` placeholders.
    :return: The text.
    """
    return translate(key, current_lang(), **values)


def num(value: float, decimals: int = 0) -> str:
    """Format a number in the current language.

    :param value: Number.
    :param decimals: Digits after the decimal mark.
    :return: The formatted number.
    """
    return fmt_number(value, decimals, current_lang())


def pct(value: float, decimals: int = 1) -> str:
    """Format a share as a percentage in the current language.

    :param value: Share, e.g. ``0.216``.
    :param decimals: Digits after the decimal mark.
    :return: The formatted percentage.
    """
    return fmt_percent(value, decimals, current_lang())


def help_text(key: str) -> str:
    """Return the glossary tooltip of a term in the current language.

    Use it as ``st.metric(..., help=help_text("auc"))``. An unknown key raises
    ``KeyError``, so the smoke test finds a figure without a glossary entry.

    :param key: Glossary key, e.g. ``"auc"``.
    :return: The short explanation.
    """
    return glossary_help(key, current_lang())


def get_bundle() -> dict[str, object]:
    """Load the bundle from ``BUNDLE_PATH`` or stop the app with a message.

    :return: The bundle dict.
    """
    path = Path(os.environ.get("BUNDLE_PATH", DEFAULT_BUNDLE_PATH))
    if not path.exists():
        st.error(t("common.bundle_missing", path=path))
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

    This is the only way pages output charts. Axis numbers follow the language.

    :param fig: Plotly figure.
    """
    st.plotly_chart(
        style_figure(fig, SEPARATORS[current_lang()]),
        theme="streamlit",
        width="stretch",
    )
