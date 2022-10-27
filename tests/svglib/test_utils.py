import pytest
from lxml.etree import _Element

from delicacy.svglib.utils import get_canvas

STANDARD_CANVAS = {
    "width": "512",
    "height": "512",
    "xmlns": "http://www.w3.org/2000/svg",
}


@pytest.mark.parametrize(
    ("size", "kwds"),
    (
        (tuple(), {}),
        (("1024", "1024"), {}),
        (("1024", "1024"), dict(background_color="black")),
    ),
    ids=["default", "empty-keywords", "with-keywords"],
)
def test_get_canvas(size, kwds):
    canvas = get_canvas(*size, **kwds)
    expected = STANDARD_CANVAS | kwds
    if size:
        expected["width"] = size[0]
        expected["height"] = size[1]

    assert isinstance(canvas, _Element)
    assert canvas.attrib == expected
