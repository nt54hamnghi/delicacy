from collections import namedtuple
from colorsys import hsv_to_rgb
from typing import TypeVar

T = TypeVar("T")

HUE_MIN, HUE_MAX = HUE_RANGE = (0, 360)
SAT_MIN, SAT_MAX = SATURATION_RANGE = (0, 100)
VAL_MIN, VAL_MAX = VALUE_RANGE = (0, 100)


# subclass namedtuple to override __new__,
# which is not allowed with NamedTuple.
class HSVColor(namedtuple("HSVColor", ["hue", "sat", "val"])):
    __slots__ = ()

    def __new__(cls: type[T], hue: float, sat: float, val: float) -> T:
        if not SAT_MIN <= sat <= SAT_MAX:
            raise ValueError("invalid saturation, must be in [0, 100]")
        if not VAL_MIN <= val <= VAL_MAX:
            raise ValueError("invalid value, must be in [0, 100]")

        return super().__new__(cls, int(hue % HUE_MAX), int(sat), int(val))

    def normalize(self) -> tuple[float, float, float]:
        hue, sat, val = self
        return (hue / HUE_MAX, sat / SAT_MAX, val / VAL_MAX)

    def to_rgb(self, normalize: bool = True) -> tuple:
        rgb = hsv_to_rgb(*self.normalize())
        if normalize:
            return tuple(int(c * 255) for c in rgb)
        return rgb

    def to_hex(self) -> str:
        # https://stackoverflow.com/a/3380754
        return "#{0:02x}{1:02x}{2:02x}".format(*self.to_rgb())
