from hashlib import sha512
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
    assert img_gen.hash_func.__name__ == sha512.__name__


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

    hash_object = sha512("test".encode())
    hash_object.update(str(data).encode("utf8"))
    sha512_hashed = hash_object.digest()

    assert isinstance(hashed, BitArray)
    assert hashed.bytes == sha512_hashed


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

    assert picked.name == expected


@pytest.mark.parametrize(
    "hashed", (0, 10, 2**32), ids=["inrange", "outrange", "large"]
)
@mock.patch("delicacy.igen.igen.ImageGenerator._hash")
def test_igen_pick_layers(mock_hash, image_path, hashed):
    mock_hash.return_value = BitArray(uint=hashed, length=256)

    collection = Collection("Test", image_path)
    igen = ImageGenerator(collection)

    expected = [
        _path / f"img_{hashed%10}.png" for _path in image_path.iterdir()
    ]

    assert list(igen._pick_layers(b"")) == expected


# def test_nothing(image_path):
#     # print(type(tmpdir))
#     print(image_path)
#     print(sorted(image_path.iterdir()))
