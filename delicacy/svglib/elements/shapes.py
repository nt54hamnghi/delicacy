from collections.abc import Iterable
from itertools import chain
from math import radians, tan
from typing import Callable

from attrs import define
from decorator import decorator
from lxml.etree import Element

from delicacy.svglib.elements.element import ExtendedElement
from delicacy.svglib.point import Point
from delicacy.svglib.style import Fill, Stroke
from delicacy.svglib.utils import Size, chainable


@define
class Circle(ExtendedElement):
    radius: float
    center: Point = Point(0, 0)

    def __attrs_post_init__(self) -> None:
        tags = ("cx", "cy", "r")
        vals = (str(v) for v in chain(self.center, (self.radius,)))
        self._element = Element("circle", attrib=dict(zip(tags, vals)))

    @classmethod
    def make_circle(cls, radius: float, cx: float, cy: float) -> "Circle":
        return cls(radius, Point(cx, cy))


@define
class Line(ExtendedElement):
    start: Point
    stop: Point

    def __attrs_post_init__(self) -> None:
        tags = ("x1", "y1", "x2", "y2")
        vals = (str(v) for v in chain(self.start, self.stop))
        self._element = Element("line", attrib=dict(zip(tags, vals)))

    @classmethod
    def make_line(cls, x1: float, y1: float, x2: float, y2: float) -> "Line":
        return cls(Point(x1, y1), Point(x2, y2))


@decorator
def _make_relative(func: Callable[..., ExtendedElement], *args, **kwds):
    result = func(*args, **kwds)
    path_ops = result._element.get("d")

    if path_ops is None:
        raise NotImplementedError

    prev_ops, _, latest_op = path_ops.rpartition(" ")
    result.set("d", prev_ops + _ + latest_op.lower())

    return result


@define
class Path(ExtendedElement):
    def __attrs_post_init__(self) -> None:
        self._element = Element("path", d="")  # type: ignore

    def _update(self, value: str) -> None:
        ops = self._element.get("d")
        if ops is None:
            raise NotImplementedError
        self._element.set("d", ops + value)

    @chainable
    def M(self, x: float, y: float) -> str:
        return f" M{x},{y}"

    m = _make_relative(M)

    @chainable
    def L(self, x: float, y: float) -> str:
        return f" L{x},{y}"

    l = _make_relative(L)  # noqa

    @chainable
    def Q(self, x1: float, y1: float, x: float, y: float) -> str:
        return f" Q{x1},{y1} {x},{y}"

    q = _make_relative(Q)

    @chainable
    def C(
        self, x1: float, y1: float, x2: float, y2: float, x: float, y: float
    ) -> str:
        return f" C{x1},{y1} {x2},{y2} {x},{y}"

    c = _make_relative(C)

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

    a = _make_relative(A)

    @chainable
    def Z(self) -> str:
        return " Z"

    z = _make_relative(Z)


@define
class Polygon(ExtendedElement):
    points: Iterable[Point]

    def __attrs_post_init__(self) -> None:
        points = " ".join("{},{}".format(*p) for p in self.points)
        self._element = Element("polygon", points=points)  # type: ignore


@define
class Rectangle(ExtendedElement):
    location: Point
    size: Size
    corner_radius: tuple[int, int] = (0, 0)

    def __attrs_post_init__(self) -> None:
        tags = ("x", "y", "width", "height", "rx", "ry")
        vals = (
            str(v)
            for v in chain(self.location, self.size, self.corner_radius)
        )
        self._element = Element("rect", attrib=dict(zip(tags, vals)))

    @classmethod
    def make_rectangle(
        cls, x: float, y: float, width: float, height: float
    ) -> "Rectangle":
        return cls(Point(x, y), Size(width, height))


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

    return path


def XShape(
    location: Point = Point(0, 0), length: float = 120, styless: bool = True
) -> Path:
    x, y = location
    step = length
    path = Path().m(x, y).l(step, step).m(0, -step).l(-step, step)

    if not styless:
        path.apply_styles(Stroke(), Fill(color="none"))

    return path