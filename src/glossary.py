"""Glossary of the dashboard (no Streamlit import).

The entries live in the language files, ``[glossary.<key>]`` in
``src/locales/<lang>.toml``, so the parity test of ``i18n`` checks them too.
Pages and tooltips both read the texts from here, so a term has one explanation.
"""

from __future__ import annotations

from src.i18n import _texts, fmt_number, fmt_percent

#: Group ids in display order; titles are in ``[glossary_groups]``.
GROUPS = (
    "data",
    "models",
    "quality",
    "calibration",
    "explain",
    "economics",
    "regulatory",
)


def glossary_entries(lang: str) -> list[dict[str, str]]:
    """List all entries, ordered by group and, within a group, by file order.

    :param lang: Language code.
    :return: One dict per entry with its ``key`` and all fields of the file.
    """
    table = _texts(lang)["glossary"]
    entries = [{"key": key, **fields} for key, fields in table.items()]
    return sorted(entries, key=lambda entry: GROUPS.index(entry["group"]))


def glossary_help(key: str, lang: str) -> str:
    """Return the short explanation of a term, used as tooltip.

    :param key: Glossary key, e.g. ``"auc"``.
    :param lang: Language code.
    :return: The ``what`` text.
    :raises KeyError: For an unknown key.
    """
    table = _texts(lang)["glossary"]
    if key not in table:
        raise KeyError(f"missing glossary entry {key!r}")
    return table[key]["what"]


def project_figures(bundle: dict[str, object], lang: str) -> dict[str, str]:
    """Format the project values for the ``{placeholders}`` of ``in_project``.

    :param bundle: The model bundle (``metrics``, ``y_test``, ``n_train``,
        ``n_test``, ``iv_table``).
    :param lang: Language code.
    :return: Placeholder name to formatted text.
    """
    default_rate = float(bundle["y_test"].mean())
    top_iv = bundle["iv_table"].iloc[0]  # the bundle sorts it by IV, descending
    figures = {
        "default_rate": fmt_percent(default_rate, 1, lang),
        "accuracy_naive": fmt_percent(1 - default_rate, 1, lang),
        "n_train": fmt_number(bundle["n_train"], 0, lang),
        "n_test": fmt_number(bundle["n_test"], 0, lang),
        "iv_top_name": str(top_iv["name"]),
        "iv_top": fmt_number(top_iv["iv"], 2, lang),
    }
    for model in ("rf", "scorecard"):
        for name, source in (("auc", "roc_auc"), ("gini", "gini"), ("ks", "ks")):
            figures[f"{name}_{model}"] = fmt_number(
                bundle["metrics"][model][source], 3, lang
            )
    return figures
