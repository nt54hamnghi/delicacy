from collections.abc import Sequence
from itertools import chain
from typing import TypeVar

from attrs import field
from attrs.validators import in_
from lxml.etree import Element, SubElement

from delicacy.svglib.elements.element import SVGElement, svg_define
from delicacy.svglib.utils.utils import linspace


@svg_define(init=False)
class BaseGradient(SVGElement):
    id: str
    spreadMethod: str = field(
        default="pad",
        validator=in_(("pad", "repeat", "reflect")),
        kw_only=True,
    )

    def add_stop(self, offset: float, color: str, opacity: float) -> None:
        if not 0 <= offset <= 1:
            raise ValueError(f"offset: {offset} not in range: [0, 1]")
        if not 0 <= opacity <= 1:
            raise ValueError(f"opacity: {opacity} not in range: [0, 1]")

        attributes = {
            "offset": f"{offset:.0%}",
            "stop-color": color,
            "stop-opacity": str(float(opacity)),
        }

        SubElement(self(), "stop", attrib=attributes)


@svg_define
class LinearGradient(BaseGradient):
    id: str = "linearGradient"
    start: tuple[float, float] = field(default=(0, 0))
    stop: tuple[float, float] = field(default=(1, 1))

    def __attrs_post_init__(self) -> None:
        tags = ["x1", "y1", "x2", "y2"]
        start = (f"{i:.0%}" for i in self.start)
        stop = (f"{i:.0%}" for i in self.stop)

        attrib = dict(zip(tags, chain(start, stop)))
        attrib.update(id=self.id, spreadMethod=self.spreadMethod)

        self._element = Element("linearGradient", attrib=attrib)

    @classmethod
    def make_linear_gradient(
        cls,
        id: str,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        spreadMethod: str,
    ) -> "LinearGradient":
        return cls(id, (x1, y1), (x2, y2), spreadMethod=spreadMethod)


@svg_define
class RadialGradient(BaseGradient):
    id: str = "radialGradient"
    radius: float = 0.55
    center: tuple[float, float] = field(default=(0.5, 0.5))
    focus: tuple[float, float] = field(default=(0.5, 0.5))

    def __attrs_post_init__(self) -> None:
        tags = ["cx", "cy", "fx", "fy"]
        center = (f"{i:.0%}" for i in self.center)
        focus = (f"{i:.0%}" for i in self.focus)

        attrib = dict(zip(tags, chain(center, focus)))
        attrib.update(
            id=self.id, r=f"{self.radius:.0%}", spreadMethod=self.spreadMethod
        )

        self._element = Element("radialGradient", attrib=attrib)

    @classmethod
    def make_radial_gradient(
        cls: str,
        id,
        r: float,
        cx: float,
        cy: float,
        fx: float,
        fy: float,
        spreadMethod: str,
    ) -> "RadialGradient":
        return cls(id, r, (cx, cy), (fx, fy), spreadMethod=spreadMethod)


GradientT = TypeVar("GradientT", bound=BaseGradient)


def create_gradient(
    cls: type[GradientT], colors: Sequence[str], *args, **kwds
) -> GradientT:
    gradient = cls(*args, **kwds)

    for color, offset in zip(colors, linspace(0, 1, len(colors))):
        gradient.add_stop(offset, color, 1)

    return gradient
