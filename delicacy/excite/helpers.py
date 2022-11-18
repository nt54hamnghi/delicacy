from collections.abc import Iterator
from itertools import product
from random import Random

from delicacy.svglib.elements.element import ExtendedElement, defs, group
from delicacy.svglib.elements.peripheral.point import Point
from delicacy.svglib.elements.peripheral.style import Fill, Stroke
from delicacy.svglib.elements.peripheral.transform import Transform
from delicacy.svglib.elements.shapes import (
    Circle,
    ETriangle,
    Rectangle,
    XShape,
)
from delicacy.svglib.elements.use import Use
from delicacy.svglib.utils.utils import linspace


def randspace(
    rng: Random, start: float = 0, end: float = 512, k: int = 10
) -> Iterator[int]:

    start, end = int(start), int(end)
    min_space = end // k
    yield from (
        rng.randint(start, (start := start + min_space)) for _ in range(k)
    )


def fade(
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


def make_elm(side: int = 120, option: str = "rec") -> ExtendedElement:
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


def linplane(
    xrange: tuple[int, int] = (0, 512),
    yrange: tuple[int, int] = (0, 512),
    xk: int = 10,
    yk: int = 10,
) -> Iterator[tuple[int, int]]:
    """a linear plane: a cartisan product of 2 linear spaces"""
    xspace = linspace(*xrange, n_samples=xk)
    yspace = linspace(*yrange, n_samples=yk)
    return product(xspace, yspace)  # type: ignore


def randplane(
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

    plane = linplane(xrange, yrange, xk, yk)
    yield from (coord for coord in plane if rng.random() < rate)
