from PIL import Image as PILImage
from wand import image as WandImage

from delicacy.config import COLLECTION_DIR
from delicacy.excite.excite import BackgroundMaker, MakerFunc
from delicacy.igen.collection import Collection
from delicacy.igen.igen import ImageGenerator
from delicacy.svglib.utils.utils import materialize, wand2pil

robot_path = COLLECTION_DIR / "robot"
robot_collection = Collection("Robot", robot_path)
robot_gen = ImageGenerator(robot_collection)


def combine(
    foreground: PILImage.Image, background: WandImage.Image
) -> PILImage.Image:
    img = wand2pil(background)
    img.paste(foreground, (0, 0), foreground)
    return img


def make_background(
    phrase: str, maker: MakerFunc, width: float = 320, height: float = 320
) -> PILImage.Image:
    bgmaker = BackgroundMaker.from_phrase(phrase, maker)

    canvas = bgmaker.generate(width, height)
    return materialize(canvas)


def generate(
    phrase: str,
    maker: MakerFunc,
    gen: ImageGenerator = robot_gen,
    width: float = 320,
    height: float = 320,
) -> PILImage.Image:
    character = gen.generate(phrase, size=(width, height))
    background = make_background(phrase, maker, width, height)
    return combine(character, background)
