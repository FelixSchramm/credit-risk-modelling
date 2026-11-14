"""Glossary page: searchable, grouped, one expander per term."""

import streamlit as st

from app.ui import current_lang, get_bundle, t
from src.glossary import GROUPS, glossary_entries, project_figures

README_REGULATORY = (
    "https://github.com/FelixSchramm/credit-risk-modelling#regulatory-context"
)
# Order of the parts inside an entry; the formula follows at the end.
PARTS = ("what", "how_to_read", "in_project", "limit")

lang = current_lang()
figures = project_figures(get_bundle(), lang)

st.title(t("glossary_page.title"))
st.write(t("glossary_page.intro"))
query = st.text_input(t("glossary_page.search"), key="glossary_search").strip().lower()

matching = [
    entry
    for entry in glossary_entries(lang)
    if query in " ".join(entry.get(f, "") for f in ("term", *PARTS)).lower()
]
shown = 0
for group in GROUPS:
    entries = [entry for entry in matching if entry["group"] == group]
    if not entries:
        continue
    st.subheader(t(f"glossary_groups.{group}"))
    for entry in entries:
        with st.expander(entry["term"]):
            for part in PARTS:
                if part in entry:
                    text = entry[part]
                    if part == "in_project":
                        text = text.format(**figures)
                    st.markdown(f"**{t(f'glossary_page.{part}')}**  \n{text}")
            if "formula" in entry:
                st.latex(entry["formula"])
            if group == "regulatory":
                st.markdown(
                    f"[{t('glossary_page.regulatory_link')}]({README_REGULATORY})"
                )
    shown += len(entries)

if not shown:
    st.info(t("glossary_page.no_results"))
