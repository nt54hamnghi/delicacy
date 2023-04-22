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
from PIL import Image as PILImage
from wand import image as WandImage

from delicacy.igen.igen import ImageGenerator
from delicacy.saturn.saturn import BackgroundMaker
from delicacy.saturn.saturn import MakerFunc
from delicacy.svglib.utils.utils import materialize
from delicacy.svglib.utils.utils import wand2pil


def combine(foreground: PILImage.Image, background: WandImage.Image) -> PILImage.Image:
    img = wand2pil(background)
    img.paste(foreground, (0, 0), foreground)
    return img


def make_background(
    phrase: str,
    maker: MakerFunc,
    width: float = 320,
    height: float = 320,
    background: str | None = None,
) -> WandImage.Image:
    bgmaker = BackgroundMaker.from_phrase(phrase, maker)

    canvas = bgmaker.make(width, height)
    return materialize(canvas, background)


def create(
    phrase: str,
    maker: MakerFunc,
    gen: ImageGenerator,
    width: float = 320,
    height: float = 320,
    background_color: str = "#09132b",
) -> PILImage.Image:
    character = gen.generate(phrase, size=(width, height))
    background = make_background(phrase, maker, width, height, background_color)
    return combine(character, background)
