from config import COLLECTION_DIR

from delicacy.igen.collection import Collection
from delicacy.igen.igen import ImageGenerator


def main():
    robot_collection = Collection("Robot", COLLECTION_DIR / "robot")
    print(robot_collection)

    img_gen = ImageGenerator(robot_collection)
    my_img = img_gen.generate("hamnghi", size=(512, 512), proportion=0.85)
    my_img.show()


def sandbox():
    ...


if __name__ == "__main__":
    # main()
    sandbox()
