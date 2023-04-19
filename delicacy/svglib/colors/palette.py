from itertools import count
from itertools import cycle
from random import Random
from typing import Callable
from typing import Iterator
from typing import TypeAlias
from typing import TypeVar

from cytoolz import curry

from delicacy.svglib.colors.hsv import HSVColor
from delicacy.svglib.colors.hsv import HUE_MAX
from delicacy.svglib.colors.hsv import HUE_RANGE
from delicacy.svglib.colors.hsv import SAT_MAX
from delicacy.svglib.colors.hsv import SAT_MIN
from delicacy.svglib.colors.hsv import VAL_MAX
from delicacy.svglib.colors.hsv import VAL_MIN
from delicacy.svglib.utils.utils import linspace

# NOTE: use yield from in all palette functions
# to avoid seed-sharing behavior of generator expression
# https://stackoverflow.com/questions/74249443/random-seed-doesnt-work-with-generators

ColorIter: TypeAlias = Iterator[HSVColor]
PaletteFunc: TypeAlias = Callable[..., ColorIter]
Palettes: list[PaletteFunc] = []
PT = TypeVar("PT", bound=PaletteFunc)  # Palette Type Variable


def palette(func: PT) -> PT:
    Palettes.append(func)
    return func


@palette
def analogous(
    num: int,
    rng: Random,
    hue_variance: int = 25,
    sat_variance: int = 25,
) -> ColorIter:
    """Generate an analogous color scheme that consists of adjacent colors on
    the color wheel but having variant saturations and values
    """

    base_hue = rng.getrandbits(256)
    hues = linspace(base_hue - hue_variance, base_hue + hue_variance, num)

    base_sat = rng.randint(30, SAT_MAX - sat_variance)
    if (high_sat := base_sat + sat_variance) > 100:
        high_sat = SAT_MAX
    sats = cycle((base_sat, high_sat))

    val = rng.randint(50, VAL_MAX)

    yield from (HSVColor(hue, sat, val) for hue, sat in zip(hues, sats))


@palette
def monochromatic(num: int, rng: Random) -> ColorIter:
    """Generate a monochromatic color scheme that consists of same-hue colors
    but having variant saturations and values.
    """
    hue = rng.getrandbits(256)
    sats = rng.choices(range(SAT_MAX - 10), k=num)
    vals = rng.choices(range(50, VAL_MAX + 1), k=num)

    yield from (HSVColor(hue, sat, val) for sat, val in zip(sats, vals))


@palette
def shade(num: int, rng: Random) -> ColorIter:
    """Generate a shade color scheme that is
    a mixture of a dominant hue mixed with BLACK (different values)
    """

    hue = rng.getrandbits(256)
    sat = SAT_MAX
    vals = linspace(VAL_MIN, VAL_MAX, num)

    yield from (HSVColor(hue, sat, val) for val in vals)


@palette
def tint(num: int, rng: Random) -> ColorIter:
    """Generate a tint color scheme that is
    a mixture of a dominant hue mixed with WHITE (different saturations)
    """

    hue = rng.getrandbits(256)
    sats = linspace(SAT_MIN, SAT_MAX, num)
    val = VAL_MAX

    yield from (HSVColor(hue, sat, val) for sat in sats)


@curry
def segment(n_segments: int, num: int, rng: Random) -> ColorIter:
    """A curried segment function that divide the color wheel
    into segments based on the number provided.

    This is useful for creating:

        complementary (2-segment color scheme)\n
        triad (3-segment color scheme)\n
        tetradic/square (4-segment color scheme)
    """

    if not n_segments > 0:
        raise ValueError("segments count must be non-negative")

    base_hue = rng.randint(*HUE_RANGE)
    hue_step = HUE_MAX // n_segments

    hues = count(base_hue, hue_step)
    sats = rng.choices(range(70, SAT_MAX - 10), k=num)
    vals = rng.choices(range(70, VAL_MAX + 1), k=num)

    yield from (HSVColor(hue, sat, val) for hue, sat, val in zip(hues, sats, vals))


# re-assign __name__ for debugging purposes
complementary = palette(segment(2))
complementary.__name__ = "complementary"

triad = palette(segment(3))
triad.__name__ = "triad"

square = palette(segment(4))
square.__name__ = "square"


@curry
def elizabeth(
    sat_range: tuple[int, int],
    val_range: tuple[int, int],
    num: int,
    rng: Random,
) -> ColorIter:
    """
    An implementation of https://www.youtube.com/watch?v=GyVMoejbGFg
    Thanks to Elizabeth
    """

    hues = rng.choices(range(*HUE_RANGE), k=num)
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
