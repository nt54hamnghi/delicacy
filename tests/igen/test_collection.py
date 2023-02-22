import pytest

from delicacy.config import COLLECTION_DIR
from delicacy.igen.collection import Collection

PASSED_LAYER_NAMES = ("body", "fur", "eyes", "mount", "accessories")
DEFAULT_LAYER_NAMES = (
    "000#00body",
    "001#01fur",
    "002#02eyes",
    "003#03mouth",
    "004#04accessories",
)


@pytest.fixture
def collection_dir():
    return COLLECTION_DIR / "cat"


@pytest.fixture
def layer_paths(collection_dir):
    return tuple(str(d) for d in collection_dir.iterdir() if d.is_dir())


def test_layer_names_converted_to_tuple(collection_dir):
    cat = Collection("Cat", collection_dir, list(PASSED_LAYER_NAMES))

    assert isinstance(cat.layer_names, tuple)


@pytest.mark.parametrize(
    ("layer_names", "expected"),
    (
        (PASSED_LAYER_NAMES, PASSED_LAYER_NAMES),
        (None, DEFAULT_LAYER_NAMES),
    ),
    ids=("passed", "default"),
)
def test_create_collection(
    layer_names, expected, collection_dir, layer_paths
):
    if layer_names is None:
        cat = Collection("Cat", collection_dir)
    else:
        cat = Collection("Cat", collection_dir, layer_names)

    assert tuple(cat.layer_paths) == layer_paths
    assert cat.layer_names == expected


def test_collection_layers_property(collection_dir, layer_paths):
    cat = Collection("Cat", collection_dir)

    assert isinstance(cat.layers, zip)
    assert list(cat.layers) == list(zip(DEFAULT_LAYER_NAMES, layer_paths))
