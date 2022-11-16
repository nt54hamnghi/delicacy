import random
from itertools import product
from collections.abc import Iterator
from random import choice, choices, randint
from typing import cast

from cytoolz.itertoolz import partition
from lxml.etree import _Element

from delicacy.svglib.colors.palette import (
    PaletteFunc,
    PaletteGenerator,
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


def _randspace(
    start: float = 0, end: float = 512, k: int = 10, min_space: int = 10
):
    start, end = int(start), int(end)
    min_space = end // k
    yield from (
        randint(start, (start := start + min_space)) for _ in range(k)
    )


def exaid(
    width: float = 512,
    height: float = 512,
    x_density: int = 8,
    y_density: int = 32,
    palette_func: PaletteFunc = pastel,
    n_colors: int = 5,
    seed: int | None = None,
) -> _Element:

    canvas = get_canvas(width, height)
    palgen = PaletteGenerator(palette_func, seed)
    colors = tuple(c.to_hex() for c in palgen.generate(n_colors))

    for y in linspace(0, height, y_density):
        n_lines = randint(1, x_density)
        x_space = _randspace(0, width, n_lines * 2)

        for start, end in partition(2, x_space):
            line = Line.make_line(start, y, end, y)
            line.add_style(Stroke(choice(colors), width=7, linecap="round"))
            canvas.append(line.base)

    return canvas


def _fade(
    element: ExtendedElement,
    color: str,
    num: int = 3,
    location: Point = Point(0, 0),
    scale: float | None = None,
    rotate: float | None = None,
    spread: tuple[int, int] = (20, 25),
    fading_scale: float = 0.7,
) -> ExtendedElement:

    scale = randint(10, 25) / 100 if scale is None else scale
    rotate = randint(0, 360) if rotate is None else rotate % 360

    eid = str(id(element))
    defs_element = defs(group(element, id=eid))

    uses = []
    fill = Fill(color="none")
    direction = choices([-1, 1], k=2)

    width = 10.0 if num <= 1 else 20.0
    opacity = 1.0

    for i in range(num):
        distance = choices(range(*spread), k=2)
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


GENM_OPTIONS = "rec tri cir xsh".split()


def genm(
    width: float = 512,
    height: float = 512,
    x_density: int = 6,
    y_density: int = 12,
    palette_func: PaletteFunc = pastel,
    n_colors: int = 5,
    seed: int | None = None,
) -> _Element:

    canvas = get_canvas(width, height)
    palgen = PaletteGenerator(palette_func, seed)
    colors = tuple(c.to_hex() for c in palgen.generate(n_colors))

    for y in linspace(0, 512, y_density):
        for x in _randspace(0, 512, x_density):
            faded = _fade(
                _make_elm(option=choice(GENM_OPTIONS)),
                num=choice([1, 3]),
                # use tuple instead of Point to improve performance
                location=(x, y),  # type: ignore
                color=choice(colors),
            )
            canvas.append(faded.base)

    return canvas


def linplane(
    xrange: tuple[int, int] = (0, 512),
    yrange: tuple[int, int] = (0, 512),
    xk: int = 10,
    yk: int = 10,
) -> Iterator[tuple[int, int]]:
    xspace = linspace(*xrange, n_samples=xk)
    yspace = linspace(*yrange, n_samples=yk)
    result = product(xspace, yspace)
    return cast(Iterator[tuple[int, int]], result)


def randplane(
    xrange: tuple[int, int] = (0, 512),
    yrange: tuple[int, int] = (0, 512),
    xk: int = 10,
    yk: int = 10,
    rate: float = 0.2,
) -> Iterator[tuple[int, int]]:
    if not 0 < rate <= 1:
        raise ValueError("rate must be in range (0, 1]")

    plane = linplane(xrange, yrange, xk, yk)
    yield from (coord for coord in plane if random.random() < rate)


def paradx(
    side: float = 512,
    x_density: int = 10,
    y_density: int = 10,
    palette_func: PaletteFunc = pastel,
    n_colors: int = 5,
    seed: int | None = None,
) -> _Element:
    offset = 20

    canvas = get_canvas()
    palgen = PaletteGenerator(palette_func, seed)
    colors = tuple(c.to_hex() for c in palgen.generate(n_colors))

    _range = (offset, (side // 2) - offset)
    _range = cast(tuple[int, int], _range)
    plane = randplane(_range, _range, x_density, y_density, rate=0.5)

    cirs = []
    for x, y in plane:
        color = choice(colors)
        cir = Circle.make_circle(10, x, y)
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
