"""Entry point: loads the bundle, draws the sidebar and runs the navigation.

Start with ``streamlit run streamlit_app.py`` from the repository root.
"""

import streamlit as st

from app.ui import PAGES, get_bundle

st.set_page_config(page_title="Credit risk dashboard", layout="wide")

bundle = get_bundle()
st.sidebar.caption(f"Model bundle from {bundle['created_at']}")

pages = [
    st.Page(path, title=key.capitalize(), url_path=key, default=key == "home")
    for key, path in PAGES.items()
]
st.navigation(pages).run()
