import hashlib
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Protocol, TypeAlias
from unicodedata import normalize

from bitstring import BitArray
from PIL import Image

from delicacy.igen.collection import Collection


class SupportHashing(Protocol):
    def digest(self) -> bytes:
        ...

    def hexdigest(self) -> str:
        ...

    def update(self, __data: bytes) -> None:
        ...


class SupportStr(Protocol):
    def __str__(self) -> str:
        ...


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
    def _pick(_hash: BitArray, path: Path) -> Path:
        imgs = sorted(path.iterdir())
        chosen_idx = _hash.uint % len(imgs)
        return imgs[chosen_idx]

    def _pick_layers(self, seed: bytes | BitArray) -> Iterator[Path]:
        if isinstance(seed, bytes):
            seed = BitArray(bytes=seed)

        base_hash = self._hash(seed.bytes, self.collection.name)

        for name, path in self.collection.layers:
            layer_hash = self._hash(base_hash.bytes, name)
            yield self._pick(layer_hash, path)

    def _assemble(
        self,
        layers: Iterator[Path],
        size: tuple[int, int] = (300, 300),
        proportion: float = 0.7,
    ) -> Image.Image:
        frame_size = fx, fy = (1024, 1024)
        layer_size = lx, ly = int(fx * proportion), int(fy * proportion)
        box = (fx - lx) // 2, fy - ly

        frame = Image.new(mode="RGBA", size=frame_size)

        for item in layers:
            img = Image.open(item).resize(layer_size)
            frame.paste(img, box, mask=img)
            img.close()

        return frame.resize(size)

    def generate(self, phrase: str, *args, **kwds) -> Image.Image:
        if len(phrase) > 32:
            raise ValueError("phrase length must be less than 32")
        seed = self._hash(normalize("NFC", phrase))
        layers = self._pick_layers(seed)
        return self._assemble(layers, *args, **kwds)
