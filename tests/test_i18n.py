"""Tests of the language files, ``translate`` and the number formats."""

import re
from pathlib import Path

import pytest
import tomllib

from src.i18n import LANGUAGES, SEPARATORS, fmt_number, fmt_percent, translate

LOCALES = Path(__file__).resolve().parents[1] / "src" / "locales"
PLACEHOLDER = re.compile(r"\{(\w+)\}")


def _flatten(table: dict, prefix: str = "") -> dict[str, str]:
    """Flatten nested tables to dot-notation keys."""
    flat = {}
    for name, value in table.items():
        if isinstance(value, dict):
            flat.update(_flatten(value, f"{prefix}{name}."))
        else:
            flat[f"{prefix}{name}"] = value
    return flat


@pytest.fixture(scope="module")
def texts() -> dict[str, dict[str, str]]:
    """All texts per language, flattened."""
    return {
        lang: _flatten(tomllib.loads((LOCALES / f"{lang}.toml").read_text("utf-8")))
        for lang in LANGUAGES
    }


def test_languages_have_the_same_keys(texts):
    assert set(texts["en"]) == set(texts["de"])


def test_no_text_is_empty(texts):
    for lang, flat in texts.items():
        assert all(isinstance(v, str) and v.strip() for v in flat.values()), lang


def test_placeholders_are_the_same_in_both_languages(texts):
    for key, text in texts["en"].items():
        assert set(PLACEHOLDER.findall(text)) == set(
            PLACEHOLDER.findall(texts["de"][key])
        ), key


def test_translate_fills_placeholders():
    assert translate("common.model_bundle", "de", created_at="X") == (
        "Modell-Bundle vom X"
    )


@pytest.mark.parametrize(
    "key, lang", [("nav.nope", "en"), ("nope", "de"), ("nav", "en"), ("nav.home", "fr")]
)
def test_translate_raises_key_error(key, lang):
    with pytest.raises(KeyError):
        translate(key, lang)


def test_key_error_names_key_and_language():
    with pytest.raises(KeyError, match="nav.nope.*de"):
        translate("nav.nope", "de")


def test_fmt_number():
    assert fmt_number(0.7168, 3, "en") == "0.717"
    assert fmt_number(125381, 0, "en") == "125,381"
    assert fmt_number(0.7168, 3, "de") == "0,717"
    assert fmt_number(125381, 0, "de") == "125.381"
    assert fmt_number(1234567.5, 1, "de") == "1.234.567,5"


def test_fmt_percent():
    assert fmt_percent(0.216, 1, "en") == "21.6%"
    assert fmt_percent(0.216, 1, "de") == "21,6 %"


def test_plotly_separators():
    assert SEPARATORS == {"en": ".,", "de": ",."}
