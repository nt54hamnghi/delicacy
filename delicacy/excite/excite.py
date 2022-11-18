import random
from collections.abc import Sequence
from itertools import product
from random import Random
from typing import Callable, TypeAlias

from cytoolz.itertoolz import partition
from lxml.etree import _Element

from delicacy.excite.helpers import fade, make_elm, randplane, randspace
from delicacy.svglib.colors.palette import (
    PaletteFunc,
    PaletteGenerator,
    palettes,
)
from delicacy.svglib.elements.element import group
from delicacy.svglib.elements.peripheral.style import Fill, Stroke
from delicacy.svglib.elements.peripheral.transform import Transform
from delicacy.svglib.elements.shapes import Circle, Line
from delicacy.svglib.elements.use import Use
from delicacy.svglib.utils.utils import get_canvas, linspace

Canvas: TypeAlias = _Element
MakerFunc: TypeAlias = Callable[..., Canvas]

makers: list[MakerFunc] = []


def maker(func: MakerFunc) -> MakerFunc:
    makers.append(func)
    return func


@maker
def ExAid(
    width: float,
    height: float,
    colors: Sequence[str],
    rng: Random,
    x_density: int = 8,
    y_density: int = 32,
) -> Canvas:

    canvas = get_canvas(width, height)
    linewidth = height * 6.5 // 512

    for y in linspace(0, height, y_density):
        n_lines = rng.randint(1, x_density)
        x_space = randspace(rng, 0, width, n_lines * 2)

        for (start, end) in partition(2, x_space):
            stroke = Stroke(
                rng.choice(colors), width=linewidth, linecap="round"
            )
            line = Line.make_line(start, y, end, y)
            line.add_style(stroke)
            canvas.append(line.base)

    return canvas


GENM_OPTIONS = "rec tri cir xsh".split()


@maker
def Genm(
    width: float,
    height: float,
    colors: Sequence[str],
    rng: Random,
    x_density: int = 6,
    y_density: int = 12,
) -> Canvas:

    canvas = get_canvas(width, height)
    scale_limit = width * 12 // 512, width * 24 // 512

    for y in linspace(0, width, y_density):
        for x in randspace(rng, 0, height, x_density):
            faded = fade(
                rng,
                make_elm(option=rng.choice(GENM_OPTIONS)),
                num=rng.choice([1, 3]),
                scale=rng.randint(*scale_limit) / 100,  # type: ignore
                color=rng.choice(colors),
                location=(x, y),  # type: ignore
            )
            canvas.append(faded.base)

    return canvas


@maker
def ParaDX(
    width: float,
    height: float,
    colors: Sequence[str],
    rng: Random,
    x_density: int = 10,
    y_density: int = 10,
) -> Canvas:
    side = min(width, height)
    canvas = get_canvas(side, side)

    offset = side * 20 // 512
    radius = side * 6 // 512

    _range = (offset, (side // 2) - offset)
    plane = randplane(
        rng, _range, _range, x_density, y_density, rate=0.6
    )  # type: ignore

    cirs = []
    for x, y in plane:
        color = rng.choice(colors)
        cir = Circle.make_circle(radius, x, y)
        cir.apply_styles(Stroke(color), Fill(color))
        cirs.append(cir)

    cid = str(id(cirs))
    grp = group(*cirs, id=cid)

    canvas.append(grp.base)

    flip = zip(product((0, side), repeat=2), product((1, -1), repeat=2))
    next(flip)

    for translate, scale in flip:
        # mypy can't understand that __init__ is injected by attrs
        use = Use(cid)  # type: ignore
        use.add_transform(Transform().translate(*translate).scale(*scale))
        canvas.append(use.base)
    return canvas


class BGMaker:
    def __init__(
        self,
        maker: MakerFunc,
        palette: PaletteFunc | None = None,
        seed: int | None = None,
    ) -> None:
        if maker not in makers:
            raise ValueError("not a valid maker function")

        self.maker = maker

        self.rng = random if seed is None else Random(seed)
        palette = self.rng.choice(palettes) if palette is None else palette

        self.palette_gen = PaletteGenerator(palette, seed)

    def generate(
        self, width: float = 320, height: float = 320, n_colors: int = 4
    ) -> Canvas:
        colors = self.palette_gen.generate(n_colors, to_hex=True)
        return self.maker(width, height, colors, self.rng)
