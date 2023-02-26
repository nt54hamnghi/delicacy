from itertools import product
import pytest

from delicacy.svglib.elements.peripheral.style import Fill, Stroke, Style


def test_create_stroke_with_default():
    stroke = Stroke()
    expected = "stroke: black; stroke-opacity: 1; stroke-width: 1;"

    assert str(stroke) == expected


def test_style_to_dict():
    stroke = Stroke()
    expected = {"stroke": "black", "stroke-opacity": 1, "stroke-width": 1}
    assert stroke.to_dict() == expected


@pytest.mark.parametrize(
    "args",
    (
        ("red", 0.25, 0.25, "butt"),
        ("green", 0.5, 2.5, "square"),
        ("blue", 0.75, 25, "round"),
    ),
)
def test_create_stroke(args):
    expected = "stroke: {}; stroke-opacity: {}; stroke-width: {}; stroke-linecap: {};".format(
        *args
    )  # noqa
    stroke = Stroke(*args)
    assert str(stroke) == expected


@pytest.fixture
def style_str():
    stroke, fill = Stroke(), Fill()
    return f"{stroke} {fill}"


def test_parse_style(style_str):
    extracted = Style.parse(style_str)
    expected = Stroke().to_dict() | Fill().to_dict()

    assert extracted == expected


@pytest.mark.parametrize(
    "filter_by",
    ("stroke", "Stroke"),
)
def test_parse_style_filter_by_stroke(filter_by, style_str):
    extracted = Style.parse(style_str, filter_by)
    expected = Stroke().to_dict()

    assert extracted == expected


@pytest.mark.parametrize(
    "filter_by",
    ("fill", "Fill"),
)
def test_parse_style_filter_by_fill(filter_by, style_str):
    extracted = Style.parse(style_str, filter_by)
    expected = Fill().to_dict()

    assert extracted == expected


@pytest.mark.parametrize(
    ("opacity", "style"),
    (product((-1, 1.1), (Stroke, Fill))),
)
def test_stroke_fill_invalid_opacity(opacity, style):
    with pytest.raises(ValueError):
        style(opacity=opacity)


@pytest.mark.parametrize("option", ("", ...), ids=["empty", "ellipse"])
class TestInvalidOption:
    def test_stroke_invalid_line_cap(self, option):
        with pytest.raises(ValueError):
            Stroke(linecap=option)

    def test_fill_invalid_rule(self, option):
        with pytest.raises(ValueError):
            Fill(rule=option)
