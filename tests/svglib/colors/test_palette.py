from itertools import count, product
from operator import itemgetter
from random import Random, choice, choices
from unittest import mock

import pytest
from cytoolz.itertoolz import take

from delicacy.svglib.colors.hsv import HUE_MAX, SAT_MAX, VAL_MAX
from delicacy.svglib.colors.palette import (
    EARTH,
    JEWEL,
    NEON,
    PASTEL,
    PaletteGenerator,
    analogous,
    elizabeth,
    monochromatic,
    Palettes,
    segment,
    shade,
    tint,
)
from delicacy.svglib.utils.utils import linspace


def int_linspace(*args, **kwds):
    return tuple(int(i) for i in linspace(*args, **kwds))


@pytest.mark.parametrize("num", tuple(range(5, 16, 5)))
@mock.patch("delicacy.svglib.colors.palette.Random")
class TestColorIter:
    @pytest.mark.parametrize(("hue_var", "sat_var"), ((25, 25), (30, 60)))
    def test_analogous(self, mock_rng, num, hue_var, sat_var):
        mock_rng.randint.return_value = 50

        plt = analogous(num, mock_rng, hue_var, sat_var)
        plt = tuple(plt)
        assert len(plt) == num

        hue_space = int_linspace(50 - hue_var, 50 + hue_var, num)
        sat_space = (50, 100, 50 + sat_var)

        for hue, sat, val in plt:
            assert hue in hue_space
            assert sat in sat_space
            assert val == 50

    def test_monochromatic(self, mock_rng, num):
        mock_rng.randint.return_value = 50
        mock_rng.choices = choices

        plt = monochromatic(num, mock_rng)
        assert len(tuple(plt)) == num

    def test_shade(self, mock_rng, num):
        mock_rng.randint.return_value = 50

        plt = shade(num, mock_rng)
        plt = tuple(plt)

        assert len(plt) == num

        space = int_linspace(0, 100, num)
        for _, sat, val in plt:
            assert sat == 100
            assert val in space

    def test_tint(self, mock_rng, num):
        mock_rng.randint.return_value = 50

        plt = tint(num, mock_rng)
        plt = tuple(plt)

        assert len(plt) == num

        space = int_linspace(0, 100, num)
        for _, sat, val in plt:
            assert sat in space
            assert val == 100

    @pytest.mark.parametrize(
        "n_segments",
        range(2, 5),
        ids="complementary triad square".split(),
    )
    def test_segment(self, mock_rng, num, n_segments):

        mock_rng.randint.return_value = 50
        mock_rng.choices = choices

        plt = segment(n_segments, num, mock_rng)
        plt = tuple(plt)

        hue_space = take(num, count(50, HUE_MAX // n_segments))
        hue_space = tuple(i % HUE_MAX for i in hue_space)

        for hue, sat, val in plt:
            assert hue in hue_space
            assert sat in range(70, SAT_MAX - 10)
            assert val in range(70, VAL_MAX + 1)

    @pytest.mark.parametrize("n_segments", (-1, 0))
    def test_segment_fail(self, mock_rng, num, n_segments):
        with pytest.raises(ValueError):
            tuple(segment(n_segments, num, mock_rng))

    @pytest.mark.parametrize("_range", (JEWEL, PASTEL, EARTH, NEON))
    def test_elizabeth(self, mock_rng, num, _range):
        mock_rng.choice = choice
        mock_rng.choices = choices

        sat_range, val_range = _range.values()

        plt = elizabeth(sat_range, val_range, num, mock_rng)
        plt = tuple(plt)
        assert len(plt) == num

        sats = set(itemgetter(1)(color) for color in plt)
        vals = set(itemgetter(2)(color) for color in plt)

        assert len(sats) == 1
        assert len(vals) == 1


@pytest.mark.parametrize(
    ("func", "num", "to_hex"),
    tuple(product(Palettes, range(3, 6), [True, False])),
)
class TestPaletteGenerator:
    @pytest.mark.parametrize("rng", (None, 0))
    def test_palette_gen(self, func, num, to_hex, rng):
        pgen = PaletteGenerator(func, rng)
        plt = pgen.generate(num, to_hex)

        assert len(plt) == num
        assert isinstance(plt, tuple)

    @pytest.mark.parametrize("seed", range(3))
    def test_palette_gen_reproducible(self, func, num, to_hex, seed):

        pgen0 = PaletteGenerator(func, seed)
        plt0 = pgen0.generate(num, to_hex)

        pgen1 = PaletteGenerator(func, seed)
        plt1 = pgen1.generate(num, to_hex)

        assert all(p0 == p1 for p0, p1 in zip(plt0, plt1))


def test_palette_fail():
    with pytest.raises(ValueError) as err:
        PaletteGenerator(lambda _: ..., Random(0))

    assert str(err.value) == "not a valid palette function"
