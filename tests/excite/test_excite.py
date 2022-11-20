from itertools import product
from random import choices

import pytest
from lxml.etree import tostring

from delicacy.excite.excite import BGMaker, makers
from delicacy.svglib.utils.utils import materialize


@pytest.mark.parametrize(
    ("maker", "seed"),
    product(makers, choices(range(2**32), k=4)),
)
def test_bgmaker_reproducible(maker, seed):
    bg_maker0 = BGMaker(maker, seed=seed)
    bg0 = bg_maker0.generate()

    bg_maker1 = BGMaker(maker, seed=seed)
    bg1 = bg_maker1.generate()

    assert tostring(bg0) == tostring(bg1)
    assert materialize(bg0) == materialize(bg1)


def test_bgmaker_fail():
    with pytest.raises(ValueError):
        BGMaker(lambda _: ...)
