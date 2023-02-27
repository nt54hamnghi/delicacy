import re
from abc import ABC
from typing import Any, Iterator

from attrs import asdict, field, frozen
from attrs.validators import and_, ge, in_, le
from cytoolz.curried import keyfilter, keymap, valfilter
from cytoolz.functoolz import pipe


def cast_float(item: str):
    try:
        return float(item)
    except ValueError:
        return str(item)


class Style(ABC):
    __slots__: tuple[str] = tuple()  # type: ignore

    @classmethod
    def name(cls) -> str:
        return cls.__name__.lower()

    def get_prop_name(self, prop: str) -> str:
        style = self.__class__.__name__.lower()
        return style if prop == "color" else f"{style}-{prop}"

    @property
    def props(self) -> Iterator[str]:
        return (self.get_prop_name(prop) for prop in self.__slots__)

    def __str__(self) -> str:
        values = tuple(getattr(self, attr) for attr in self.__slots__)
        output = (
            f"{prop}: {value};"
            for prop, value in zip(self.props, values)
            if value is not None
        )
        return " ".join(output)

    def to_dict(self) -> dict[str, Any]:
        prop_map = keymap(self.get_prop_name)
        filter_none = valfilter(lambda x: x is not None)
        return pipe(self, asdict, prop_map, filter_none)

    @staticmethod
    def parse(style_str: str, filter_by: str | None = None) -> dict[str, str]:
        tokens = re.split("[:;][ ]?", style_str.strip())
        props, raw = tokens[:-1:2], tokens[1::2]
        values = map(cast_float, raw)

        style_dict = dict(zip(props, values))

        if filter_by is not None:
            return keyfilter(lambda x: filter_by.lower() in x, style_dict)

        return style_dict


@frozen
class Stroke(Style):
    color: str = "black"
    opacity: float = field(default=1, validator=and_(ge(0), le(1)))
    width: float = 1
    linecap: str | None = field(
        default=None,
        validator=in_(("butt", "square", "round", None)),
    )


@frozen
class Fill(Style):
    color: str = "black"
    opacity: float = field(default=1, validator=and_(ge(0), le(1)))
    rule: str | None = field(
        default=None, validator=(in_(("nonzero", "evenodd", None)))
    )
