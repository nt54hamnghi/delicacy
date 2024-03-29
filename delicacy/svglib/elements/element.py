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
from abc import ABC
from abc import abstractmethod
from functools import partial
from typing import Any

from attrs import define
from attrs import field
from lxml import etree
from lxml.etree import _Element
from lxml.etree import Element

from delicacy.svglib.elements.peripheral.style import Style
from delicacy.svglib.elements.peripheral.transform import Transform


@define
class SVGElement(ABC):
    _element: _Element = field(repr=False, init=False)

    @abstractmethod
    def __attrs_post_init__(self) -> None:
        """subclasses must define how to construct _element in this method"""

    @property
    def base(self) -> _Element:
        return self._element

    def _element_repr(self) -> str:
        return repr(self._element)

    def __str__(self) -> str:
        return bytes(self).decode("utf8")

    def __bytes__(self) -> bytes:
        return etree.tostring(self._element, pretty_print=True)

    def __len__(self) -> int:
        return len(self._element)

    def set(self, attr: str, value: Any) -> None:
        self._element.set(attr, value)

    def get(self, attr: str) -> str | None:
        return self._element.get(attr)


class ExtendedElement(SVGElement):
    __slots__ = ()

    @property
    def style(self) -> dict[str, str]:
        style_str: str | None = self.get("style")
        return Style.parse(style_str or "")

    def add_style(self, style: Style) -> None:
        super().set("style", str(style))

    def set_style(self, style: Style) -> None:
        current: str | None = self.get("style")

        if current is None:
            self.add_style(style)
        else:
            new = str(style)
            remain = ";".join(
                item for item in current.split(";") if style.name() not in item
            ).strip()
            super().set("style", f"{new} {remain}")

    def apply_styles(self, *styles: Style) -> None:
        new = " ".join(str(style) for style in styles)
        super().set("style", new)

    def add_transform(self, transform: Transform) -> None:
        value = transform()
        if value == "":
            raise ValueError("empty transform")
        super().set("transform", value)


class WrappingElement(ExtendedElement):
    __slots__ = ()

    def __init__(self, tag: str, **kwds: str) -> None:
        self._element = Element(tag, attrib=kwds)

    def __attrs_post_init__(self) -> None:  # pragma: no cover
        ...

    def __call__(self, *childs: SVGElement, **kwds: str):
        for k, v in kwds.items():
            self._element.set(k, v)
        self._element.extend(child.base for child in childs)
        return self

    def append(self, element: SVGElement) -> None:
        self._element.append(element._element)


def wraps(tag, *childs, **kwds):
    return WrappingElement(tag, **kwds)(*childs)


defs = partial(wraps, "defs")
group = partial(wraps, "g")
symbol = partial(wraps, "symbol")
