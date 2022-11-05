import pytest
from lxml.etree import _Element

from delicacy.svglib.utils.utils import get_canvas, linspace

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


def test_linspace_empty():
    space = linspace(0, 100, 0)
    assert not list(space)


def test_linspace_fail_zero_samples():
    with pytest.raises(ValueError) as err:
        linspace(0, 100, -1)
    assert str(err.value) == "number of samples, must be non-negative"


@pytest.mark.parametrize(
    ("start", "stop"), ((0, 0), (1, 0)), ids=["equal", "greater"]
)
def test_linspace_fail_start_stop(start, stop):
    with pytest.raises(ValueError) as err:
        linspace(start, stop, 10)
    assert str(err.value) == "start must be less than stop"


@pytest.mark.parametrize(
    ("args", "expected"),
    (
        ((1, 10, 5), (1.0, 3.25, 5.5, 7.75, 10.0)),
        ((0.1, 1.0, 5), (0.1, 0.325, 0.55, 0.775, 1.0)),
        ((-10, -1, 5), (-10.0, -7.75, -5.5, -3.25, -1.0)),
        ((-1, -0.1, 5), (-1.0, -0.775, -0.55, -0.325, -0.1)),
    ),
)
def test_linspace(args, expected):
    result = tuple(round(i, 3) for i in linspace(*args))
    assert result == expected
