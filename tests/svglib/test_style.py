import attrs
import pytest

from delicacy.svglib.utils.style import Fill, Stroke, Style


def test_create_style():
    with pytest.raises(attrs.exceptions.NotAnAttrsClassError):
        str(Style())


def test_create_stroke_with_default():
    stroke = Stroke()
    expected = "stroke: black; stroke-opacity: 1; stroke-width: 1;"

    assert str(stroke) == expected


@pytest.mark.parametrize(
    "_input",
    (
        ("white", 0.8, 0.18, "butt", "miter"),
        ("red", 0.7, 1.8, "square", "round"),
        ("blue", 0.6, 18, "round", "bevel"),
    ),
)
def test_create_stroke(_input):
    expected = "stroke: {}; stroke-opacity: {}; stroke-width: {}; \
stroke-linecap: {}; stroke-linejoin: {};".format(
        *_input
    )  # noqa
    stroke = Stroke(*_input)
    assert str(stroke) == expected


@pytest.mark.parametrize(
    ("opacity", "style_factory"),
    (
        (-1, Stroke),
        (-1, Fill),
        (1.1, Stroke),
        (1.1, Fill),
    ),
)
def test_create_stroke_fail_opacity(opacity, style_factory):
    with pytest.raises(ValueError):
        style_factory(opacity=opacity)


@pytest.mark.parametrize("option", ("", ...), ids=["empty", "ellipse"])
def test_stroke_invalid_options_line_cap_join(option):
    with pytest.raises(ValueError):
        Stroke(linecap=option)
        Fill(rule=option)
    with pytest.raises(ValueError):
        Stroke(linejoin=option)
        Fill(rule=option)


def test_stroke_set_miter():
    stroke = Stroke(linejoin="miter", miterlimit=1)
    expected = "stroke: black; stroke-opacity: 1; stroke-width: 1;"
    expected += " stroke-linejoin: miter; stroke-miterlimit: 1;"
    assert str(stroke) == expected


def test_stroke_set_miter_fail():
    with pytest.raises(ValueError):
        Stroke(miterlimit=1)
