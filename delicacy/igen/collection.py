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
