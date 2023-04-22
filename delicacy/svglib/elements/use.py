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
from itertools import chain
from typing import Iterator

from attrs import define
from lxml.etree import Element

from delicacy.svglib.elements.element import ExtendedElement
from delicacy.svglib.elements.peripheral.point import Point
from delicacy.svglib.utils.utils import Size


@define
class Use(ExtendedElement):
    href: str
    location: Point = Point(0, 0)
    size: Size | None = None

    def __attrs_post_init__(self) -> None:
        self.href = "#" + self.href

        tags = "href x y".split()
        vals: Iterator[str] = map(str, (self.href, *self.location))

        if self.size is not None:
            tags += ["width", "height"]
            vals = chain(vals, map(str, self.size))

        self._element = Element("use", attrib=dict(zip(tags, vals)))
