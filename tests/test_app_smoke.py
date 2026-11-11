"""Smoke tests of the Streamlit app with ``streamlit.testing.v1.AppTest``."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from app.ui import PAGES

ENTRY = str(Path(__file__).resolve().parents[1] / "streamlit_app.py")


@pytest.mark.parametrize("page", list(PAGES))
def test_every_page_renders_without_exception(page, bundle_env):
    at = AppTest.from_file(ENTRY, default_timeout=30).run()
    at.switch_page(PAGES[page]).run()
    assert not at.exception


def test_missing_bundle_shows_a_message_instead_of_an_exception(monkeypatch, tmp_path):
    monkeypatch.setenv("BUNDLE_PATH", str(tmp_path / "missing.joblib"))
    at = AppTest.from_file(ENTRY, default_timeout=30).run()
    assert not at.exception
    assert "scripts/build_bundle.py" in at.error[0].value


@pytest.mark.parametrize("lang", ["en", "de"])
@pytest.mark.parametrize("page", list(PAGES))
def test_every_page_renders_in_both_languages(page, lang, bundle_env):
    at = AppTest.from_file(ENTRY, default_timeout=30)
    at.query_params["lang"] = lang
    at.run()
    at.switch_page(PAGES[page]).run()
    assert not at.exception
    assert at.session_state["lang"] == lang


def test_language_switcher_changes_title_and_query_parameter(bundle_env):
    at = AppTest.from_file(ENTRY, default_timeout=30).run()
    assert at.title[0].value == "Credit risk dashboard"
    assert at.query_params["lang"] == "en"
    at.sidebar.radio(key="lang").set_value("de").run()
    assert not at.exception
    assert at.title[0].value == "Kreditrisiko-Dashboard"
    assert at.query_params["lang"] == "de"


def test_language_survives_a_page_switch(bundle_env):
    at = AppTest.from_file(ENTRY, default_timeout=30)
    at.query_params["lang"] = "de"
    at.run()
    at.switch_page(PAGES["home"]).run()
    assert at.query_params["lang"] == "de"


def test_invalid_language_in_the_url_falls_back_to_english(bundle_env):
    at = AppTest.from_file(ENTRY, default_timeout=30)
    at.query_params["lang"] = "fr"
    at.run()
    assert at.session_state["lang"] == "en"
    assert at.query_params["lang"] == "en"


def test_missing_bundle_message_is_translated(monkeypatch, tmp_path):
    monkeypatch.setenv("BUNDLE_PATH", str(tmp_path / "missing.joblib"))
    at = AppTest.from_file(ENTRY, default_timeout=30)
    at.query_params["lang"] = "de"
    at.run()
    assert at.error[0].value.startswith("Modell-Bundle nicht gefunden")
