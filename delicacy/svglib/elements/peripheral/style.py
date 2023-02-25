from abc import ABC
from typing import Iterator

from attrs import field, frozen
from attrs.validators import and_, ge, in_, le


class Style(ABC):
    __slots__: tuple[str] = tuple()  # type: ignore

    @staticmethod
    def get_prop_name(style: str, prop: str) -> str:
        return style if prop == "color" else f"{style}-{prop}"

    @property
    def style(self) -> str:
        return self.__class__.__name__.lower()

    @property
    def props(self) -> Iterator[str]:
        style = self.style
        return (self.get_prop_name(style, prop) for prop in self.__slots__)

    def __str__(self) -> str:
        values = tuple(getattr(self, attr) for attr in self.__slots__)
        output = (
            f"{prop}: {value};"
            for prop, value in zip(self.props, values)
            if value is not None
        )
        return " ".join(output)


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
