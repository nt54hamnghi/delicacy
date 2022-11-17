import random
from collections.abc import Iterator
from itertools import product
from random import Random
from typing import Callable, TypeAlias, cast

from cytoolz.itertoolz import partition
from lxml.etree import _Element

from delicacy.svglib.colors.palette import (
    PaletteFunc,
    PaletteGenerator,
    palettes,
    pastel,
)
from delicacy.svglib.elements.element import ExtendedElement, defs, group
from delicacy.svglib.elements.peripheral.point import Point
from delicacy.svglib.elements.peripheral.style import Fill, Stroke
from delicacy.svglib.elements.peripheral.transform import Transform
from delicacy.svglib.elements.shapes import (
    Circle,
    ETriangle,
    Line,
    Rectangle,
    XShape,
)
from delicacy.svglib.elements.use import Use
from delicacy.svglib.utils.utils import get_canvas, linspace

PALETTES = tuple(palettes)

Canvas: TypeAlias = _Element
MakerFunc: TypeAlias = Callable[..., Canvas]

MAKERS: set[MakerFunc] = set()


def maker(func: MakerFunc) -> MakerFunc:
    MAKERS.add(func)
    return func


def _randspace(
    rng: Random, start: float = 0, end: float = 512, k: int = 10
) -> Iterator[int]:

    start, end = int(start), int(end)
    min_space = end // k
    yield from (
        rng.randint(start, (start := start + min_space)) for _ in range(k)
    )


@maker
def ExAid(
    width: float = 512,
    height: float = 512,
    x_density: int = 8,
    y_density: int = 32,
    palette_func: PaletteFunc | None = None,
    n_colors: int = 5,
    seed: int | None = None,
) -> Canvas:
    rng = random if seed is None else Random(seed)

    linewidth = height * 6.5 // 512

    canvas = get_canvas(width, height)
    palette_func = (
        rng.choice(PALETTES) if palette_func is None else palette_func
    )
    palgen = PaletteGenerator(palette_func, rng)
    colors = tuple(c.to_hex() for c in palgen.generate(n_colors))

    for y in linspace(0, height, y_density):
        n_lines = rng.randint(1, x_density)
        x_space = _randspace(rng, 0, width, n_lines * 2)

        for start, end in partition(2, x_space):
            line = Line.make_line(start, y, end, y)
            line.add_style(
                Stroke(rng.choice(colors), width=linewidth, linecap="round")
            )
            canvas.append(line.base)

    return canvas


def _fade(
    rng: Random,
    element: ExtendedElement,
    color: str,
    num: int = 3,
    location: Point = Point(0, 0),
    scale: float | None = None,
    rotate: float | None = None,
    spread: tuple[int, int] = (20, 25),
    fading_scale: float = 0.7,
) -> ExtendedElement:

    scale = rng.randint(15, 25) / 100 if scale is None else scale
    rotate = rng.randint(0, 360) if rotate is None else rotate % 360

    eid = str(id(element))
    defs_element = defs(group(element, id=eid))

    uses = []
    fill = Fill(color="none")
    direction = rng.choices([-1, 1], k=2)

    width = 10.0 if num <= 1 else 20.0
    opacity = 1.0

    for i in range(num):
        distance = rng.choices(range(*spread), k=2)
        new_location = ((i * ds * dr) for ds, dr in zip(distance, direction))

        # mypy can't understand that __init__ is injected by attrs
        use = Use(eid, new_location)  # type: ignore
        use.apply_styles(Stroke(color, opacity, width), fill)

        width *= fading_scale
        opacity *= fading_scale

        uses.append(use)

    faded = group(defs_element, *uses)
    transform = Transform().translate(*location).scale(scale).rotate(rotate)
    faded.add_transform(transform)

    return faded


GENM_OPTIONS = "rec tri cir xsh".split()


@maker
def Genm(
    width: float = 512,
    height: float = 512,
    x_density: int = 6,
    y_density: int = 12,
    palette_func: PaletteFunc | None = None,
    n_colors: int = 5,
    seed: int | None = None,
) -> Canvas:
    rng = random if seed is None else Random(seed)

    canvas = get_canvas(width, height)
    palette_func = (
        rng.choice(PALETTES) if palette_func is None else palette_func
    )
    palgen = PaletteGenerator(palette_func, rng)
    colors = tuple(c.to_hex() for c in palgen.generate(n_colors))
    scale_limit = width * 12 // 512, width * 24 // 512

    for y in linspace(0, width, y_density):
        for x in _randspace(rng, 0, height, x_density):
            faded = _fade(
                rng,
                _make_elm(option=rng.choice(GENM_OPTIONS)),
                num=rng.choice([1, 3]),
                scale=rng.randint(*scale_limit) / 100,  # type: ignore
                color=rng.choice(colors),
                location=(x, y),  # type: ignore
            )
            canvas.append(faded.base)

    return canvas


def _make_elm(side: int = 120, option: str = "rec") -> ExtendedElement:
    match option:  # noqa
        case "rec":
            return Rectangle.make_rectangle(0, 0, side, side)
        case "tri":
            return ETriangle(side=side)
        case "cir":
            return Circle.make_circle(side // 2, 0, 0)
        case "xsh":
            return XShape(length=side)
        case _:
            raise ValueError(
                f'option: {option} is not one of "rec", "tri", "cir", "xsh"'
            )


def _linplane(
    xrange: tuple[int, int] = (0, 512),
    yrange: tuple[int, int] = (0, 512),
    xk: int = 10,
    yk: int = 10,
) -> Iterator[tuple[int, int]]:
    """a linear plane: a cartisan product of 2 linear spaces"""
    xspace = linspace(*xrange, n_samples=xk)
    yspace = linspace(*yrange, n_samples=yk)
    result = product(xspace, yspace)
    return cast(Iterator[tuple[int, int]], result)


def _randplane(
    rng: Random,
    xrange: tuple[int, int] = (0, 512),
    yrange: tuple[int, int] = (0, 512),
    xk: int = 10,
    yk: int = 10,
    rate: float = 0.2,
) -> Iterator[int]:

    """randomly dropping points from a linear plane"""
    if not 0 < rate <= 1:
        raise ValueError("rate must be in range (0, 1]")

    plane = _linplane(xrange, yrange, xk, yk)
    yield from (coord for coord in plane if rng.random() < rate)


@maker
def ParaDX(
    side: float = 512,
    x_density: int = 9,
    y_density: int = 9,
    palette_func: PaletteFunc | None = None,
    n_colors: int = 5,
    seed: int | None = None,
) -> Canvas:
    rng = random if seed is None else Random(seed)

    offset = side * 20 // 512
    radius = side * 7 // 512

    canvas = get_canvas(side, side)
    palette_func = (
        rng.choice(PALETTES) if palette_func is None else palette_func
    )
    palgen = PaletteGenerator(palette_func, rng)
    colors = tuple(c.to_hex() for c in palgen.generate(n_colors))

    _range = (offset, (side // 2) - offset)
    _range = cast(tuple[int, int], _range)
    plane = _randplane(rng, _range, _range, x_density, y_density, rate=0.5)

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
