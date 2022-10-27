from typing import ClassVar

from attrs import asdict, field, frozen
from attrs.validators import and_, ge, in_, le
from cytoolz.dicttoolz import valfilter


class Style:
    _main_property: str = ""

    def __str__(self) -> str:

        _name = self.__class__.__name__.lower()
        _dict = valfilter(lambda x: x is not None, asdict(self))
        _keyfunc = (
            lambda k: _name if k == self._main_property else f"{_name}-{k}"
        )

        result = (f"{_keyfunc(key)}: {val};" for key, val in _dict.items())
        return " ".join(result)


@frozen
class Stroke(Style):
    _main_property: ClassVar[str] = "color"

    color: str = "black"
    opacity: float = field(default=1, validator=and_(ge(0), le(1)))

    width: float = 1
    linecap: str | None = field(
        default=None,
        validator=in_(("butt", "square", "round", None)),
    )
    linejoin: str | None = field(
        default=None,
        validator=in_(("miter", "round", "bevel", None)),
    )
    miterlimit: float | None = field(default=None, init=False)

    def set_miterlimit(self, value):
        if self.linejoin != "miter":
            raise ValueError(
                "miterlimit can only be set if linejoin is 'miter'"
            )
        self.miterlimit = str(value)


@frozen
class Fill(Style):
    _main_property: ClassVar[str] = "color"

    color: str = "black"
    opacity: float = field(default=1, validator=and_(ge(0), le(1)))
    rule: str | None = field(
        default=None, validator=in_(("nonzero", "evenodd", None))
    )
