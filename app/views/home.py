"""Start page: the project in 60 seconds (problem, key figures, guide, links)."""

import streamlit as st

from app.ui import LINKS, PAGES, get_bundle, help_text, num, pct, t

bundle = get_bundle()
rf = bundle["metrics"]["rf"]

st.title(t("home.title"))
st.write(t("home.problem"))

st.subheader(t("home.metrics_title"))
tiles = [
    ("auc", num(rf["roc_auc"], 3), "metric_auc"),
    ("gini", num(rf["gini"], 3), "metric_gini"),
    ("ks", num(rf["ks"], 3), "metric_ks"),
    ("base_rate", pct(bundle["y_test"].mean()), "metric_base_rate"),
]
for column, (term, value, label) in zip(st.columns(len(tiles)), tiles):
    column.metric(t(f"home.{label}"), value, help=help_text(term), border=True)

st.warning(t("home.notice"))

st.subheader(t("home.done_title"))
for point in ("leakage", "calibration", "comparison", "explain", "limits"):
    st.markdown(f"- {t(f'home.done_{point}')}")

st.subheader(t("home.guide_title"))
# Built from PAGES, so pages added later appear here with their nav_desc text.
for key, path in PAGES.items():
    if key != "home":
        st.page_link(path, label=t(f"nav.{key}"))
        st.caption(t(f"nav_desc.{key}"))

st.subheader(t("home.links_title"))
for key, url in LINKS.items():
    st.link_button(t(f"home.link_{key}"), url)
