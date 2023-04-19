from typing import Any

from delicacy.svglib.utils.chain import chainable


class Transform:
    def __init__(self):
        self._storage = ""

    @chainable.updater
    def _update(self, value: Any) -> None:
        self._storage += value

    @chainable
    def translate(self, x: float, y: float | None = None) -> str:
        y = 0 if y is None else y
        return f" translate({x},{y})"

    @chainable
    def rotate(
        self, angle: float, x: float | None = None, y: float | None = None
    ) -> str:
        if x is None and y is None:
            return f" rotate({angle})"
        elif (x is None) ^ (y is None):
            msg = "x and y must either have values or be None simutanously"
            raise ValueError(msg)
        else:
            return f" rotate({angle},{x},{y})"

    @chainable
    def scale(self, x: float, y: float | None = None) -> str:
        y = x if y is None else y
        return f" scale({x},{y})"

    @chainable
    def skewX(self, x: int) -> str:
        return f" skewX({x})"

    @chainable
    def skewY(self, y: int) -> str:
        return f" skewY({y})"

    @chainable
    def matrix(self, a: float, b: float, c: float, d: float, e: float, f: float) -> str:
        return f" matrix({a},{b},{c},{d},{e},{f})"

    def __call__(self) -> str:
        return self._storage.lstrip()
