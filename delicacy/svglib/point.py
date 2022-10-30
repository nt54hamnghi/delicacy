import random
from math import cos, radians, sin
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

    @classmethod
    def randpoint(
        cls,
        xlim: tuple[int, int] = (0, 512),
        ylim: tuple[int, int] = (0, 512),
        fixed_x: bool = False,
        fixed_y: bool = False,
    ) -> "Point":

        x = random.choice(xlim) if fixed_x else random.randint(*xlim)
        y = random.choice(ylim) if fixed_y else random.randint(*ylim)

        return cls(x, y)


def rand_points(
    num: int,
    xlim: tuple[int, int],
    ylim: tuple[int, int],
    seed: int | None = None,
):
    if seed is not None:
        random.seed(seed)

    yield from (Point.randpoint(xlim, ylim) for _ in range(num))


def rand_bounded_points(
    num: int,
    xlim: tuple[int, int],
    ylim: tuple[int, int],
    seed: int | None = None,
):
    """
    generate random points whose x and y are randomly bounded to the limit
    """

    if seed is not None:
        random.seed(seed)

    fxs = random.choices([True, False], k=num)  # fixed flags for x
    fys = random.choices([True, False], k=num)  # fixed flags for y

    for _, fx, fy in zip(range(num), fxs, fys):
        yield Point.randpoint(xlim, ylim, fx, fy)
