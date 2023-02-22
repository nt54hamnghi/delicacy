import hashlib
import os
from collections.abc import Callable, Iterator
from typing import Protocol, TypeAlias, cast
from unicodedata import normalize

from bitstring import BitArray
from PIL import Image

from delicacy.igen.collection import Collection, PathType


# Protocol definitions are not supposed to be executed, thus excluded from coverage report
class SupportHashing(Protocol):
    def digest(self) -> bytes:  # pragma: no cover
        pass

    def hexdigest(self) -> str:  # pragma: no cover
        pass

    def update(self, __data: bytes) -> None:  # pragma: no cover
        pass


# Protocol definitions are not supposed to be executed, thus excluded from coverage report
class SupportStr(Protocol):
    def __str__(self) -> str:  # pragma: no cover
        pass


HashFunction: TypeAlias = Callable[..., SupportHashing]


class ImageGenerator:
    def __init__(
        self,
        collection: Collection,
        hash_func: HashFunction = hashlib.sha3_512,
    ) -> None:
        self.collection = collection
        self.hash_func = hash_func

    def _hash(self, key: str | bytes, data: SupportStr = "") -> BitArray:

        _key = key if isinstance(key, bytes) else key.encode("utf8")
        _data = str(data).encode("utf8")

        hashed = self.hash_func(_key)
        hashed.update(_data)

        return BitArray(bytes=hashed.digest())

    @staticmethod
    def _pick(_hash: BitArray, path: PathType) -> PathType:
        imgs = sorted(d.path for d in os.scandir(path))
        chosen_idx = _hash.uint % len(imgs)
        return imgs[chosen_idx]

    def _pick_layers(self, seed: bytes | BitArray) -> Iterator[PathType]:
        if isinstance(seed, bytes):
            seed = BitArray(bytes=seed)

        base_hash = self._hash(seed.bytes, self.collection.name)

        for name, path in self.collection.layers:
            layer_hash = self._hash(base_hash.bytes, name)
            yield self._pick(layer_hash, path)

    def _assemble(
        self,
        layers: Iterator[PathType],
        size: tuple[int, int] = (300, 300),
        factor: float = 0.8,
    ) -> Image.Image:
        fx, fy = size
        lx, ly = int(fx * factor), int(fy * factor)
        box = (fx - lx) // 2, fy - ly

        layers = cast(Iterator[str], layers)

        with Image.open(next(layers)) as base:
            for item in layers:
                with Image.open(item) as img:
                    base.paste(img, box=(0, 0), mask=img)

        base = base.resize(size=(lx, ly))

        with Image.new(mode="RGBA", size=size) as frame:
            frame.paste(base, box, mask=base)
            return frame

    def generate(self, phrase: str, *args, **kwds) -> Image.Image:
        if len(phrase) > 32:
            raise ValueError("phrase length must be less than 32")
        seed = self._hash(normalize("NFC", phrase))
        layers = self._pick_layers(seed)
        return self._assemble(layers, *args, **kwds)
