import pytest

from delicacy.svglib.colors.hsv import HSVColor


@pytest.mark.parametrize(
    "hsv",
    ((1, 50, 50), (361, 50, 50), (1.5, 50.75, 50.75)),
    ids=["normal", "overflow", "float"],
)
class TestParametrized:
    def test_create_hsv_color(self, hsv):
        hue, sat, val = HSVColor(*hsv)

        assert hue == 1
        assert sat == 50
        assert val == 50

    def test_normalize(self, hsv):
        hsv = HSVColor(*hsv)

        assert all(0 <= c <= 1 for c in hsv.normalize())

    def test_to_rgb(self, hsv):
        hsv = HSVColor(*hsv)

        assert all(0 <= c <= 1 for c in hsv.to_rgb(False))

    def test_to_rgb_normalized(self, hsv):
        hsv = HSVColor(*hsv)

        assert all(0 <= c <= 255 for c in hsv.to_rgb(True))

    def test_to_hex(self, hsv):
        result = HSVColor(*hsv).to_hex()
        expected = "#7f403f"

        assert result == expected


@pytest.mark.parametrize("argument", (-1, 101))
def test_create_hsv_fail(argument):
    with pytest.raises(ValueError) as err:
        HSVColor(0, argument, 0)
    assert str(err.value) == "invalid saturation, must be in [0, 100]"

    with pytest.raises(ValueError) as err:
        HSVColor(0, 0, argument)
    assert str(err.value) == "invalid value, must be in [0, 100]"
