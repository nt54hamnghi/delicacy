from io import BytesIO
from typing import NamedTuple

from cairosvg import svg2png
from lxml import etree
from lxml.etree import Element, _Element
from PIL import Image


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


def svg2img(bytestring: bytes, bgcolor="black", *args, **kwds) -> Image.Image:
    img_bytes = svg2png(bytestring, background_color=bgcolor, *args, **kwds)
    byte_io = BytesIO(img_bytes)
    return Image.open(byte_io)


def canvas2img(canvas: _Element, *args, **kwds) -> Image.Image:
    return svg2img(etree.tostring(canvas), *args, **kwds)


class Size(NamedTuple):
    width: float
    height: float
