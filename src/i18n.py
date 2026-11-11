"""Translations and number formats for the dashboard (no Streamlit import).

Texts live in ``src/locales/<lang>.toml``, one table per area. Keys use dot
notation, e.g. ``"nav.home"``.
"""

from __future__ import annotations

from functools import cache
from pathlib import Path

import tomllib

LANGUAGES = ("en", "de")
DEFAULT_LANGUAGE = "en"

#: Decimal and thousands separator for Plotly (``layout.separators``).
SEPARATORS = {"en": ".,", "de": ",."}

_LOCALES = Path(__file__).parent / "locales"
# Swap decimal point and thousands comma; the locale module is process-wide
# and therefore unsafe with several Streamlit sessions.
_DE_SWAP = str.maketrans(".,", ",.")
_NO_BREAK_SPACE = " "


@cache
def _texts(lang: str) -> dict[str, object]:
    """Read the language file once.

    :param lang: Language code.
    :return: The nested tables of the file.
    :raises KeyError: For an unknown language.
    """
    if lang not in LANGUAGES:
        raise KeyError(f"unknown language {lang!r}")
    with open(_LOCALES / f"{lang}.toml", "rb") as file:
        return tomllib.load(file)


def translate(key: str, lang: str, **values: object) -> str:
    """Look up a text and fill in its placeholders.

    There is no fallback to the other language, so a forgotten text fails
    loudly in the smoke test.

    :param key: Dot-notation key, e.g. ``"nav.home"``.
    :param lang: Language code.
    :param values: Values for the ``{name}`` placeholders.
    :return: The text.
    :raises KeyError: For an unknown key or language.
    """
    node: object = _texts(lang)
    for part in key.split("."):
        if not isinstance(node, dict) or part not in node:
            raise KeyError(f"missing text {key!r} for language {lang!r}")
        node = node[part]
    if not isinstance(node, str):
        raise KeyError(f"{key!r} is a table, not a text, for language {lang!r}")
    return node.format(**values)


def fmt_number(value: float, decimals: int, lang: str) -> str:
    """Format a number with the thousands and decimal marks of a language.

    :param value: Number.
    :param decimals: Digits after the decimal mark.
    :param lang: Language code.
    :return: ``0.717`` and ``125,381`` for ``en``, ``0,717`` and ``125.381`` for ``de``.
    """
    text = f"{value:,.{decimals}f}"
    return text.translate(_DE_SWAP) if lang == "de" else text


def fmt_percent(value: float, decimals: int, lang: str) -> str:
    """Format a share as a percentage.

    :param value: Share, e.g. ``0.216``.
    :param decimals: Digits after the decimal mark.
    :param lang: Language code.
    :return: ``21.6%`` for ``en``, ``21,6 %`` (no-break space) for ``de``.
    """
    text = fmt_number(value * 100, decimals, lang)
    return f"{text}{_NO_BREAK_SPACE}%" if lang == "de" else f"{text}%"
