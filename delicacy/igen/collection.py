from collections.abc import Iterable, Iterator
from pathlib import Path

from attrs import define, field


@define(frozen=True, eq=False, order=False)
class Collection:
    name: str
    path: Path
    layer_names: Iterable[str] = field(converter=tuple)

    @layer_names.default  # type: ignore
    def _layer(self) -> Iterator[str]:
        return (d.stem for d in self.layer_paths)

    @property
    def layer_paths(self) -> Iterator[Path]:
        return (d for d in self.path.iterdir() if d.is_dir())

    @property
    def layers(self) -> Iterator[tuple[str, Path]]:
        return zip(self.layer_names, self.layer_paths)
