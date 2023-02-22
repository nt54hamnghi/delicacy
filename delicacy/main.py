from enum import Enum
from io import BytesIO

from fastapi import FastAPI, Query
from fastapi.responses import Response

from delicacy.config import COLLECTION_DIR
from delicacy.excite.excite import ExAid, Genm, ParaDX
from delicacy.generate import generate
from delicacy.igen.collection import Collection
from delicacy.igen.igen import ImageGenerator

app = FastAPI()


robot_path = COLLECTION_DIR / "robot"
robot_collection = Collection("Robot", robot_path)
robot_gen = ImageGenerator(robot_collection)


class MakerType(str, Enum):
    exaid = "exaid"
    genm = "genm"
    paradx = "paradx"


@app.get("/make/{maker_type}")
async def make(maker_type: MakerType, phrase: str = Query(max_length=32)):

    match maker_type:
        case maker_type.exaid:
            maker = ExAid
        case maker_type.genm:
            maker = Genm
        case maker_type.paradx:
            maker = ParaDX
        case _:
            raise ValueError("invalid maker_typeType")

    img = generate(phrase, maker, robot_gen)

    with BytesIO() as imgbytes:
        img.save(imgbytes, "png")
        return Response(content=imgbytes.getvalue(), media_type="image/png")
