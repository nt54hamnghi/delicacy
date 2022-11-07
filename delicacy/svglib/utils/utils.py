from collections.abc import Iterator
from io import BytesIO
from itertools import count
from typing import NamedTuple

from cairosvg import svg2png
from cytoolz.itertoolz import take
from lxml import etree
from lxml.etree import Element, _Element
from PIL import Image


class Size(NamedTuple):
    width: float
    height: float


def eprint(element: _Element) -> None:
    msg = etree.tostring(element, pretty_print=True).decode("utf8")
    print(msg)


def get_canvas(
    width: float = 512, height: float = 512, **kwds: str
) -> _Element:
    tag = dict(
        width=str(width),
        height=str(height),
        xmlns="http://www.w3.org/2000/svg",
    )
    tag |= kwds
    nsmap = dict(xlink="http://www.w3.org/1999/xlink")
    return Element("svg", attrib=tag, nsmap=nsmap)


def linspace(start: float, stop: float, n_samples: int) -> Iterator[float]:
    if start >= stop:
        raise ValueError("start must be less than stop")
    if n_samples < 0:
        raise ValueError("number of samples, must be non-negative")
    elif n_samples == 0:
        return iter(())

    step = (stop - start) / (n_samples - 1)
    space = (round(i, 3) for i in count(start, step))

    return take(n_samples, space)


def svg2img(bytestring: bytes, *args, **kwds) -> Image.Image:
    img_bytes = svg2png(bytestring, *args, **kwds)
    byte_io = BytesIO(img_bytes)
    return Image.open(byte_io)


def canvas2img(
    canvas: _Element, bg_color="black", *args, **kwds
) -> Image.Image:
    return svg2img(
        etree.tostring(canvas), background_color=bg_color, *args, **kwds
    )
