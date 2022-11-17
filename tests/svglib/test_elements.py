import pytest
from cytoolz.dicttoolz import keyfilter
from lxml.etree import Element, _Element, tostring

from delicacy.svglib.elements.element import (
    ExtendedElement,
    SVGElement,
    WrappingElement,
    wraps,
)
from delicacy.svglib.elements.peripheral.style import Fill, Stroke
from delicacy.svglib.elements.peripheral.transform import Transform


@pytest.fixture
def element():
    return Element("circle", attrib=dict(cx="10", cy="10", r="20"))


@pytest.mark.parametrize("cls", (SVGElement, ExtendedElement))
def test_create_fail(cls, element):
    with pytest.raises(TypeError):
        cls(element)


class TestElement(ExtendedElement):
    __test__ = False

    def __init__(self, element: _Element) -> "TestElement":
        self._element = element

    def __attrs_post_init__(self) -> None:
        ...


@pytest.fixture
def toy(element):
    return TestElement(element)


def test_create_toyElement(toy):
    assert isinstance(toy, ExtendedElement)


def test_element_repr(element, toy):
    assert toy._element_repr() == repr(element)


def test_element_bytes(element, toy):
    assert bytes(toy) == tostring(element, pretty_print=True)


def test_element_str(element, toy):
    expected = tostring(element, pretty_print=True).decode("utf8")
    assert str(toy) == expected


def test_element_set(toy):
    toy.set("set", str(...))
    assert toy.base.get("set") == str(Ellipsis)


def test_element_get(toy):
    assert toy.get("cx") == "10"


@pytest.fixture
def style_str():
    return "stroke: white; stroke-opacity: 1; stroke-width: 5; fill: black; fill-opacity: 0.8;"  # noqa


@pytest.fixture
def style_dict():
    return {
        "stroke": "white",
        "stroke-opacity": "1",
        "stroke-width": "5",
        "fill": "black",
        "fill-opacity": "0.8",
    }


@pytest.mark.parametrize(
    "kind",
    (None, "stroke", "fill", "Stroke", "FILL"),
)
def test_extract_styles(style_str, style_dict, kind):
    if kind is None:
        assert TestElement.extract_styles(style_str) == style_dict
    else:
        expected = keyfilter(lambda x: kind.lower() in x, style_dict)
        assert TestElement.extract_styles(style_str, kind) == expected


def test__extract_styles_fail(style_str):
    with pytest.raises(ValueError) as err:
        TestElement.extract_styles(style_str, kind="")

    assert str(err.value) == "not a valid style"


def test_add_style(toy):
    stroke = Stroke("white", 1, 5)
    toy.add_style(stroke)

    expected = "stroke: white; stroke-opacity: 1; stroke-width: 5;"

    assert toy.base.get("style") == expected


def test_apply_styles(style_str, toy):
    toy.apply_styles(Stroke("white", 1, 5), Fill("black", 0.8))
    assert toy.base.get("style") == style_str


def test_set_style_normal(toy):
    stroke = Stroke("white", 1, 5)
    toy.set_style(stroke)
    expected = "stroke: white; stroke-opacity: 1; stroke-width: 5;"

    assert toy.base.get("style") == expected


def test_set_style_existing(toy):
    toy.apply_styles(Stroke("white", 1, 5), Fill("black", 0.8))

    toy.set_style(Stroke("orange", 0.5, 0.5))
    expected = "stroke: orange; stroke-opacity: 0.5; stroke-width: 0.5; fill: black; fill-opacity: 0.8;"  # noqa
    assert toy.base.get("style") == expected

    toy.set_style(Fill("orange", 0.5))
    expected = "fill: orange; fill-opacity: 0.5; stroke: orange; stroke-opacity: 0.5; stroke-width: 0.5;"  # noqa
    assert toy.base.get("style") == expected


def test_add_transform(toy):
    transform = Transform().translate(5).rotate(45).scale(5)
    toy.add_transform(transform)
    expected = "translate(5,0) rotate(45) scale(5,5)"
    assert toy.base.get("transform") == expected


def test_add_transform_fail(toy):
    transform = Transform()

    with pytest.raises(ValueError) as err:
        toy.add_transform(transform)

    assert str(err.value) == "empty transform"


@pytest.mark.parametrize("tag", ("defs", "g", "symbol"))
class TestWrappingElement:
    @pytest.fixture
    def childs(self):
        childs = []
        for i in range(10):
            elm = Element("circle", attrib=dict(r=f"{i}"))
            childs.append(TestElement(elm))
        return childs

    def test_create(self, tag):
        wrap = WrappingElement(tag)
        assert wrap.base.tag == tag

    def test_create_with_kwds(self, tag):
        attrib = dict(id="id", name="name")
        wrap = WrappingElement(tag, **attrib)
        assert wrap.base.attrib == attrib

    def test_call(self, tag, childs):

        wrap = WrappingElement(tag)
        wrap(*childs)

        assert len(wrap.base) == 10

        for c, w in zip(childs, wrap.base):
            assert c.base is w

    def test_call_with_kwds(self, tag, childs):

        attrib = dict(id="id", name="name")
        wrap = WrappingElement(tag)
        wrap(*childs, **attrib)

        assert len(wrap.base) == 10
        assert wrap.base.attrib == attrib

    def test_create_wraps(self, tag):
        wrp_0 = wraps(tag)
        wrp_1 = wraps(tag)

        assert wrp_0 is not wrp_1
        assert isinstance(wrp_0, WrappingElement)
        assert isinstance(wrp_1, WrappingElement)
