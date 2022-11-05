import random
from colorsys import hsv_to_rgb
from typing import NamedTuple


class RGBColor(NamedTuple):
    red: int
    green: int
    blue: int

    @staticmethod
    def _clamp(x):
        """
        _clamp ensures that 0 <= {r,g,b} <= 255
        https://stackoverflow.com/a/3380754
        """
        return max(0, min(x, 255))

    def to_hex(self):
        """
        convert rgb to hex representation
        https://stackoverflow.com/a/3380754
        """
        r, g, b = tuple(self._clamp(c) for c in self)
        return f"#{r:02x}{g:02x}{b:02x}"

    @classmethod
    def from_iterable(cls, it):
        return cls(*it)

    @classmethod
    def from_hex(cls, hexstring: str):
        _len = len(hexstring)

        if _len != 7:
            raise ValueError("Invalid hex color")

        hexstring = hexstring.lstrip("#")

        return cls.from_iterable(
            int(hexstring[i : (i + 2)], 16)  # noqa
            for i in range(0, _len - 1, 2)
        )

    @classmethod
    def randcolor(cls, style="normal"):
        available_styles = ("pastel", "neon", "normal")

        if style not in available_styles:
            raise ValueError(f"style must be one of: {available_styles}")

        if style == "neon":
            h, s, v = random.random(), 1, 1
        elif style == "pastel":
            h, s, v = random.random(), random.random(), 1
        else:
            h, s, v = tuple(random.random() for _ in range(3))

        return cls.from_iterable(int(c * 255) for c in hsv_to_rgb(h, s, v))
