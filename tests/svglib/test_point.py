from math import pi
from unittest.mock import patch

import pytest

from delicacy.svglib.utils.point import (
    Point,
    rand_bounded_points,
    rand_fixed_points,
    rand_points,
)


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


def test_rand_point():
    p = Point.randpoint()
    assert 0 <= p.x <= 512
    assert 0 <= p.y <= 512


@pytest.mark.parametrize(
    ("fixed_x", "fixed_y"),
    ((True, False), (False, True), (True, True)),
    ids=("fixed x", "fixed y", "fixed both"),
)
def test_rand_point_fixed(fixed_x, fixed_y):
    x, y = Point.randpoint(
        fixed_x=fixed_x,
        fixed_y=fixed_y,
    )

    if all((fixed_x, fixed_y)):
        assert x == 0 or x == 512
        assert y == 0 or y == 512
    elif fixed_x:
        assert x == 0 or x == 512
        assert 0 <= y <= 512
    else:
        assert 0 <= x <= 512
        assert y == 0 or y == 512


@pytest.mark.parametrize("seed", tuple(range(3)))
def test_rand_points_with_seed(seed):
    xlim = ylim = (0, 512)
    first = rand_points(3, xlim, ylim, seed=seed)
    second = rand_points(3, xlim, ylim, seed=seed)

    assert list(first) == list(second)


@patch("delicacy.svglib.utils.point.random.choices")
def test_rand_bounded_points(mock_choices):
    mock_choices.return_value = [(True, True), (True, False), (False, False)]
    xlim = ylim = (0, 512)
    points = rand_bounded_points(3, xlim, ylim)

    def onbound(n, lim):
        start, end = lim
        return n == start or n == end

    x, y = next(points)
    assert onbound(x, xlim) and onbound(y, ylim)

    x, y = next(points)
    assert onbound(x, xlim) and not onbound(y, ylim)

    x, y = next(points)
    assert not onbound(x, xlim) and not onbound(y, ylim)


@pytest.mark.parametrize("seed", tuple(range(3)))
def test_rand_bounded_points_with_seed(seed):
    xlim = ylim = (0, 512)
    first = rand_bounded_points(3, xlim, ylim, seed=seed)
    second = rand_bounded_points(3, xlim, ylim, seed=seed)

    assert list(first) == list(second)


def test_rand_fixed_points():
    xlim = ylim = (0, 512)
    points = list(rand_bounded_points(3, xlim, ylim))

    def onbound(n, lim):
        start, end = lim
        return n == start or n == end

    assert all(onbound(x, xlim) or onbound(y, ylim) for x, y in points)


@pytest.mark.parametrize("seed", tuple(range(3)))
def test_rand_fixed_points_with_seed(seed):
    xlim = ylim = (0, 512)
    first = rand_fixed_points(3, xlim, ylim, seed=seed)
    second = rand_fixed_points(3, xlim, ylim, seed=seed)

    assert list(first) == list(second)
