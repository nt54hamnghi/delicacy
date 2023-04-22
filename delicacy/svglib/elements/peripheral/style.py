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
import re
from abc import ABC
from typing import Any
from typing import Iterator

from attrs import asdict
from attrs import field
from attrs import frozen
from attrs.validators import and_
from attrs.validators import ge
from attrs.validators import in_
from attrs.validators import le
from cytoolz.curried import keyfilter
from cytoolz.curried import keymap
from cytoolz.curried import valfilter
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
        return pipe(self, asdict, prop_map, filter_none)  # type: ignore

    @staticmethod
    def parse(style_str: str, filter_by: str | None = None) -> dict[str, str]:
        tokens = re.split("[:;][ ]?", style_str.strip())
        props, raw = tokens[:-1:2], tokens[1::2]
        values = map(cast_float, raw)

        style_dict = dict(zip(props, values))

        if filter_by is not None:
            return keyfilter(lambda x: filter_by.lower() in x, style_dict)  # type: ignore

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
