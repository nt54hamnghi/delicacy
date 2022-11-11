import os
from collections.abc import Iterable, Iterator
from os import PathLike
from typing import AnyStr, TypeAlias

from attrs import field, frozen

PathType: TypeAlias = PathLike | AnyStr


@frozen(order=False)
class Collection:
    name: str
    path: PathType
    layer_names: Iterable[str] = field(converter=tuple)

    @layer_names.default
    def _(self) -> list[str]:
        return os.listdir(self.path)

    @property
    def layer_paths(self) -> Iterator[PathType]:
        return (d.path for d in os.scandir(self.path))

    @property
    def layers(self) -> Iterator[tuple[str, PathType]]:
        return zip(self.layer_names, self.layer_paths)
