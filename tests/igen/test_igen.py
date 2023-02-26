import hashlib
import os
from itertools import product
from random import choices
from string import ascii_letters, digits, punctuation
from unittest import mock

import pytest
from bitstring import BitArray

from delicacy.config import COLLECTION_DIR
from delicacy.igen.collection import Collection
from delicacy.igen.igen import ImageGenerator

HASH_FUNC = hashlib.sha3_256


@pytest.fixture(scope="session")
def collection():
    collection_dir = COLLECTION_DIR / "cat"
    layers_name = ["body", "fur", "eyes", "mount", "accessories"]
    return Collection("Cat", collection_dir, layers_name)


@pytest.fixture(scope="session")
def img_gen(collection):
    return ImageGenerator(collection, HASH_FUNC)


def test_create_igen(img_gen):
    assert img_gen.collection.name == "Cat"
    assert img_gen.hash_func.__name__ == HASH_FUNC.__name__


@pytest.mark.parametrize(
    "key",
    (
        pytest.param("test", id="str"),
        pytest.param(b"test", id="bytes"),
    ),
)
def test_igen_hash(img_gen, key):
    igen_hash = img_gen._hash(key, "")

    expected_hash = (
        "36f028580bb02cc8272a9a020f4200e346e276ae664e45ee80745574e2f5ab80"
    )

    assert isinstance(igen_hash, BitArray)
    assert igen_hash.hex == expected_hash


@pytest.mark.parametrize(
    ("data"),
    (0, "", list(), set(), dict(), None),
    ids=("int", "str", "list", "set", "dict", "None"),
)
def test_igen_hash_with_arbitrary_data(img_gen, data):
    igen_hash = img_gen._hash("", data)

    expected_hash = HASH_FUNC(str(data).encode()).hexdigest()

    assert isinstance(igen_hash, BitArray)
    assert igen_hash.hex == expected_hash


def test_generate_max_length(img_gen):
    with pytest.raises(ValueError):
        img_gen.generate("-" * 33)


# For a imagined/mocked file system
LAYERS_COUNT = 10  # number of layers
IMAGES_COUNT = 10  # numbers of images in each layer


@pytest.fixture
def imagined(tmp_path):

    for layer in range(LAYERS_COUNT):
        new_path = tmp_path / f"layers#{layer}"
        new_path.mkdir()

        for img in range(IMAGES_COUNT):
            (new_path / f"img_{img}.png").touch()

    return tmp_path


@pytest.mark.parametrize("layer", range(LAYERS_COUNT), ids=range(10))
def test_igen_pick(layer, img_gen, imagined):

    layer_path = imagined / f"layers#{layer}"
    hash_value = img_gen._hash("test")

    picked = img_gen._pick(hash_value, layer_path)
    expected = f"img_{hash_value.uint % IMAGES_COUNT}.png"

    assert os.path.basename(picked) == expected


@pytest.mark.parametrize(
    "hash_value", (0, 10, 2**32), ids=["inrange", "outrange", "large"]
)
@mock.patch("delicacy.igen.igen.ImageGenerator._hash")
def test_igen_pick_layers(mock_hash, imagined, hash_value):
    """
    Always pick layers from the list of possible layers,
    even if the hash value is in range (0 to 9), out range, or arbitrarily large.
    """

    mock_hash.return_value = BitArray(uint=hash_value, length=256)
    collection = Collection("Test", imagined)
    img_gen = ImageGenerator(collection)

    expected = [
        str(path / f"img_{hash_value % IMAGES_COUNT}.png")
        for path in imagined.iterdir()
    ]
    result = list(img_gen._pick_layers(b""))

    assert result == sorted(expected)


@pytest.mark.parametrize(
    ("size", "factor", "collection_name"),
    tuple(product((256, 512), (0.8, 1.0), ["cat", "robot"])),
)
def test_generate(size, factor, collection_name):
    collection_dir = COLLECTION_DIR / collection_name
    collection = Collection(collection_name.capitalize(), collection_dir)
    img_gen = ImageGenerator(collection)

    phrase = "".join(choices(ascii_letters + digits + punctuation, k=32))

    # the same phrase should generate the same image
    first = img_gen.generate(phrase, size=(size, size), factor=factor)
    second = img_gen.generate(phrase, size=(size, size), factor=factor)

    assert first.tobytes() == second.tobytes()
