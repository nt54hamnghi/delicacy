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
def test_init_not_accept_agrument(cls, element):
    with pytest.raises(TypeError):
        cls(element)


class TestElement(ExtendedElement):
    __test__ = False

    def __init__(self, element: _Element):
        self._element = element

    def __attrs_post_init__(self) -> None:  # pragma: no cover
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


def test_element_len(toy):
    assert len(toy) == 0


def test_element_set(toy):
    toy.set("ellipsis", str(...))

    assert toy.base.get("ellipsis") == str(...)


def test_element_get(toy):
    assert toy.get("cx") == "10"


@pytest.fixture
def style_str():
    stroke, fill = Stroke(), Fill()
    return f"{stroke} {fill}"


@pytest.fixture
def style_dict():
    stroke, fill = Stroke(), Fill()
    return stroke.to_dict() | fill.to_dict()


def test_empty_style_property(toy):
    assert toy.style == {}


def test_add_style(toy):
    stroke = Stroke()
    toy.add_style(stroke)

    assert toy.style == stroke.to_dict()
    assert toy.get("style") == str(stroke)


def test_apply_styles(toy, style_dict, style_str):
    stroke, fill = Stroke(), Fill()
    toy.apply_styles(stroke, fill)

    assert toy.style == style_dict
    assert toy.get("style") == style_str


def test_set_style_normal(toy):
    white_stroke = Stroke("white")
    toy.set_style(white_stroke)

    assert toy.style == white_stroke.to_dict()
    assert toy.get("style") == str(white_stroke)


def test_set_style_existing_stroke(toy):
    stroke, fill = Stroke(), Fill()
    toy.apply_styles(stroke, fill)

    orange_stroke = Stroke("orange", 0.5, 0.5)
    toy.set_style(orange_stroke)

    assert toy.style == orange_stroke.to_dict() | fill.to_dict()
    assert toy.get("style") == f"{orange_stroke} {fill}"

    orange_fill = Fill("orange", 0.5, "nonzero")
    toy.set_style(orange_fill)

    assert toy.style == orange_fill.to_dict() | orange_stroke.to_dict()
    assert toy.get("style") == f"{orange_fill} {orange_stroke}"


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
        wrapper = WrappingElement(tag)
        wrapper(*childs)

        assert len(wrapper) == 10

        for c, w in zip(childs, wrapper.base):
            assert c.base is w

    def test_call_with_kwds(self, tag, childs):

        attrib = dict(id="id", name="name")
        wrap = WrappingElement(tag)
        wrap(*childs, **attrib)

        assert len(wrap.base) == 10
        assert wrap.base.attrib == attrib

    def test_create_wraps(self, tag):
        wrap_0 = wraps(tag)
        wrap_1 = wraps(tag)

        assert wrap_0 is not wrap_1
        assert isinstance(wrap_0, WrappingElement)
        assert isinstance(wrap_1, WrappingElement)

    def test_append(self, tag, childs):
        wrapper = WrappingElement(tag)
        for child in childs:
            wrapper.append(child)

        assert len(wrapper) == len(childs)
