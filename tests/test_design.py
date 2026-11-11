"""Tests of the design tokens, the chart rules and the no-hex-code rule."""

import re
from pathlib import Path

import plotly.graph_objects as go
import pytest
import tomllib
from streamlit.testing.v1 import AppTest

from src.design import CI, model_color, series_color, style_figure

ROOT = Path(__file__).resolve().parents[1]
HEX = re.compile(r"#[0-9a-fA-F]{6}\b")


def test_ci_loads_with_expected_version():
    assert CI["meta"]["version"] == "1.3.0"


@pytest.mark.parametrize("mode", ["dark", "light"])
def test_model_colors_use_fixed_slots(mode):
    assert model_color("rf", mode) == series_color(1, mode)
    assert model_color("scorecard", mode) == series_color(2, mode)
    assert series_color(1, mode) != series_color(2, mode)


def test_unknown_model_raises_key_error():
    with pytest.raises(KeyError):
        model_color("xgboost", "dark")


def test_style_figure_sets_rules_but_no_surface_colors():
    fig = go.Figure(go.Bar(x=[1, 2], y=[3, 4]), layout={"title": "T"})
    fig.add_trace(go.Scatter(x=[1, 2], y=[3, 4]))
    style_figure(fig, separators=",.")
    assert fig.layout.xaxis.showgrid is False
    assert fig.layout.yaxis.showgrid is True
    assert fig.layout.title.x == 0
    assert fig.layout.separators == ",."
    assert fig.data[0].marker.cornerradius == CI["chart"]["bar_corner_radius_px"]
    assert fig.data[1].line.width == CI["chart"]["line_width_px"]
    assert fig.layout.paper_bgcolor is None
    assert fig.layout.plot_bgcolor is None
    assert fig.layout.font.color is None


def test_config_colors_come_from_ci():
    config = (ROOT / ".streamlit" / "config.toml").read_text(encoding="utf-8")
    ci_text = (ROOT / "src" / "ci.json").read_text(encoding="utf-8").upper()
    hexes = HEX.findall(config)
    assert hexes
    assert all(code.upper() in ci_text for code in hexes)
    assert {"light", "dark"} <= tomllib.loads(config)["theme"].keys()


def test_app_code_has_no_hex_codes():
    files = [ROOT / "streamlit_app.py", *(ROOT / "app").rglob("*.py")]
    assert len(files) > 1
    for path in files:
        assert not HEX.search(path.read_text(encoding="utf-8")), path


def test_show_chart_renders_through_the_app_code_path():
    def script():
        import plotly.graph_objects as go

        from app.ui import show_chart

        show_chart(go.Figure(go.Bar(x=[1, 2], y=[3, 4])))

    at = AppTest.from_function(script, default_timeout=30).run()
    assert not at.exception
