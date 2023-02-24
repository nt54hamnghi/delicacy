from math import pi

import pytest

from delicacy.svglib.elements.peripheral.point import Point


def test_create_point():
    x, y = p = Point(0, 0)
    assert x == 0
    assert y == 0
    assert isinstance(p, tuple)


@pytest.mark.parametrize(
    ("radius", "theta", "expected"),
    (
        (-1, 2 * pi, (-1, 0)),
        (1, pi, (-1, 0)),
        (2, pi / 2, (0, 2)),
        (2, pi / 4, (1, 1)),
    ),
)
def test_create_point_from_polar_radians(radius, theta, expected):
    x, y = Point.from_polar_radians(radius, theta)
    assert Point(round(x), round(y)) == Point(*expected)


@pytest.mark.parametrize(
    ("radius", "theta", "expected"),
    (
        (-1, 360, (-1, 0)),
        (1, 180, (-1, 0)),
        (2, 90, (0, 2)),
        (2, 45, (1, 1)),
    ),
)
def test_create_point_from_polar_degree(radius, theta, expected):
    x, y = Point.from_polar_degree(radius, theta)
    assert Point(round(x), round(y)) == Point(*expected)
