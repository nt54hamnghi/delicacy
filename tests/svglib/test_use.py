import pytest

from delicacy.svglib.elements.use import Use


@pytest.mark.parametrize(
    "size", ((10, 10), None), ids=["argument", "default"]
)
def test_use(size):
    use = Use("random", size=size)

    expected = dict(href="#random", x="0", y="0")
    if size is not None:
        width, height = size
        expected.update(width=str(width), height=str(height))

    assert use().tag == "use"
    assert use().attrib == expected
