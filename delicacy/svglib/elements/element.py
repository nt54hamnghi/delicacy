import re
from functools import cache, partial
from typing import Any

from attrs import define, field
from cytoolz.dicttoolz import keyfilter
from lxml import etree
from lxml.etree import _Element

from delicacy.svglib.utils.style import Style
from delicacy.svglib.utils.transform import Transform

svg_define = partial(define, str=False, order=False)


@define
class SVGElement:
    _element: _Element = field(init=False, repr=False)

    def _element_repr(self) -> str:
        return repr(self._element)

    def __str__(self) -> str:
        return bytes(self).decode("utf8")

    def __bytes__(self) -> bytes:
        return etree.tostring(self._element, pretty_print=True)

    def __call__(self) -> _Element:
        return self._element

    def set(self, tag: str, value: Any) -> None:
        self().set(tag, value)

    def get(self, tag: str):
        return self().get(tag)

    @classmethod
    def from_etree_element(cls, value: _Element) -> "SVGElement":
        if not isinstance(value, _Element):
            raise ValueError("not an etree._Element")
        instance = cls()
        instance._element = value
        return instance


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
        _styles = self().get("style")
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
