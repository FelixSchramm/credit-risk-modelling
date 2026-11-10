"""Streamlit helpers shared by all pages: bundle loading and the page list."""

from __future__ import annotations

import os
from pathlib import Path

import streamlit as st

from src.bundle import load_bundle

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
