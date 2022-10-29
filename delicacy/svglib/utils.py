from operator import methodcaller
from types import MethodType
from typing import NamedTuple

from decorator import decorator
from lxml import etree
from lxml.etree import Element, _Element


def eprint(element: _Element) -> None:
    msg = etree.tostring(element, pretty_print=True).decode("utf8")
    print(msg)


def get_canvas(
    width: float = 512, height: float = 512, **kwds: str
) -> _Element:
    tag = dict(
        width=str(width),
        height=str(height),
        xmlns="http://www.w3.org/2000/svg",
    )
    tag |= kwds
    nsmap = dict(xlink="http://www.w3.org/1999/xlink")
    return Element("svg", attrib=tag, nsmap=nsmap)


@decorator
def chainable(method: MethodType, updater: str = "_update", *args, **kwds):
    self = args[0]
    value = method(*args, **kwds)
    methodcaller(updater, value)(self)
    return self


class Size(NamedTuple):
    width: int
    height: int
