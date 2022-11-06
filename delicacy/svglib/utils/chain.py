from collections.abc import Callable
from typing import NoReturn, TypeVar

from cytoolz.dicttoolz import valfilter  # type: ignore

T = TypeVar("T")


class _updater:
    """A descriptor class to chain method calls"""

    def __init__(self, target: Callable) -> None:
        # checking against type(None) to avoid NoneType callable
        if not callable(target) or target is type(None):  # noqa
            raise TypeError("target must be callable")

        self.target = target

    def __set_name__(self, owner: type, name: str) -> None:
        chains = valfilter(lambda x: isinstance(x, chainable), owner.__dict__)

        if len(chains) == 0:
            msg = "_updater cannot be used with non-chainable class"
            raise ValueError(msg)

    def __set__(self, instance, value) -> NoReturn:
        raise AttributeError("setter not available for updater methods")

    def __get__(self, instance: T = None, owner: type[T] | None = None):
        if instance is None:
            return self

        return self.target


class chainable:
    """A descriptor class to chain method calls"""

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
            msg = "each chainable class can have one and only one updater"
            raise ValueError(msg)

        self.managed_updater = tuple(ups.values())[0]

    def __set__(self, instance, value) -> NoReturn:
        raise AttributeError("setter not available for chained methods")

    def __get__(self, instance: T = None, owner: type[T] | None = None):
        if instance is None:
            return self

        return self(instance)

    def __call__(self, instance: T) -> Callable[..., T]:
        def chained(*args, **kwds) -> T:
            # prepend instance in self.target call
            # because the decorated target is passed as a function
            value = self.target(instance, *args, **kwds)

            try:
                # call __get__ to retrieve the underlying method
                self.managed_updater.__get__(instance)(instance, value)
            except AttributeError as err:
                raise type(err)("chainable must be used in class definition")

            return instance

        return chained
