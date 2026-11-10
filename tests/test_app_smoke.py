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
