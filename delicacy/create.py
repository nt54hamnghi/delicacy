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
