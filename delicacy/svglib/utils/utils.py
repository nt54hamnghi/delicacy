"""
Copyright (c) 2023 Nghi Trieu Ham Nguyen

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
from collections.abc import Iterator
from io import BytesIO
from itertools import count
from typing import NamedTuple

from cytoolz.itertoolz import take
from lxml import etree
from lxml.etree import _Element
from lxml.etree import Element
from lxml.etree import tostring
from PIL import Image as PILImange
from wand import image as WandImage


class Size(NamedTuple):
    width: float
    height: float


def get_canvas(width: float = 512, height: float = 512, **kwds: str) -> _Element:
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
    space = take(n_samples, count(start, step))

    return (round(i, 3) for i in space)


def eprint(element: _Element, **kwds) -> None:
    msg = etree.tostring(element, pretty_print=True).decode("utf8")
    print(msg, **kwds)


def materialize(canvas: _Element, background: str | None = None) -> WandImage.Image:
    blob = tostring(canvas)
    return WandImage.Image(blob=blob, format="svg", background=background)


def wand2pil(wand_image: WandImage.Image) -> PILImange.Image:
    bytesio = BytesIO(wand_image.make_blob("png"))
    return PILImange.open(bytesio)
