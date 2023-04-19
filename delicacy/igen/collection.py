import os
from collections.abc import Iterable
from collections.abc import Iterator
from os import PathLike
from typing import AnyStr
from typing import TypeAlias

from attrs import field
from attrs import frozen

PathType: TypeAlias = PathLike | AnyStr


@frozen(order=False)
class Collection:
    name: str
    path: PathType
    layer_names: tuple[str] = field(converter=tuple)
    layer_paths: Iterable[PathType] = field(init=False)

    @layer_names.default
    def _(self) -> list[str]:
        return sorted(os.listdir(self.path))

    @layer_paths.default
    def _(self) -> list[PathType]:
        return sorted(d.path for d in os.scandir(self.path))

    @property
    def layers(self) -> Iterator[tuple[str, PathType]]:
        return zip(self.layer_names, self.layer_paths)
