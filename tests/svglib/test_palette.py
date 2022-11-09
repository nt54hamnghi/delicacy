from itertools import count, product
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
    palettes,
    segment,
    shade,
    tint,
)
from delicacy.svglib.utils.utils import linspace


def int_linspace(*args, **kwds):
    return tuple(int(i) for i in linspace(*args, **kwds))


@pytest.mark.parametrize("num", tuple(range(5, 16, 5)))
@mock.patch("delicacy.svglib.colors.palette.random.randint", return_value=50)
class TestColorIter:
    @pytest.mark.parametrize(("hue_var", "sat_var"), ((25, 25), (30, 60)))
    def test_analogous(self, mock_randint, num, hue_var, sat_var):
        plt = tuple(analogous(num, hue_var, sat_var))
        assert len(plt) == num

        hue_space = int_linspace(50 - hue_var, 50 + hue_var, num)
        sat_space = (50, 100, 50 + sat_var)

        for hue, sat, val in plt:
            assert hue in hue_space
            assert sat in sat_space
            assert val == 50

    def test_monochromatic(self, mock_randint, num):
        plt = tuple(monochromatic(num))
        assert len(plt) == num

    def test_shade(self, mock_randint, num):
        plt = tuple(shade(num))
        space = int_linspace(0, 100, num)

        assert len(plt) == num

        for _, sat, val in plt:
            assert sat == 100
            assert val in space

    def test_tint(self, mock_randint, num):
        plt = tuple(tint(num))
        space = int_linspace(0, 100, num)

        assert len(plt) == num

        for _, sat, val in plt:
            assert sat in space
            assert val == 100

    @pytest.mark.parametrize(
        "n_segments", range(2, 5), ids="complementary triad square".split()
    )
    def test_segment(self, mock_randint, num, n_segments):
        hue_space = take(num, count(50, HUE_MAX // n_segments))
        hue_space = tuple(i % HUE_MAX for i in hue_space)

        plt = tuple(segment(n_segments, num))

        for hue, sat, val in plt:
            assert hue in hue_space
            assert sat in range(70, SAT_MAX - 10)
            assert val in range(70, VAL_MAX + 1)

    @pytest.mark.parametrize("_input", (JEWEL, PASTEL, EARTH, NEON))
    def test_elizabeth(self, mock_randint, num, _input):

        sat_range, val_range = _input.values()
        plt = tuple(elizabeth(sat_range, val_range, num))
        assert len(plt) == num

        sats = set()
        vals = set()

        for _, sat, val in plt:
            sats.add(sat)
            assert sat in range(*sat_range)

            vals.add(val)
            assert val in range(*val_range)

        assert len(sats) == 1
        assert len(vals) == 1


@pytest.mark.parametrize(("func"), palettes)
def test_palette_gen(func):
    pgen = PaletteGenerator(func)
    plt = pgen.generate(5)

    assert len(plt) == 5
    assert isinstance(plt, tuple)


@pytest.mark.parametrize(("func", "seed"), list(product(palettes, range(2))))
def test_palette_gen_with_seed(func, seed):
    pgen_1 = PaletteGenerator(func, seed)
    first = pgen_1.generate(5)

    pgen_2 = PaletteGenerator(func, seed)
    second = pgen_2.generate(5)

    assert first == second


def test_palette_fail():
    with pytest.raises(ValueError) as err:
        PaletteGenerator(lambda _: ...)

    assert str(err.value) == "not a valid palette function"
