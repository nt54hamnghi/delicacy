import re
from abc import ABC, abstractmethod
from functools import cache, partial
from typing import Any

from attrs import define, field
from cytoolz.dicttoolz import keyfilter
from lxml import etree
from lxml.etree import Element, _Element

from delicacy.svglib.elements.peripheral.style import Style
from delicacy.svglib.elements.peripheral.transform import Transform

svg_define = partial(define, str=False, order=False)


@svg_define
class SVGElement(ABC):
    _element: _Element = field(repr=False, init=False)

    @abstractmethod
    def __attrs_post_init__(self) -> None:
        """subclasses must define how to construct _element in this method"""

    @property
    def base(self):
        return self._element

    def _element_repr(self) -> str:
        return repr(self._element)

    def __str__(self) -> str:
        return bytes(self).decode("utf8")

    def __bytes__(self) -> bytes:
        return etree.tostring(self._element, pretty_print=True)

    def set(self, attr: str, value: Any) -> None:
        self.base.set(attr, value)

    def get(self, attr: str):
        return self.base.get(attr)


class ExtendedElement(SVGElement):
    __slots__ = ()

    @staticmethod
    @cache
    def extract_styles(
        style_str: str, kind: str | None = None
    ) -> dict[str, str]:
        temp = [item.strip() for item in re.split(r"[:;]", style_str)]
        keys, values = temp[0:-1:2], temp[1:-1:2]

        if kind is not None:
            style_set = set(k.split("-")[0] for k in keys)
            if (kind := kind.lower()) not in style_set:
                raise ValueError("not a valid style")

        style_dict = dict(zip(keys, values))

        if kind is None:
            return style_dict

        return keyfilter(lambda x: kind in x, style_dict)

    @property
    def styles(self):
        return self.extract_styles(self._element.get("style"))

    def add_style(self, style: Style) -> None:
        super().set("style", str(style))

    def apply_styles(self, *styles: Style) -> None:
        _styles = " ".join(str(style) for style in styles)
        super().set("style", _styles)

    def set_style(self, style: Style) -> None:
        _styles = self.base.get("style")
        if _styles is None:
            self.add_style(style)
        else:
            kind = style.__class__.__name__.lower()
            remains = ";".join(s for s in _styles.split(";") if kind not in s)
            _styles = str(style) + f" {remains.strip()}"
            super().set("style", _styles)

    def add_transform(self, transform: Transform) -> None:
        value = transform()
        if value == "":
            raise ValueError("empty transform")
        super().set("transform", value)


class WrappingElement(ExtendedElement):
    __slots__ = ()

    def __init__(self, tag, **kwds: Any) -> None:
        self._element = Element(tag, attrib=kwds)

    def __attrs_post_init__(self) -> None:
        ...

    def __call__(self, *childs: SVGElement, **kwds: Any) -> "WrappingElement":
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
