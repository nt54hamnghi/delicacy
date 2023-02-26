from delicacy.svglib.elements.use import Use


def test_use_default():
    use = Use("use")

    expected = dict(href="#use", x="0", y="0")

    assert use.base.tag == "use"
    assert use.base.attrib == expected


def test_use_with_size():
    use = Use("use", size=(10, 10))

    expected = dict(href="#use", x="0", y="0")

    assert use.base.tag == "use"
    assert use.base.attrib == expected | dict(width="10", height="10")
