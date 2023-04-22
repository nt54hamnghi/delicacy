"""
Copyright (c) 2023 Nghi Trieu Ham Nguyen

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
from collections.abc import Sequence
from itertools import chain
from typing import TypeVar

from attrs import define
from attrs import field
from attrs.validators import in_
from lxml.etree import Element
from lxml.etree import SubElement

from delicacy.svglib.elements.element import SVGElement
from delicacy.svglib.utils.utils import linspace


@define
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

        attrib = {
            "offset": f"{offset:.0%}",
            "stop-color": color,
            "stop-opacity": str(float(opacity)),
        }

        SubElement(self.base, "stop", attrib=attrib)


@define
class LinearGradient(BaseGradient):
    id: str = "linearGradient"
    start: tuple[float, float] = field(default=(0, 0))
    stop: tuple[float, float] = field(default=(1, 1))

    def __attrs_post_init__(self) -> None:
        tags = ["x1", "y1", "x2", "y2"]
        start = (f"{i:.0%}" for i in self.start)
        stop = (f"{i:.0%}" for i in self.stop)

        attrib = dict(zip(tags, chain(start, stop), strict=True))
        attrib.update(id=self.id, spreadMethod=self.spreadMethod)

        self._element = Element("linearGradient", attrib=attrib)


@define
class RadialGradient(BaseGradient):
    id: str = "radialGradient"
    radius: float = 0.55
    center: tuple[float, float] = field(default=(0.5, 0.5))
    focus: tuple[float, float] = field(default=(0.5, 0.5))

    def __attrs_post_init__(self) -> None:
        tags = ["cx", "cy", "fx", "fy"]
        center = (f"{i:.0%}" for i in self.center)
        focus = (f"{i:.0%}" for i in self.focus)

        attrib = dict(zip(tags, chain(center, focus), strict=True))
        attrib.update(
            id=self.id, r=f"{self.radius:.0%}", spreadMethod=self.spreadMethod
        )

        self._element = Element("radialGradient", attrib=attrib)


GradientT = TypeVar("GradientT", bound=BaseGradient)


def create_gradient(
    cls: type[GradientT], colors: Sequence[str], *args, **kwds
) -> GradientT:
    gradient = cls(*args, **kwds)

    for color, offset in zip(colors, linspace(0, 1, len(colors))):
        gradient.add_stop(offset, color, 1)

    return gradient
