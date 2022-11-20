import pytest
from lxml.etree import tostring

from delicacy.excite.excite import BGMaker, makers
from delicacy.svglib.utils.utils import materialize


@pytest.mark.parametrize("maker", makers)
class TestBGMakerReproducibility:
    def test_bgmaker(self, maker):
        seed = 0

        bg_maker0 = BGMaker(maker, seed=seed)
        bg0 = bg_maker0.generate()

        bg_maker1 = BGMaker(maker, seed=seed)
        bg1 = bg_maker1.generate()

        assert tostring(bg0) == tostring(bg1)
        assert materialize(bg0) == materialize(bg1)

    def test_bgmaker_from_phrase(self, maker):
        phrase = ""

        bg_maker0 = BGMaker.from_phrase(phrase, maker)
        bg0 = bg_maker0.generate()

        bg_maker1 = BGMaker.from_phrase(phrase, maker)
        bg1 = bg_maker1.generate()

        assert tostring(bg0) == tostring(bg1)
        assert materialize(bg0) == materialize(bg1)

    def test_bgmaker_from_phrase_fail(self, maker):
        with pytest.raises(ValueError):
            BGMaker.from_phrase("*" * 33, maker)


def test_bgmaker_fail():
    with pytest.raises(ValueError):
        BGMaker(lambda _: ...)
