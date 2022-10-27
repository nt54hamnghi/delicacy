from functools import partial

from attrs import define

immutable = partial(define, frozen=True)
non_comparable = partial(define, eq=False, order=False)
