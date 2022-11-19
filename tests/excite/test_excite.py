from itertools import product
from random import choices
from delicacy.excite.excite import BGMaker, makers

import pytest
from lxml.etree import tostring

from delicacy.svglib.utils.utils import svg2img


@pytest.mark.parametrize(
    ("maker", "seed"),
    product(makers, choices(range(2**32), k=4)),
)
def test_bgmaker_reproducible(maker, seed):
    bg_maker0 = BGMaker(maker, seed=seed)
    bg0 = tostring(bg_maker0.generate())

    bg_maker1 = BGMaker(maker, seed=seed)
    bg1 = tostring(bg_maker1.generate())

    assert bg0 == bg1
    assert svg2img(bg0) == svg2img(bg1)


def test_bgmaker_fail():
    with pytest.raises(ValueError):
        BGMaker(lambda _: ...)
