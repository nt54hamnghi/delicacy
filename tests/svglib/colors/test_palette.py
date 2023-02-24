from itertools import count, product, repeat
from operator import mod
from random import Random, choice, choices
from unittest import mock

import pytest
from cytoolz.functoolz import identity
from cytoolz.itertoolz import take

from delicacy.svglib.colors.hsv import HUE_MAX, SAT_MAX, SAT_MIN, VAL_MAX
from delicacy.svglib.colors.palette import (
    EARTH,
    JEWEL,
    NEON,
    PASTEL,
    PaletteGenerator,
    Palettes,
    analogous,
    elizabeth,
    monochromatic,
    segment,
    shade,
    tint,
)
from delicacy.svglib.utils.utils import linspace


def int_linspace(*args, **kwds):
    return tuple(int(i) for i in linspace(*args, **kwds))


# mocked returned value for random.randint
RANDINT = 50


@pytest.mark.parametrize("num", tuple(range(5, 16, 5)))
@mock.patch("delicacy.svglib.colors.palette.Random")
class TestColorIter:
    @pytest.mark.parametrize(("hue_var", "sat_var"), ((25, 25), (30, 60)))
    def test_analogous(self, mock_rng, num, hue_var, sat_var):
        mock_rng.randint.return_value = RANDINT

        palette = tuple(analogous(num, mock_rng, hue_var, sat_var))
        assert len(palette) == num

        hue_space = int_linspace(RANDINT - hue_var, RANDINT + hue_var, num)
        sat_space = (RANDINT, SAT_MAX, RANDINT + sat_var)

        for hue, sat, val in palette:
            assert hue in hue_space
            assert sat in sat_space
            assert val == RANDINT

    def test_monochromatic(self, mock_rng, num):
        _range = range(RANDINT, RANDINT + num)
        mock_rng.randint.return_value = RANDINT
        mock_rng.choices.return_value = _range

        plt = tuple(monochromatic(num, mock_rng))
        assert len(plt) == num

        for hue, sat, val in plt:
            assert hue == RANDINT
            assert sat in _range
            assert val in _range

    def test_shade(self, mock_rng, num):
        mock_rng.randint.return_value = RANDINT

        plt = tuple(shade(num, mock_rng))
        assert len(plt) == num

        val_space = int_linspace(0, VAL_MAX, num)
        for hue, sat, val in plt:
            assert hue == RANDINT
            assert sat == SAT_MAX
            assert val in val_space

    def test_tint(self, mock_rng, num):
        mock_rng.randint.return_value = RANDINT

        plt = tint(num, mock_rng)
        plt = tuple(plt)

        assert len(plt) == num

        sat_space = int_linspace(SAT_MIN, SAT_MAX, num)
        for hue, sat, val in plt:
            assert hue == RANDINT
            assert sat in sat_space
            assert val == VAL_MAX

    @pytest.mark.parametrize(
        "n_segments",
        range(2, 5),
        ids="complementary triad square".split(),
    )
    def test_segment(self, mock_rng, num, n_segments):

        mock_rng.randint.return_value = RANDINT
        mock_rng.choices = choices

        plt = tuple(segment(n_segments, num, mock_rng))

        hue_space = take(num, count(RANDINT, HUE_MAX // n_segments))
        hue_space = tuple(map(mod, hue_space, repeat(HUE_MAX)))

        for hue, sat, val in plt:
            assert hue in hue_space
            assert sat in range(70, SAT_MAX - 10)
            assert val in range(70, VAL_MAX + 1)

    @pytest.mark.parametrize("n_segments", (-1, 0))
    def test_segment_fail(self, mock_rng, num, n_segments):
        with pytest.raises(ValueError):
            tuple(segment(n_segments, num, mock_rng))

    @pytest.mark.parametrize("constants", (JEWEL, PASTEL, EARTH, NEON))
    def test_elizabeth(self, mock_rng, num, constants):
        mock_rng.choice = choice
        mock_rng.choices = choices

        sat_range, val_range = constants.values()

        plt = tuple(elizabeth(sat_range, val_range, num, mock_rng))
        assert len(plt) == num

        sats = set(color.sat for color in plt)
        vals = set(color.val for color in plt)

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
        PaletteGenerator(identity, Random(0))

    assert str(err.value) == "not a valid palette function"
