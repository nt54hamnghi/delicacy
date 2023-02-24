import pytest
from lxml import etree
from lxml.etree import _Element
from PIL import Image as PILImage
from wand import image as WandImage

from delicacy.svglib.utils.utils import (
    eprint,
    get_canvas,
    linspace,
    materialize,
    wand2pil,
)

STANDARD_CANVAS = {
    "width": "512",
    "height": "512",
    "xmlns": "http://www.w3.org/2000/svg",
}


def test_get_canvas_empty():
    canvas = get_canvas()

    assert isinstance(canvas, _Element)
    assert canvas.attrib == STANDARD_CANVAS


@pytest.mark.parametrize(
    ("size", "kwds"),
    (
        (("1024", "1024"), {}),
        (("1024", "1024"), dict(background_color="black")),
    ),
    ids=["no-keywords", "with-keywords"],
)
def test_get_canvas(size, kwds):
    width, height = size
    canvas = get_canvas(*size, **kwds)
    expected = STANDARD_CANVAS | dict(width=width, height=height, **kwds)

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
    result = tuple(linspace(*args))
    assert result == expected


# use capsys fixture to capture standard output and error
def test_eprint(capsys):
    root = etree.Element("root")
    etree.SubElement(root, "child1")
    etree.SubElement(root, "child2")

    eprint(root, end="")
    [output, _] = capsys.readouterr()

    expected = etree.tostring(root, pretty_print=True)

    assert output.encode("utf8") == expected


def test_materialize():
    canvas = get_canvas()
    img = materialize(canvas)

    assert isinstance(img, WandImage.Image)
    assert img.width == int(STANDARD_CANVAS["width"])
    assert img.height == int(STANDARD_CANVAS["height"])


def test_wand2pil():
    canvas = get_canvas()
    wand_img = materialize(canvas)
    pil_img = wand2pil(wand_img)

    assert isinstance(pil_img, PILImage.Image)
    assert pil_img.width == int(STANDARD_CANVAS["width"])
    assert pil_img.height == int(STANDARD_CANVAS["height"])
