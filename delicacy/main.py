from enum import Enum
from io import BytesIO

from fastapi import FastAPI, Query
from fastapi.responses import Response

from delicacy.config import COLLECTION_DIR
from delicacy.excite.excite import MakerDict
from delicacy.generate import generate
from delicacy.igen.collection import Collection
from delicacy.igen.igen import ImageGenerator

app = FastAPI()


robot_path = COLLECTION_DIR / "robot"
robot_collection = Collection("Robot", robot_path)
robot_gen = ImageGenerator(robot_collection)


# workaround to dynamically create a StrEnum from a dictionary's keys
MakerNames = tuple(MakerDict.keys())
MakerEnum = Enum("MakerEnum", dict(zip(MakerNames, MakerNames)))  # type: ignore


@app.get("/make/{maker_type}")
async def make(maker_type: MakerEnum, phrase: str = Query(max_length=32)):

    try:
        maker = MakerDict[maker_type.name]
    except KeyError:
        raise ValueError("invalid maker_typeType")

    img = generate(phrase, maker, robot_gen)

    with BytesIO() as imgbytes:
        img.save(imgbytes, "png")
        return Response(content=imgbytes.getvalue(), media_type="image/png")
