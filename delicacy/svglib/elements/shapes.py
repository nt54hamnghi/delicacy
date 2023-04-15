from collections.abc import Callable, Iterable
from itertools import chain
from math import radians, tan
from typing import cast

from attrs import define
from decorator import decorator
from lxml.etree import Element

from delicacy.svglib.elements.element import ExtendedElement
from delicacy.svglib.elements.peripheral.point import Point
from delicacy.svglib.elements.peripheral.style import Fill, Stroke
from delicacy.svglib.utils.chain import chainable
from delicacy.svglib.utils.utils import Size


@define
class Circle(ExtendedElement):
    radius: float
    center: Point = Point(0, 0)

    def __attrs_post_init__(self) -> None:
        tags = ("cx", "cy", "r")
        vals = map(str, (*self.center, self.radius))
        self._element = Element("circle", attrib=dict(zip(tags, vals)))

    @classmethod
    def make_circle(cls, radius: float, cx: float, cy: float) -> "Circle":
        # mypy can't understand that attrs injects __init__
        return cls(radius, (cx, cy))  # type: ignore


@define
class Line(ExtendedElement):
    start: Point
    stop: Point

    def __attrs_post_init__(self) -> None:
        tags = ("x1", "y1", "x2", "y2")
        vals = map(str, chain(self.start, self.stop))
        self._element = Element("line", attrib=dict(zip(tags, vals)))

    @classmethod
    def make_line(cls, x1: float, y1: float, x2: float, y2: float) -> "Line":
        return cls((x1, y1), (x2, y2))  # type: ignore


@decorator
def relative(func: Callable[..., str], *args, **kwds):
    result = func(*args, **kwds)
    return result.lower()


@define
class Path(ExtendedElement):
    def __attrs_post_init__(self) -> None:
        self._element = Element("path", d="")  # type: ignore

    @property
    def d(self):
        """SVG Path defines path operations inside an attribute named `d`"""
        return self.get("d") or ""

    @chainable.updater
    def _update(self, value: str) -> None:
        self._element.set("d", (self.d + value).lstrip())

    @chainable
    def M(self, x: float, y: float) -> str:
        return f" M{x},{y}"

    m = chainable(relative(M.target))

    @chainable
    def L(self, x: float, y: float) -> str:
        return f" L{x},{y}"

    l = chainable(relative(L.target))  # noqa

    @chainable
    def Q(self, x1: float, y1: float, x: float, y: float) -> str:
        return f" Q{x1},{y1} {x},{y}"

    q = chainable(relative(Q.target))

    @chainable
    def C(
        self, x1: float, y1: float, x2: float, y2: float, x: float, y: float
    ) -> str:
        return f" C{x1},{y1} {x2},{y2} {x},{y}"

    c = chainable(relative(C.target))

    @chainable
    def A(
        self,
        rx: float,
        ry: float,
        x_rotation: float,
        large_arc_flag: bool,
        sweep_flag: bool,
        x: float,
        y: float,
    ) -> str:
        return (
            f" A{rx},{ry} {x_rotation} {large_arc_flag},{sweep_flag} {x},{y}"
        )

    a = chainable(relative(A.target))

    @chainable
    def Z(self) -> str:
        return " Z"

    z = chainable(relative(Z.target))


@define
class Polygon(ExtendedElement):
    points: Iterable[Point]

    def __attrs_post_init__(self) -> None:
        points = " ".join("{},{}".format(*p) for p in self.points)
        # mypy can't understand that attrs injects __init__
        self._element = Element("polygon", points=points)  # type: ignore


@define
class Rectangle(ExtendedElement):
    location: Point
    size: Size
    corner_radius: tuple[int, int] = (0, 0)

    def __attrs_post_init__(self) -> None:
        tags = ("x", "y", "width", "height", "rx", "ry")
        vals = map(str, chain(self.location, self.size, self.corner_radius))
        self._element = Element("rect", attrib=dict(zip(tags, vals)))

    @classmethod
    def make_rectangle(
        cls, x: float, y: float, width: float, height: float
    ) -> "Rectangle":
        return cls((x, y), (width, height))  # type: ignore


def ETriangle(
    location: Point = Point(0, 0), side: float = 120, styless: bool = True
) -> Path:
    """EquilateralTriangle"""
    x, y = location
    half = side // 2
    angle = radians(60)

    path = Path().m(x, y).l(side, 0).l(-half, tan(angle) * half).z()

    if not styless:
        path.apply_styles(Stroke(), Fill(color="none"))

    return cast(Path, path)


def XShape(
    location: Point = Point(0, 0), length: float = 120, styless: bool = True
) -> Path:
    x, y = location
    step = length
    path = Path().m(x, y).l(step, step).m(0, -step).l(-step, step)

    if not styless:
        path.apply_styles(Stroke(), Fill(color="none"))

    return cast(Path, path)
