from typing import ClassVar

from attrs import asdict, field, frozen
from attrs.validators import and_, ge, in_, le


class Style:
    _main_property: ClassVar[str] = ""

    def __str__(self) -> str:
        name = self.__class__.__name__.lower()
        prop = self._main_property
        keyfunc = lambda k: name if k == prop else f"{name}-{k}"  # noqa

        return " ".join(
            f"{keyfunc(key)}: {val};"
            for key, val in asdict(self).items()
            if val is not None
        )


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
    miterlimit: float | None = field(default=None)

    @miterlimit.validator
    def _check_if_miter(self, attr, val: float | None) -> None:
        if val is not None:
            if self.linejoin != "miter":
                raise ValueError(
                    "miterlimit can only be set if linejoin is 'miter'"
                )


@frozen
class Fill(Style):
    _main_property: ClassVar[str] = "color"

    color: str = "black"
    opacity: float = field(default=1, validator=and_(ge(0), le(1)))
    rule: str | None = field(
        default=None, validator=in_(("nonzero", "evenodd", None))
    )
