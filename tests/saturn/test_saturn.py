import pytest
from cytoolz.functoolz import identity
from lxml.etree import tostring

from delicacy.saturn.saturn import BackgroundMaker, MakerDict
from delicacy.svglib.utils.utils import materialize


@pytest.mark.parametrize("maker", MakerDict.values())
class TestBGMakerReproducibility:
    @pytest.mark.parametrize("seed", range(2))
    def test_bgmaker(self, maker, seed):

        first_bg = BackgroundMaker(maker, seed=seed).generate()
        second_bg = BackgroundMaker(maker, seed=seed).generate()

        assert tostring(first_bg) == tostring(second_bg)
        assert materialize(first_bg) == materialize(second_bg)

    @pytest.mark.parametrize("phrase", ("random", "hash"))
    def test_bgmaker_from_phrase(self, maker, phrase):

        first_bg = BackgroundMaker.from_phrase(phrase, maker).generate()
        second_bg = BackgroundMaker.from_phrase(phrase, maker).generate()

        assert tostring(first_bg) == tostring(second_bg)
        assert materialize(first_bg) == materialize(second_bg)

    def test_bgmaker_from_phrase_fail(self, maker):
        with pytest.raises(ValueError):
            BackgroundMaker.from_phrase("*" * 33, maker)


def test_bgmaker_create_fail():
    with pytest.raises(ValueError):
        BackgroundMaker(identity)


def test_bgmaker_from_phrase_fail():
    with pytest.raises(ValueError):
        BackgroundMaker.from_phrase("random", identity)
