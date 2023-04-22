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
from collections.abc import Callable
from typing import NoReturn
from typing import TypeVar

from cytoolz.dicttoolz import valfilter

T = TypeVar("T")


class _updater:
    def __init__(self, target: Callable) -> None:
        # checking against type(None) to avoid NoneType callable
        if not callable(target) or target is type(None):  # noqa
            raise TypeError("target must be callable")

        self.target = target

    def __set_name__(self, owner: type, name: str) -> None:
        chains = valfilter(lambda x: isinstance(x, chainable), owner.__dict__)

        if len(chains) == 0:
            msg = "_updater cannot be used with non-chainable classes"
            raise ValueError(msg)

    def __set__(self, instance, value) -> NoReturn:
        raise AttributeError("setter not available for updater methods")

    def __get__(self, instance: T | None = None, owner: type[T] | None = None):
        if instance is None:
            return self

        return self.target


class chainable:
    """A descriptor to chain method calls"""

    # reference to _updater descriptor class to expose it through chainable
    updater = _updater

    def __init__(self, target: Callable) -> None:
        # checking against type(None) to avoid NoneType callable
        if not callable(target) or target is type(None):  # noqa
            raise TypeError("target must be callable")

        self.target = target
        self.managed_updater = None

    def __set_name__(self, owner: type, name: str) -> None:
        ups = valfilter(lambda x: isinstance(x, _updater), owner.__dict__)

        if len(ups) != 1:
            msg = "each chainable class has one and only one updater"
            raise ValueError(msg)

        self.managed_updater = tuple(ups.values())[0]

    def __set__(self, instance, value) -> NoReturn:
        raise AttributeError("setter not available for chained methods")

    def __get__(self, instance: T | None = None, owner: type[T] | None = None):
        if instance is None:
            return self

        # invoke self.__call__ to get a chainable method and return it
        return self(instance)

    def __call__(self, instance: T) -> Callable[..., T]:
        # this will replace the decorated target in chainable classes
        def chained_method(*args, **kwds) -> T:
            # prepend instance in self.target call
            # because target is passed as a function
            value = self.target(instance, *args, **kwds)

            # use chainable in class definition allows __set_name__ to run
            # __set_name__ is responisble for initialzing managed_updater
            # otherwise managed_updater is None
            if self.managed_updater is None:
                msg = "chainable must be used in class definition"
                raise AttributeError(msg)

            # call __get__ to retrieve the underlying method
            self.managed_updater.__get__(instance)(instance, value)  # type: ignore

            return instance

        return chained_method
