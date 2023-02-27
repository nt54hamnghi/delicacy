import random
from itertools import product, repeat
from random import Random
from unittest import mock

import pytest
from delicacy.saturn.saturn import DIONE_OPTIONS

from delicacy.saturn.helpers import (
    fade,
    linear_plane,
    make_shape,
    rand_plane,
    sorted_randspace,
    spreadit,
)
from delicacy.svglib.elements.peripheral.transform import Transform
from delicacy.svglib.elements.shapes import Circle, Path, Rectangle
from delicacy.svglib.utils.utils import linspace


@pytest.mark.parametrize(
    ("seed", "start", "stop", "k"),
    product((0, 1), (0, 32), (256, 512), range(5, 30, 10)),
)
def test_sorted_randspace(seed, start, stop, k):
    s1 = list(sorted_randspace(Random(seed), start, stop, k))
    s2 = list(sorted_randspace(Random(seed), start, stop, k))

    # reproducibility
    assert s1 == s2
    assert s1 == sorted(s1)
    assert set(s1).issubset(set(range(start, stop + 1)))


@pytest.mark.parametrize("option", DIONE_OPTIONS)
def test_make_elm(option):
    elm = make_shape(option=option)
    if option == "rec":
        assert isinstance(elm, Rectangle)
    elif option == "cir":
        assert isinstance(elm, Circle)
    else:
        assert isinstance(elm, Path)


@pytest.mark.parametrize("non_option", map(str.upper, DIONE_OPTIONS))
def test_make_elm_fail(non_option):
    with pytest.raises(ValueError):
        make_shape(option=non_option)


@pytest.mark.parametrize(
    ("x", "y", "range"),
    (
        (10, 20, (1, 256)),
        (20, 10, (2, 512)),
    ),
)
class TestPlane:
    def test_linear_plane(self, x, y, range):
        plane = tuple(linear_plane(range, range, x, y))

        assert len(plane) == x * y

    @pytest.mark.parametrize("rate", (0.25, 0.75, 1))
    def test_rand_plane_reproducible(self, x, y, range, rate):
        seed = int(rate * 100)
        args = (range, range, x, y, rate)

        first = rand_plane(Random(seed), *args)
        second = rand_plane(Random(seed), *args)

        assert all(f == s for f, s in zip(first, second))

    @pytest.mark.parametrize(
        ("random", "rate"), product((0, 0.5, 1), linspace(0.1, 1, 5))
    )
    @mock.patch("delicacy.saturn.helpers.Random")
    def test_rand_plane(self, mock_rng, x, y, range, random, rate):
        mock_rng.random.return_value = random

        plane = tuple(rand_plane(mock_rng, range, range, x, y, rate))
        expected = x * y if random < rate else 0

        assert len(plane) == expected


@pytest.mark.parametrize("rate", (-1, 0, 1.1))
def test_rand_plane_fail(rate):
    with pytest.raises(ValueError):
        tuple(rand_plane(Random(0), rate=rate))


@pytest.mark.parametrize(
    ("k", "spread"),
    (
        (2, (5, 20)),
        (4, (10, 20)),
        (6, (15, 20)),
    ),
)
class TestSpreadIt:
    @pytest.mark.parametrize(
        "direction",
        product((-1, 1), repeat=2),
    )
    @mock.patch("delicacy.saturn.helpers.Random")
    def test_spread_it(self, mock_rng, k, spread, direction):
        mock_rng.choices.side_effect = [direction] + list(
            repeat(spread, times=k)
        )
        spr = tuple(spreadit(mock_rng, spread, k))

        assert len(spr) == k

        expected = [
            (i * spread[0] * direction[0], i * spread[1] * direction[1])
            for i in range(k)
        ]

        assert tuple(expected) == spr

    @pytest.mark.parametrize("seed", range(3))
    def test_spread_it_reproducible(self, spread, k, seed):
        first = spreadit(Random(seed), spread, k)
        second = spreadit(Random(seed), spread, k)

        assert all(f == s for f, s in zip(first, second))


@pytest.mark.parametrize(
    ("option", "num", "scale", "location"),
    product(
        ("rec", "cir", "tri", "xsh"),
        range(2, 4),
        (0.2, 0.3),
        product((0, 1), repeat=2),
    ),
)
def test_fade(option, num, scale, location):
    elm = make_shape(option=option)
    faded = fade(
        random, elm, "black", scale, num=num, location=location, rotate=90
    )

    assert len(faded.base) == num + 1

    expected = Transform().translate(*location).scale(scale).rotate(90)
    assert faded.base.attrib["transform"] == expected()
