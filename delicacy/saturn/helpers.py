from collections.abc import Iterator
from hashlib import sha3_256
from itertools import product, repeat
from random import Random

from delicacy.svglib.elements.element import (
    ExtendedElement,
    WrappingElement,
    defs,
    group,
)
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


def generate_id(*args):
    hs = sha3_256()
    for item in args:
        hs.update(str(item).encode())
    return hs.hexdigest()[:32]


def sorted_randspace(
    rng: Random, start: float = 0, end: float = 512, k: int = 10
) -> Iterator[int]:

    start, end = int(start), int(end)
    min_space = (end - start) // k
    yield from (
        rng.randint(start, (start := start + min_space))  # noqa F481
        for _ in range(k)
    )


def linear_plane(
    xrange: tuple[int, int] = (0, 512),
    yrange: tuple[int, int] = (0, 512),
    xk: int = 10,
    yk: int = 10,
) -> Iterator[tuple[int, int]]:
    """a linear plane: a cartisan product of 2 linear spaces"""

    xspace = linspace(*xrange, n_samples=xk)
    yspace = linspace(*yrange, n_samples=yk)
    return product(xspace, yspace)  # type: ignore


def rand_plane(
    rng: Random,
    xrange: tuple[int, int] = (0, 512),
    yrange: tuple[int, int] = (0, 512),
    xk: int = 10,
    yk: int = 10,
    rate: float = 0.2,
) -> Iterator[tuple[int, int]]:
    """randomly dropping points from a linear plane"""

    if not 0 < rate <= 1:
        raise ValueError("rate must be in range (0, 1]")

    plane = linear_plane(xrange, yrange, xk, yk)
    yield from (coord for coord in plane if rng.random() < rate)


def make_shape(
    side: float = 120, option: str = "rec", x: int = 0, y: int = 0
) -> ExtendedElement:
    """make shape based on option"""

    match option:
        case "cir":
            radius = side // 2
            cx = x + radius if x != 0 else x
            cy = y + radius if y != 0 else y
            return Circle.make_circle(radius, cx, cy)
        case "rec":
            return Rectangle.make_rectangle(x, y, side, side)
        case "tri":
            return ETriangle(location=Point(x, y), side=side)
        case "xsh":
            return XShape(location=Point(x, y), length=side)
        case _:
            raise ValueError(
                f'option: {option} is not one of "rec", "tri", "cir", "xsh"'
            )


def spreadit(
    rng: Random, spread: tuple[int, int], k: int = 3
) -> Iterator[tuple[int, int]]:
    """used in fade, dictates how to spread the faded effects"""

    direction = rng.choices((-1, 1), k=2)
    spread_range = range(*spread)

    for i, (x, y) in enumerate(repeat(direction, times=k)):
        dx, dy = rng.choices(spread_range, k=2)
        yield i * x * dx, i * y * dy


def fade(
    rng: Random,
    element: ExtendedElement,
    color: str,
    scale: float,
    num: int = 3,
    location: Point = Point(0, 0),
    rotate: float | None = None,
    spread: tuple[int, int] = (15, 25),
    fading_scale: float = 0.8,
) -> ExtendedElement:
    """Create fading effect on an element shape"""

    opacity = 1.0
    width = 10.0 if num <= 1 else 20.0
    rotate = rng.randint(0, 360) if rotate is None else rotate % 360
    fill = Fill(color="none")

    eid = generate_id(rng.getstate())

    defs_element = defs(group(element, id=eid))

    faded = WrappingElement("g")
    faded.append(defs_element)

    for loc in spreadit(rng, spread, k=num):
        stroke = Stroke(color, opacity, width)
        use = Use(eid, loc)  # type: ignore
        use.apply_styles(stroke, fill)
        faded.append(use)

        width *= fading_scale
        opacity *= fading_scale

    transform = Transform().translate(*location).scale(scale).rotate(rotate)
    faded.add_transform(transform)

    return faded
