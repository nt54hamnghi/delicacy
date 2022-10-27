import hashlib

from config import COLLECTION_DIR, ROOT_DIR


def main():
    print(ROOT_DIR)
    print(COLLECTION_DIR)
    print(type(hashlib.sha512))


if __name__ == "__main__":
    main()
