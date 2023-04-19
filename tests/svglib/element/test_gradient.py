import pytest

from delicacy.svglib.elements.gradient import BaseGradient
from delicacy.svglib.elements.gradient import create_gradient
from delicacy.svglib.elements.gradient import LinearGradient
from delicacy.svglib.elements.gradient import RadialGradient
from delicacy.svglib.utils.utils import linspace


def test_create_base_gradient_fail():
    with pytest.raises(TypeError):
        BaseGradient("base", "pad")


@pytest.mark.parametrize(
    "id x1 y1 x2 y2 spreadMethod".split(),
    (
        ("pad-linear", 0, 0, 1, 1, "pad"),
        ("repeat-linear", 1, 1, 0, 0, "repeat"),
        ("reflect-linear", 1, 0, 1, 0, "reflect"),
    ),
)
def test_create_linear_gradient(id, x1, y1, x2, y2, spreadMethod):
    linear = LinearGradient(id, (x1, y1), (x2, y2), spreadMethod=spreadMethod)

    expected = dict(
        id=id,
        x1=f"{x1:.0%}",
        y1=f"{y1:.0%}",
        x2=f"{x2:.0%}",
        y2=f"{y2:.0%}",
        spreadMethod=spreadMethod,
    )

    assert linear.base.attrib == expected


@pytest.mark.parametrize(
    "id r cx cy fx fy spreadMethod".split(),
    (
        ("pad-radial", 0.33, 0, 0, 0, 0, "pad"),
        ("repeat-radial", 0.66, 1, 2, 3, 4, "repeat"),
        ("reflect-radial", 1, 50, 50, 100, 100, "reflect"),
    ),
)
def test_create_radial_gradient(id, r, cx, cy, fx, fy, spreadMethod):
    radial = RadialGradient(id, r, (cx, cy), (fx, fy), spreadMethod=spreadMethod)

    expected = dict(
        id=id,
        r=f"{r:.0%}",
        cx=f"{cx:.0%}",
        cy=f"{cy:.0%}",
        fx=f"{fx:.0%}",
        fy=f"{fy:.0%}",
        spreadMethod=spreadMethod,
    )

    assert radial.base.attrib == expected


def test_invalid_spreadMethod():
    with pytest.raises(ValueError):
        LinearGradient(spreadMethod="")

    with pytest.raises(ValueError):
        RadialGradient(spreadMethod="")


@pytest.mark.parametrize("gradient", (LinearGradient, RadialGradient))
def test_add_stop(gradient):
    grad = gradient()
    grad.add_stop(0, "black", 1)

    expected = {
        "offset": "0%",
        "stop-color": "black",
        "stop-opacity": "1.0",
    }

    assert len(grad.base) == 1

    child = grad.base[0]
    assert child.tag == "stop"
    assert child.attrib == expected


@pytest.mark.parametrize(
    ("offset", "opacity"),
    (
        (0.5, -1.1),
        (0.5, 1.1),
        (-1.1, 0.5),
        (1.1, 0.5),
    ),
)
def test_add_stop_fail(offset, opacity):
    with pytest.raises(ValueError):
        LinearGradient().add_stop(offset, "black", opacity)

    with pytest.raises(ValueError):
        RadialGradient().add_stop(offset, "black", opacity)


@pytest.mark.parametrize("gradient", (LinearGradient, RadialGradient))
def test_create_gradient(gradient):
    colors = ["red", "green", "blue"]
    grad = create_gradient(gradient, colors)

    assert isinstance(grad, gradient)
    assert len(grad.base) == len(colors)

    space = linspace(0, 1, len(colors))
    for i, (c, l) in enumerate(zip(colors, space)):
        expected = {
            "offset": f"{l:.0%}",
            "stop-color": c,
            "stop-opacity": "1.0",
        }

        child = grad.base[i]
        assert child.tag == "stop"
        assert child.attrib == expected
