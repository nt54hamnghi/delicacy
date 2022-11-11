import pytest
from cytoolz.dicttoolz import keyfilter
from lxml.etree import Element, tostring

from delicacy.svglib.elements.element import (
    ExtendedElement,
    SVGElement,
    wraps,
)
from delicacy.svglib.elements.peripheral.style import Fill, Stroke
from delicacy.svglib.elements.peripheral.transform import Transform


@pytest.fixture
def element():
    return Element("circle", attrib=dict(cx="10", cy="10", r="20"))


def test_create_SVGElement(element):
    svge = SVGElement.from_etree_element(element)
    assert svge() is element


def test_element_repr(element):
    svge = SVGElement.from_etree_element(element)
    assert svge._element_repr() == repr(element)


def test_element_bytes(element):
    svge = SVGElement.from_etree_element(element)
    assert bytes(svge) == tostring(element, pretty_print=True)


def test_element_str(element):
    svge = SVGElement.from_etree_element(element)
    assert str(svge) == tostring(element, pretty_print=True).decode("utf8")


def test_element_set(element):
    svge = SVGElement.from_etree_element(element)
    svge.set("set", str(...))
    assert svge().get("set") == str(Ellipsis)


def test_element_get(element):
    svge = SVGElement.from_etree_element(element)
    assert svge.get("cx") == "10"


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
def test_ExtendedElement_extract_styles(style_str, style_dict, kind):
    if kind is None:
        assert ExtendedElement.extract_styles(style_str) == style_dict
    else:
        expected = keyfilter(lambda x: kind.lower() in x, style_dict)
        assert ExtendedElement.extract_styles(style_str, kind) == expected


def test_ExtendedElement_extract_styles_fail(style_str):
    with pytest.raises(ValueError) as err:
        ExtendedElement.extract_styles(style_str, kind="")

    assert str(err.value) == "not a valid style"


def test_ExtendedElement_add_style(element):
    ext: ExtendedElement = ExtendedElement.from_etree_element(element)
    stroke = Stroke("white", 1, 5)
    ext.add_style(stroke)

    assert (
        ext().get("style")
        == "stroke: white; stroke-opacity: 1; stroke-width: 5;"
    )


def test_ExtendedElement_apply_styles(style_str, element):
    ext: ExtendedElement = ExtendedElement.from_etree_element(element)
    stroke = Stroke("white", 1, 5)
    fill = Fill("black", 0.8)
    ext.apply_styles(stroke, fill)

    assert ext().get("style") == style_str


def test_ExtendedElement_set_style_normal(element):
    ext: ExtendedElement = ExtendedElement.from_etree_element(element)
    stroke = Stroke("white", 1, 5)
    ext.set_style(stroke)

    assert (
        ext().get("style")
        == "stroke: white; stroke-opacity: 1; stroke-width: 5;"
    )


def test_ExtendedElement_set_style_existing(style_str, element):
    ext: ExtendedElement = ExtendedElement.from_etree_element(element)
    ext.apply_styles(Stroke("white", 1, 5), Fill("black", 0.8))

    ext.set_style(Stroke("orange", 0.5, 0.5))
    assert (
        ext().get("style")
        == "stroke: orange; stroke-opacity: 0.5; stroke-width: 0.5; fill: black; fill-opacity: 0.8;"  # noqa
    )

    ext.set_style(Fill("orange", 0.5))
    assert (
        ext().get("style")
        == "fill: orange; fill-opacity: 0.5; stroke: orange; stroke-opacity: 0.5; stroke-width: 0.5;"  # noqa
    )


def test_ExtendedElement_add_transform(element):
    ext: ExtendedElement = ExtendedElement.from_etree_element(element)
    transform = Transform().translate(5).rotate(45).scale(5)
    ext.add_transform(transform)
    expected = "translate(5,0) rotate(45) scale(5,5)"
    assert ext().get("transform") == expected


def test_ExtendedElement_add_transform_fail(element):
    transform = Transform()
    ext: ExtendedElement = ExtendedElement.from_etree_element(element)

    with pytest.raises(ValueError) as err:
        ext.add_transform(transform)

    assert str(err.value) == "empty transform"


@pytest.mark.parametrize(
    ("tag", "extended"), (("defs", False), ("g", True), ("symbol", True))
)
def test_wraps(tag, extended):
    childs = []
    for i in range(10):
        elm = Element("circle", attrib=dict(r=f"{i}"))
        childs.append(ExtendedElement.from_etree_element(elm))
    wrapped = wraps(tag, *childs, extended=extended)

    assert wrapped().tag == tag
    assert len(wrapped()) == 10

    for c, w in zip(childs, wrapped()):
        assert c() is w

    if extended:
        assert type(wrapped) is ExtendedElement
    else:
        assert type(wrapped) is SVGElement
