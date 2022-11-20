from PIL.Image import Image as PilImg
from wand.image import Image as WandImg

from delicacy.igen.collection import Collection
from delicacy.igen.igen import ImageGenerator

from delicacy.svglib.utils.utils import materialize, wand2pil
from delicacy.excite.excite import BGMaker, MakerFunc

from delicacy.config import COLLECTION_DIR


robot_path = COLLECTION_DIR / "robot"
robot_collection = Collection("Robot", robot_path)
robot_gen = ImageGenerator(robot_collection)


def combine(foreground: PilImg, background: WandImg) -> PilImg:
    img = wand2pil(background)
    img.paste(foreground, (0, 0), foreground)
    return img


def make_background(
    phrase: str, maker: MakerFunc, width: float = 320, height: float = 320
) -> PilImg:
    bgmaker = BGMaker.from_phrase(phrase, maker)

    canvas = bgmaker.generate(width, height)
    return materialize(canvas)


def generate(
    phrase: str,
    maker: MakerFunc,
    gen: ImageGenerator = robot_gen,
    width: float = 320,
    height: float = 320,
) -> PilImg:
    character = gen.generate(phrase, size=(width, height))
    background = make_background(phrase, maker, width, height)
    return combine(character, background)
