from itertools import chain
from typing import Iterator

from lxml.etree import Element

from delicacy.svglib.elements.element import ExtendedElement, svg_define
from delicacy.svglib.elements.peripheral.point import Point
from delicacy.svglib.utils.utils import Size


@svg_define
class Use(ExtendedElement):
    href: str
    location: Point = Point(0, 0)
    size: Size | None = None

    def __attrs_post_init__(self) -> None:

        self.href = "#" + self.href

        tags = "href x y".split()
        values: Iterator[str] = (str(v) for v in (self.href, *self.location))

        if self.size is not None:
            tags += ["width", "height"]
            values = chain(values, (str(i) for i in self.size))

        self._element = Element("use", attrib=dict(zip(tags, values)))
