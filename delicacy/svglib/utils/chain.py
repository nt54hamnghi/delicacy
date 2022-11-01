from typing import Any, Callable, NoReturn, Type, TypeVar

T = TypeVar("T")
V = TypeVar("V")


class ChainableUpdaterError(ValueError):
    ...


class chainable:
    """A descriptor class to chain method calls"""

    _updater_registry: dict[str, Callable[..., None]] = {}

    def __init__(self, target: Callable[..., V]) -> None:
        self.target = target

    def __set_name__(self, owner: Type[T], name: str) -> None:
        self._managed_class = owner.__name__

    def __get__(
        self, instance: T | None = None, owner: Type[T] | None = None
    ):
        if instance is None:
            return self

        if self.target is None:
            raise AttributeError("target method is missing")

        try:
            _updater = self._updater_registry[self._managed_class]
        except AttributeError:
            raise AttributeError("chainable must be used in class definition")
        except KeyError:
            raise AttributeError("updater method is missing")
        else:
            return self(instance, _updater)

    def __set__(self, instance: T, value: Any) -> NoReturn:
        raise AttributeError("setter not available for chainned methods")

    def __call__(
        self, instance: T, _updater: Callable[..., None]
    ) -> Callable[..., T]:
        def chained(*args, **kwds) -> T:
            # append instance in self.target call
            # because when applying chainable as a decorator,
            # the target is passed as an unbound method
            value = self.target(instance, *args, **kwds)
            _updater(instance, value)
            return instance

        return chained

    @classmethod
    def updater(cls, _updater: Callable[..., None]) -> None:
        qualname = _updater.__qualname__.rsplit(".", maxsplit=2)
        try:
            owner_name = qualname[-2]
        except IndexError:
            raise ValueError("_updater must be a bound method")
        else:
            if not owner_name.isidentifier():
                raise ChainableUpdaterError(
                    "fail to identify the managed class"
                )
            cls._updater_registry[owner_name] = _updater
