import pytest

from delicacy.svglib.utils.transform import Transform


@pytest.fixture
def transform():
    return Transform()


@pytest.mark.parametrize(
    ("x", "y"), ((10, None), (10, 11)), ids=["y-default", "y-argument"]
)
def test_translate(transform, x, y):
    transform = transform.translate(x, y)

    assert isinstance(transform, Transform)
    if y is None:
        assert transform() == "translate({},{})".format(x, 0)
    else:
        assert transform() == "translate({},{})".format(x, y)


@pytest.mark.parametrize(
    ("angle", "x", "y"),
    (
        (45, None, None),
        (45, 10, 10),
    ),
    ids=["xy-default", "xy-argument"],
)
def test_rotate(transform, angle, x, y):
    transform = transform.rotate(angle, x, y)

    assert isinstance(transform, Transform)
    if x is None and y is None:
        assert transform() == f"rotate({angle})"
    else:
        assert transform() == "rotate({},{},{})".format(angle, x, y)


def test_rotate_fail(transform):

    with pytest.raises(ValueError):
        transform.rotate(45, 10)


@pytest.mark.parametrize(
    ("x", "y"), ((10, None), (10, 11)), ids=["y-default", "y-argument"]
)
def test_scale(transform, x, y):
    transform = transform.scale(x, y)

    assert isinstance(transform, Transform)
    if y is None:
        assert transform() == "scale({},{})".format(x, x)
    else:
        assert transform() == "scale({},{})".format(x, y)


def test_skewX(transform):
    transform = transform.skewX(0)
    assert isinstance(transform, Transform)
    assert transform() == "skewX(0)"


def test_skewY(transform):
    transform = transform.skewY(0)
    assert isinstance(transform, Transform)
    assert transform() == "skewY(0)"


def test_matrix(transform):
    transform = transform.matrix(*range(6))
    assert isinstance(transform, Transform)
    assert transform() == "matrix({},{},{},{},{},{})".format(*range(6))


def test_chained_ops(transform):
    transform = (
        transform.translate(5)
        .rotate(45)
        .scale(0.5)
        .skewX(4)
        .skewY(4)
        .matrix(*range(6))
    )

    assert isinstance(transform, Transform)

    expected = "translate(5,0) rotate(45) scale(0.5,0.5) skewX(4) skewY(4) matrix(0,1,2,3,4,5)"  # noqa
    assert transform() == expected
