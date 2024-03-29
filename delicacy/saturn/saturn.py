from collections.abc import Sequence
from hashlib import sha3_512
from itertools import product
from random import Random
from typing import Callable
from typing import TypeAlias
from typing import TypeVar

from bitstring import BitArray
from cytoolz.itertoolz import partition
from lxml.etree import _Element

from delicacy.saturn.helpers import fade
from delicacy.saturn.helpers import generate_id
from delicacy.saturn.helpers import make_shape
from delicacy.saturn.helpers import rand_plane
from delicacy.saturn.helpers import sorted_randspace
from delicacy.svglib.colors.palette import PaletteFunc
from delicacy.svglib.colors.palette import PaletteGenerator
from delicacy.svglib.colors.palette import PREFERRED_PALETTES
from delicacy.svglib.elements.element import WrappingElement
from delicacy.svglib.elements.peripheral.style import Fill
from delicacy.svglib.elements.peripheral.style import Stroke
from delicacy.svglib.elements.peripheral.transform import Transform
from delicacy.svglib.elements.shapes import Line
from delicacy.svglib.elements.use import Use
from delicacy.svglib.utils.utils import get_canvas
from delicacy.svglib.utils.utils import linspace

Canvas: TypeAlias = _Element
MakerFunc: TypeAlias = Callable[..., Canvas]
MakerDict: dict[str, MakerFunc] = dict()
MT = TypeVar("MT", bound=MakerFunc)


def maker(func: MT) -> MT:
    key = func.__name__.lower()
    MakerDict[key] = func
    return func


@maker
def Reah(
    width: float,
    height: float,
    colors: Sequence[str],
    rng: Random,
    x_density: int = 8,
    y_density: int = 32,
) -> Canvas:
    canvas = get_canvas(width, height)

    # proportional scale with respect to the standard frame of 512 x 512
    # so the patterns can appear nicely
    linewidth = height * 6.5 // 512

    for y in linspace(0, height, y_density):
        n_lines = rng.randint(1, x_density)
        x_space = sorted_randspace(rng, 0, width, n_lines * 2)

        for start, end in partition(2, x_space):
            stroke = Stroke(rng.choice(colors), width=linewidth, linecap="round")
            line = Line.make_line(start, y, end, y)
            line.add_style(stroke)
            canvas.append(line.base)

    return canvas


DIONE_OPTIONS = "rec tri cir xsh".split()


@maker
def Dione(
    width: float,
    height: float,
    colors: Sequence[str],
    rng: Random,
    x_density: int = 6,
    y_density: int = 12,
) -> Canvas:
    canvas = get_canvas(width, height)

    # proportional scale with respect to the standard frame of 512 x 512
    # so the patterns can appear nicely
    scale_limit = width * 12 // 512, width * 24 // 512

    for y in linspace(0, width, y_density):
        for x in sorted_randspace(rng, 0, height, x_density):
            faded = fade(
                rng=rng,
                element=make_shape(option=rng.choice(DIONE_OPTIONS)),
                color=rng.choice(colors),
                scale=rng.randint(*scale_limit) / 100,  # type: ignore
                num=rng.choice((1, 3)),
                location=(x, y),  # type: ignore
            )

            canvas.append(faded.base)

    return canvas


@maker
def Tethys(
    width: float,
    height: float,
    colors: Sequence[str],
    rng: Random,
    x_density: int = 10,
    y_density: int = 10,
) -> Canvas:
    side = min(width, height)
    canvas = get_canvas(side, side)

    # proportional scale with respect to the standard frame of 512 x 512
    # so the patterns can appear nicely
    offset, measurement = side * 20 // 512, side * 6 // 512

    _range = (offset, (side // 2) - offset)
    plane = rand_plane(
        rng, _range, _range, x_density, y_density, rate=0.6  # type: ignore
    )

    cid = generate_id(rng.getstate())
    grp = WrappingElement("g", id=cid)

    for x, y in plane:
        color = rng.choice(colors)
        option = rng.choice(("rec", "cir", "tri"))
        shape = make_shape(measurement * 2, option, x, y)
        # shape = Circle.make_circle(measurement, x, y)
        shape.apply_styles(Stroke(color), Fill(color))
        grp.append(shape)

    canvas.append(grp.base)

    flip = zip(product((0, side), repeat=2), product((1, -1), repeat=2))
    next(flip)

    for translate, scale in flip:
        use = Use(cid)
        use.add_transform(Transform().translate(*translate).scale(*scale))
        canvas.append(use.base)
    return canvas


class BackgroundMaker:
    def __init__(
        self,
        maker: MakerFunc,
        palette: PaletteFunc | None = None,
        seed: int | None = None,
    ) -> None:
        if maker not in MakerDict.values():
            raise ValueError("Not a valid maker function")
        self.maker = maker
        self.rng = Random(seed)

        palette = palette or self.rng.choice(PREFERRED_PALETTES)
        self.palette_gen = PaletteGenerator(palette, seed)

    def make(
        self, width: float = 320, height: float = 320, n_colors: int = 4
    ) -> Canvas:
        colors = self.palette_gen.generate(n_colors, to_hex=True)
        return self.maker(width, height, colors, self.rng)

    @classmethod
    def from_phrase(cls, phrase: str, maker: MakerFunc):
        if len(phrase) > 32:
            raise ValueError("Phrase length must be less than 32")

        hex = sha3_512(phrase.encode()).hexdigest()
        seed = BitArray(hex=hex).uint

        return cls(maker, seed=seed)
