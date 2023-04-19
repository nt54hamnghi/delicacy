from math import cos
from math import radians
from math import sin
from typing import NamedTuple


class Point(NamedTuple):
    x: float
    y: float

    @classmethod
    def from_polar_radians(cls, radius, theta):
        x = radius * cos(theta)
        y = radius * sin(theta)
        return cls(x, y)

    @classmethod
    def from_polar_degree(cls, radius, degree):
        return cls.from_polar_radians(radius, radians(degree))
