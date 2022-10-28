import random
from math import cos, radians, sin
from random import Random
from types import ModuleType
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
    def from_polar_degree(cls, radius, theta):
        theta = radians(theta)
        return cls.from_polar_radian(radius, theta)

    @classmethod
    def randpoint(
        cls,
        xlim: tuple[int, int],
        ylim: tuple[int, int],
        fixed_x: bool = False,
        fixed_y: bool = False,
        rng: Random | None = None,
    ) -> "Point":

        _rd: ModuleType | Random = random if rng is None else rng

        x = _rd.choice(xlim) if fixed_x else _rd.randint(*xlim)
        y = _rd.choice(ylim) if fixed_y else _rd.randint(*ylim)

        return cls(x, y)

    def __str__(self) -> str:
        return "({},{})".format(*self)
