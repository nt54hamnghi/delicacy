import os
from hashlib import sha3_512
from itertools import product
from random import choices
from string import ascii_letters, digits, punctuation
from unittest import mock

import pytest
from bitstring import BitArray

from delicacy.config import COLLECTION_DIR
from delicacy.igen.collection import Collection
from delicacy.igen.igen import ImageGenerator


@pytest.fixture(scope="session")
def collection():
    collection_dir = COLLECTION_DIR / "cat"
    layers_name = ["body", "fur", "eyes", "mount", "accessories"]
    return Collection("Cat", collection_dir, layers_name)


@pytest.fixture(scope="session")
def img_gen(collection):
    return ImageGenerator(collection)


def test_create_igen(img_gen):
    assert img_gen.collection.name == "Cat"
    assert img_gen.hash_func.__name__ == sha3_512.__name__


@pytest.mark.parametrize(
    ("key", "data"),
    (
        pytest.param("test", "", id="str"),
        pytest.param(b"test", "", id="bytes"),
        pytest.param(b"test", None, id="none_data"),
    ),
)
def test_igen_hash(img_gen, key, data):
    hashed = img_gen._hash(key, data)

    hash_object = sha3_512("test".encode())
    hash_object.update(str(data).encode("utf8"))
    sha3_512_hashed = hash_object.digest()

    assert isinstance(hashed, BitArray)
    assert hashed.bytes == sha3_512_hashed


@pytest.fixture
def image_path(tmp_path):
    for i in range(10):
        new_path = tmp_path / f"layers#{i}"
        new_path.mkdir()
        for j in range(10):
            (new_path / f"img_{j}.png").touch()
    return tmp_path


def test_igen_pick(img_gen, image_path):
    _hash = img_gen._hash("test")
    _path = image_path / "layers#0"

    picked = img_gen._pick(_hash, _path)
    expected = f"img_{_hash.uint % len(list(_path.iterdir()))}.png"

    assert os.path.basename(picked) == expected


@pytest.mark.parametrize(
    "hashed", (0, 10, 2**32), ids=["inrange", "outrange", "large"]
)
@mock.patch("delicacy.igen.igen.ImageGenerator._hash")
def test_igen_pick_layers(mock_hash, image_path, hashed):
    mock_hash.return_value = BitArray(uint=hashed, length=256)

    collection = Collection("Test", image_path)
    igen = ImageGenerator(collection)

    expected = [
        str(_path / f"img_{hashed%10}.png") for _path in image_path.iterdir()
    ]

    result = list(igen._pick_layers(b""))

    assert result == sorted(expected)


def test_generate_max_length(img_gen):
    with pytest.raises(ValueError):
        img_gen.generate("-" * 33)


@pytest.mark.parametrize(
    ("size", "factor", "coll"),
    tuple(product((256, 512), (0.8, 1.0), ["cat", "robot"])),
)
def test_generate(size, factor, coll):
    collection_dir = COLLECTION_DIR / coll
    collection = Collection(coll.capitalize(), collection_dir)
    img_gen = ImageGenerator(collection)

    phrase = "".join(choices(ascii_letters + digits + punctuation, k=32))
    print(phrase)

    img1 = img_gen.generate(phrase, size=(size, size), factor=factor)
    img2 = img_gen.generate(phrase, size=(size, size), factor=factor)

    assert img1.tobytes() == img2.tobytes()
