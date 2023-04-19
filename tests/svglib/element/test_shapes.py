from math import pi
from math import tan

import pytest
from lxml.etree import Element
from lxml.etree import tostring

from delicacy.svglib.elements.peripheral.point import Point
from delicacy.svglib.elements.shapes import Circle
from delicacy.svglib.elements.shapes import ETriangle
from delicacy.svglib.elements.shapes import Line
from delicacy.svglib.elements.shapes import Path
from delicacy.svglib.elements.shapes import Polygon
from delicacy.svglib.elements.shapes import Rectangle
from delicacy.svglib.elements.shapes import XShape
from delicacy.svglib.utils.utils import Size


def to_string(element):
    return tostring(element, pretty_print=True).decode("utf8")


def test_create_circle():
    cir = Circle(1, Point(1, 1))
    mcir = Circle.make_circle(1, 1, 1)

    expected = Element("circle", cx="1", cy="1", r="1")

    assert str(cir) == to_string(expected)
    assert str(mcir) == to_string(expected)


def test_create_line():
    line = Line(Point(1, 1), Point(1, 1))
    mline = Line.make_line(1, 1, 1, 1)

    expected = Element("line", x1="1", y1="1", x2="1", y2="1")

    assert str(line) == to_string(expected)
    assert str(mline) == to_string(expected)


def test_create_rectangle():
    rec = Rectangle(Point(1, 1), Size(120, 120))
    mrec = Rectangle.make_rectangle(1, 1, 120, 120)

    expected = Element("rect", x="1", y="1", width="120", height="120", rx="0", ry="0")

    assert str(rec) == to_string(expected)
    assert str(mrec) == to_string(expected)


def test_create_polygon():
    points = (Point(i, i) for i in range(3))
    polyg = Polygon(points)

    expected = Element("polygon", points="0,0 1,1 2,2")

    assert str(polyg) == to_string(expected)


def test_create_path():
    path = Path()
    expected = Element("path", d="")
    assert str(path) == to_string(expected)


def test_building_path():
    path = Path()
    w, x, y, z = range(4)
    rx, ry = 45, 45
    path = (
        path.M(x, y)
        .L(x, y)
        .Q(w, z, x, y)
        .C(w, z, w + 1, z + 1, x, y)
        .A(45, 45, 0, 1, 1, x, y)
        .Z()
    )

    assert isinstance(path, Path)

    expected = f"M{x},{y} L{x},{y} Q{w},{z} {x},{y} C{w},{z} {w+1},{z+1} {x},{y} A{rx},{ry} 0 1,1 {x},{y} Z"  # noqa

    assert path.d == expected


def test_building_path_relative():
    path = Path()
    w, x, y, z = range(4)
    rx, ry = 45, 45
    path = (
        path.m(x, y)
        .l(x, y)
        .q(w, z, x, y)
        .c(w, z, w + 1, z + 1, x, y)
        .a(45, 45, 0, 1, 1, x, y)
        .z()
    )

    assert isinstance(path, Path)

    expected = f"m{x},{y} l{x},{y} q{w},{z} {x},{y} c{w},{z} {w+1},{z+1} {x},{y} a{rx},{ry} 0 1,1 {x},{y} z"  # noqa

    assert path.d == expected


def test_building_path_mixed():
    path = Path()
    w, x, y, z = range(4)
    rx, ry = 45, 45
    path = (
        path.m(x, y)
        .L(x, y)
        .q(w, z, x, y)
        .C(w, z, w + 1, z + 1, x, y)
        .a(45, 45, 0, 1, 1, x, y)
        .Z()
    )

    assert isinstance(path, Path)

    expected = f"m{x},{y} L{x},{y} q{w},{z} {x},{y} C{w},{z} {w+1},{z+1} {x},{y} a{rx},{ry} 0 1,1 {x},{y} Z"  # noqa

    assert path.get("d") == expected


@pytest.mark.parametrize(
    ("location", "side"),
    (((0, 0), 30), ((1, 1), 45), ((0, 1), 60), ((1, 0), 120)),
)
def test_create_etriangle(location, side):
    half = side // 2
    point = Point(*location)
    et = ETriangle(point, side=side)
    expected = Element(
        "path",
        d=f"m{point.x},{point.y} l{side},0 l-{half},{tan(pi/3)*half} z",
    )
    assert str(et) == to_string(expected)


def test_create_etriangle_with_style():
    side = 120
    half = side // 2
    et = ETriangle(side=side, styless=False)
    expected = Element(
        "path",
        d=f"m0,0 l{side},0 l-{half},{tan(pi/3)*half} z",
        style="stroke: black; stroke-opacity: 1; stroke-width: 1; fill: none; fill-opacity: 1;",  # noqa
    )
    assert str(et) == to_string(expected)


@pytest.mark.parametrize(
    ("location", "length"),
    (((0, 0), 30), ((1, 1), 45), ((0, 1), 60), ((1, 0), 120)),
)
def test_create_xshape(location, length):
    point = Point(*location)
    x = XShape(location=point, length=length)
    expected = Element(
        "path",
        d=f"m{point.x},{point.y} l{length},{length} m{0},{-length} l{-length},{length}",  # noqa
    )
    assert str(x) == to_string(expected)


def test_create_xshape_with_style():
    length = 120
    x = XShape(length=length, styless=False)
    expected = Element(
        "path",
        d=f"m0,0 l{length},{length} m{0},{-length} l{-length},{length}",
        style="stroke: black; stroke-opacity: 1; stroke-width: 1; fill: none; fill-opacity: 1;",  # noqa
    )
    assert str(x) == to_string(expected)
