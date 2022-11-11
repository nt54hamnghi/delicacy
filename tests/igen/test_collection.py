import pytest

from delicacy.config import COLLECTION_DIR
from delicacy.igen.collection import Collection

LAYER_NAMES_AS_ARGUMENT = ("body", "fur", "eyes", "mount", "accessories")
LAYER_NAMES_BY_DEFAULT = (
    "000#00body",
    "001#01fur",
    "002#02eyes",
    "003#03mouth",
    "004#04accessories",
)


@pytest.mark.parametrize(
    ("layer_names", "expected"),
    (
        (LAYER_NAMES_AS_ARGUMENT, LAYER_NAMES_AS_ARGUMENT),
        (list(LAYER_NAMES_AS_ARGUMENT), LAYER_NAMES_AS_ARGUMENT),
        (None, LAYER_NAMES_BY_DEFAULT),
    ),
    ids=("tuple", "list", "default"),
)
def test_create_collection(layer_names, expected):
    # collection directory
    cdir = COLLECTION_DIR / "cat"

    if layer_names is None:
        cat = Collection("Cat", cdir)
    else:
        cat = Collection("Cat", cdir, layer_names)

    layer_dir = tuple(str(d) for d in cdir.iterdir() if d.is_dir())

    assert isinstance(cat.layer_names, tuple)
    assert tuple(cat.layer_paths) == layer_dir
    assert cat.layer_names == expected


def test_collection_layers_property():
    # collection directory
    cdir = COLLECTION_DIR / "cat"
    cat = Collection("Cat", cdir)
    layer_dir = tuple(str(d) for d in cdir.iterdir() if d.is_dir())

    assert isinstance(cat.layers, zip)
    assert list(cat.layers) == list(zip(LAYER_NAMES_BY_DEFAULT, layer_dir))
