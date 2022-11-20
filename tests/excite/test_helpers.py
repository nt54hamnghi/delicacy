import random
from itertools import product, repeat
from random import Random
from unittest import mock

import pytest

from delicacy.excite.helpers import (
    fade,
    linear_plane,
    make_elm,
    rand_plane,
    sorted_randspace,
    spreadit,
)
from delicacy.svglib.elements.peripheral.transform import Transform
from delicacy.svglib.elements.shapes import Circle, Path, Rectangle


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


@pytest.mark.parametrize("option", "rec tri cir xsh".split())
def test_make_elm(option):
    elm = make_elm(option=option)
    if option == "rec":
        assert isinstance(elm, Rectangle)
    elif option == "cir":
        assert isinstance(elm, Circle)
    else:
        assert isinstance(elm, Path)


def test_make_elm_fail():
    with pytest.raises(ValueError):
        make_elm(option="")


@pytest.mark.parametrize(
    ("k", "_range"),
    tuple(
        product(
            (10, 20),
            product(
                map(lambda x: pow(2, x), range(2)),
                map(lambda x: pow(2, x), range(8, 10)),
            ),
        )
    ),
)
class TestPlane:
    def test_linear_plane(self, k, _range):
        plane = linear_plane(_range, _range, k, k * 2)
        plane = tuple(plane)

        assert len(plane) == k * k * 2

    @pytest.mark.parametrize("random_returned", (0, 1))
    @mock.patch("delicacy.excite.helpers.Random")
    def test_rand_plane(self, mock_rng, k, _range, random_returned):
        mock_rng.random.return_value = random_returned
        plane = rand_plane(mock_rng, _range, _range, k, k * 2, 0.5)
        plane = tuple(plane)

        expected = k * k * 2

        if random_returned == 0:
            expected *= 1
        elif random_returned == 1:
            expected *= 0

        assert len(plane) == expected

    @pytest.mark.parametrize("rate", (0.25, 0.75, 1))
    def test_rand_plane_reproducible(self, k, _range, rate):
        seed = int(rate * 100)
        plane0 = rand_plane(Random(seed), _range, _range, k, k * 2, rate)
        plane1 = rand_plane(Random(seed), _range, _range, k, k * 2, rate)

        assert all(p0 == p1 for p0, p1 in zip(plane0, plane1))


@pytest.mark.parametrize("rate", (-1, 0, 1.1))
def test_rand_plane_fail(rate):
    with pytest.raises(ValueError):
        tuple(rand_plane(Random(0), rate=rate))


@pytest.mark.parametrize(
    ("k", "spread"),
    tuple(
        product(
            range(2, 4),
            ((5, 20), (10, 20), (15, 20)),
        ),
    ),
)
class TestSpreadIt:
    @pytest.mark.parametrize(
        "direction",
        tuple(product((-1, 1), repeat=2)),
    )
    @mock.patch("delicacy.excite.helpers.Random")
    def test_spread_it(self, mock_rng, k, spread, direction):
        mock_rng.choices.side_effect = [direction] + list(
            repeat(spread, times=k)
        )
        spr = spreadit(mock_rng, spread, k)
        spr = tuple(spr)

        assert len(spr) == k

        expected = [
            (i * spread[0] * direction[0], i * spread[1] * direction[1])
            for i in range(k)
        ]

        assert tuple(expected) == spr

    @pytest.mark.parametrize("seed", range(3))
    def test_spread_it_reproducible(self, spread, k, seed):
        spr0 = spreadit(Random(seed), spread, k)
        spr1 = spreadit(Random(seed), spread, k)

        assert all(s0 == s1 for s0, s1 in zip(spr0, spr1))


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
    elm = make_elm(option=option)
    faded = fade(
        random, elm, "black", scale, num=num, location=location, rotate=90
    )

    assert len(faded.base) == num + 1

    expected = Transform().translate(*location).scale(scale).rotate(90)
    assert faded.base.attrib["transform"] == expected()
