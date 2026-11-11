"""Entry point: language, sidebar and navigation.

Start with ``streamlit run streamlit_app.py`` from the repository root.
"""

import streamlit as st

from app.ui import PAGES, get_bundle, init_language, t
from src.i18n import LANGUAGES

init_language()
st.set_page_config(page_title=t("app.title"), layout="wide")

# Fixed key: the widget owns ``st.session_state["lang"]``. A radio cannot be
# deselected, so there is never "no language".
st.sidebar.radio(
    t("common.language"),
    LANGUAGES,
    format_func=str.upper,
    horizontal=True,
    key="lang",
)
# Written on every run because Streamlit clears the query parameters on a page change.
st.query_params["lang"] = st.session_state["lang"]

bundle = get_bundle()

pages = [
    st.Page(path, title=t(f"nav.{key}"), url_path=key, default=key == "home")
    for key, path in PAGES.items()
]
# The built-in menu is drawn above all sidebar content, so it is hidden and
# drawn below the language switcher instead.
navigation = st.navigation(pages, position="hidden")
for page in pages:
    st.sidebar.page_link(page)
st.sidebar.caption(t("common.model_bundle", created_at=bundle["created_at"]))
navigation.run()
