from itertools import count, cycle
from random import Random
from typing import Callable, Iterator, TypeAlias

from cytoolz import curry

from delicacy.svglib.colors.hsv import (
    HUE_MAX,
    HUE_RANGE,
    SAT_MAX,
    VAL_MAX,
    HSVColor,
)
from delicacy.svglib.utils.utils import linspace

# NOTE: use yield from in all palette functions
# to avoid seed-sharing behavior of generator expression
# https://stackoverflow.com/questions/74249443/random-seed-doesnt-work-with-generators

ColorIter: TypeAlias = Iterator[HSVColor]
PaletteFunc: TypeAlias = Callable[..., ColorIter]
Palettes: list[PaletteFunc] = []


def palette(func: PaletteFunc) -> PaletteFunc:
    Palettes.append(func)
    return func


@palette
def analogous(
    num: int,
    rng: Random,
    hue_variance: int = 25,
    sat_variance: int = 25,
) -> ColorIter:

    base_hue = rng.randint(*HUE_RANGE)
    hues = linspace(base_hue - hue_variance, base_hue + hue_variance, num)

    base_sat = rng.randint(30, SAT_MAX - sat_variance)

    if (high_sat := base_sat + sat_variance) > 100:
        high_sat = SAT_MAX

    sats = cycle((base_sat, high_sat))

    val = rng.randint(50, VAL_MAX)

    yield from (HSVColor(hue, sat, val) for hue, sat in zip(hues, sats))


@palette
def monochromatic(num: int, rng: Random) -> ColorIter:

    hue = rng.randint(*HUE_RANGE)
    sats = rng.choices(range(SAT_MAX - 10), k=num)
    vals = rng.choices(range(50, VAL_MAX + 1), k=num)

    yield from (HSVColor(hue, sat, val) for sat, val in zip(sats, vals))


@palette
def shade(num: int, rng: Random) -> ColorIter:

    hue = rng.randint(*HUE_RANGE)
    sat = 100
    vals = linspace(0, 100, num)

    yield from (HSVColor(hue, sat, val) for val in vals)


@palette
def tint(num: int, rng: Random) -> ColorIter:

    hue = rng.randint(*HUE_RANGE)
    sats = linspace(0, 100, num)
    val = 100

    yield from (HSVColor(hue, sat, val) for sat in sats)


@curry
def segment(n_segments: int, num: int, rng: Random) -> ColorIter:
    if not n_segments > 0:
        raise ValueError("segments count must be non-negative")

    base_hue = rng.randint(*HUE_RANGE)
    hue_step = HUE_MAX // n_segments

    hues = count(base_hue, hue_step)
    sats = rng.choices(range(70, SAT_MAX - 10), k=num)
    vals = rng.choices(range(70, VAL_MAX + 1), k=num)

    yield from (
        HSVColor(hue, sat, val) for hue, sat, val in zip(hues, sats, vals)
    )


# re-assign __name__ for debugging purposes
complementary = palette(segment(2))
complementary.__name__ = "complementary"

triad = palette(segment(3))
triad.__name__ = "triad"

square = palette(segment(4))
square.__name__ = "square"


# the below function and its curried versions is an implementation of
# https://www.youtube.com/watch?v=GyVMoejbGFg
@curry
def elizabeth(
    sat_range: tuple[int, int],
    val_range: tuple[int, int],
    num: int,
    rng: Random,
) -> ColorIter:

    hues = sorted(rng.choices(range(*HUE_RANGE), k=num))
    sat = rng.choice(range(*sat_range))
    val = rng.choice(range(*val_range))

    yield from (HSVColor(hue, sat, val) for hue in hues)


JEWEL = dict(sat_range=(73, 83), val_range=(56, 76))
jewel = palette(elizabeth(**JEWEL))
jewel.__name__ = "jewel"

PASTEL = dict(sat_range=(25, 35), val_range=(85, 92))
pastel = palette(elizabeth(**PASTEL))
pastel.__name__ = "pastel"

EARTH = dict(sat_range=(36, 41), val_range=(36, 77))
earth = palette(elizabeth(**EARTH))
earth.__name__ = "earth"

NEON = dict(sat_range=(63, 100), val_range=(82, 100))
neon = palette(elizabeth(**NEON))
neon.__name__ = "neon"


PREFERRED_PALETTES = (analogous, tint, shade, square, jewel, pastel, neon)


class PaletteGenerator:
    def __init__(self, palette: PaletteFunc, seed: int | None = None) -> None:
        if palette not in Palettes:
            raise ValueError("not a valid palette function")
        self.palette = palette
        self.rng = Random(seed)

    def generate(
        self, num: int = 5, to_hex: bool = False, *args, **kwds
    ) -> tuple[HSVColor | str, ...]:
        colors = self.palette(num=num, rng=self.rng, *args, **kwds)
        if to_hex:
            return tuple(c.to_hex() for c in colors)
        return tuple(colors)
