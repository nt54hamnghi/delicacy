from enum import Enum
from io import BytesIO

from fastapi import FastAPI, Query
from fastapi.responses import Response

from delicacy.config import COLLECTION_DIR
from delicacy.create import create
from delicacy.igen.collection import Collection
from delicacy.igen.igen import ImageGenerator
from delicacy.saturn.saturn import MakerDict

app = FastAPI()


robot_path = COLLECTION_DIR / "robot"
robot_collection = Collection("Robot", robot_path)
robot_gen = ImageGenerator(robot_collection)


# workaround to dynamically create a StrEnum from a dictionary's keys
# as long as a function is decorated with @maker,
# it's automatically added to the MakerDict, thus is also included in MakerEnum
MakerEnum = Enum("MakerEnum", {k: k for k in MakerDict.keys()})  # type: ignore


class ThemeEnum(str, Enum):
    Dark = "dark"
    Light = "light"


def get_theme(theme: ThemeEnum):
    match theme:
        case ThemeEnum.Dark:
            return "#09132b"
        case ThemeEnum.Light:
            return "#ced5e5"
        case _:
            raise ValueError("Invalid theme")


@app.get("/make/{maker_type}")
async def make(
    maker_type: MakerEnum,
    phrase: str = Query(max_length=32),
    theme: ThemeEnum = ThemeEnum.Dark,
):

    try:
        maker = MakerDict[maker_type.name]
    except KeyError:
        raise ValueError("Invalid maker type")

    img = create(phrase, maker, robot_gen, background_color=get_theme(theme))

    with BytesIO() as imgbytes:
        img.save(imgbytes, "png")
        return Response(content=imgbytes.getvalue(), media_type="image/png")
