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
from enum import Enum
from io import BytesIO

from fastapi import FastAPI
from fastapi import Query
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

cat_path = COLLECTION_DIR / "cat"
cat_collection = Collection("Cat", cat_path)
cat_gen = ImageGenerator(cat_collection)

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
    phrase: str = Query(max_length=128),
    theme: ThemeEnum = ThemeEnum.Dark,
):
    try:
        maker = MakerDict[maker_type.name]
    except KeyError:
        raise ValueError("Invalid maker type")

    img = create(
        phrase,
        maker,
        cat_gen,
        background_color=get_theme(theme),
    )

    with BytesIO() as imgbytes:
        img.save(imgbytes, "png")
        return Response(content=imgbytes.getvalue(), media_type="image/png")
