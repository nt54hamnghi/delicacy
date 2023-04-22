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
