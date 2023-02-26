import pytest
from cytoolz.functoolz import identity

from delicacy.svglib.utils.chain import chainable


class Test:
    __test__ = False

    def __init__(self):
        self._storage = "starting"

    @chainable
    def method(self, value):
        return value

    @chainable
    def another_method(self):
        return "another"

    @chainable.updater
    def _update(self, value):
        self._storage += f"_{value}"


def test_simple_checks():
    test = Test()

    assert isinstance(Test.method, chainable)
    assert isinstance(Test.another_method, chainable)
    assert isinstance(Test._update, chainable.updater)

    assert callable(test.method)
    assert callable(test.another_method)


def test_chainable_result():
    test = Test()

    test = test.method("method")
    assert isinstance(test, Test)
    assert test._storage == "starting_method"

    test = test.another_method()
    assert isinstance(test, Test)
    assert test._storage == "starting_method_another"


def test_disallowed_patching_managed_class():
    # monkey-patch function to the Test class
    Test.patched = chainable(identity)
    with pytest.raises(AttributeError) as err:
        Test().patched()
    assert str(err.value) == "chainable must be used in class definition"


def test_set_chained_method_fail():
    test = Test()
    with pytest.raises(AttributeError) as err:
        test.method = identity
    assert str(err.value) == "setter not available for chained methods"


def test_set_updater_fail():
    test = Test()
    with pytest.raises(AttributeError) as err:
        test._update = identity
    assert str(err.value) == "setter not available for updater methods"


def test_mising_updater():
    # raise error inside __set_name__ will trigger RuntimeError
    with pytest.raises(RuntimeError):

        class _:
            method = chainable(identity)


def test_use_updater_in_non_chainable_class():
    # raise error inside __set_name__ will trigger RuntimeError
    with pytest.raises(RuntimeError):

        class _:
            updater_method = chainable.updater(identity)


@pytest.mark.parametrize("argument", (None, type(None), 0))
class TestInitFailNonCallable:
    def test__init__chainable_fail(self, argument):
        with pytest.raises(TypeError) as err:

            class _:
                method = chainable(argument)

        assert str(err.value) == "target must be callable"

    def test__init__updater_fail(self, argument):
        with pytest.raises(TypeError) as err:

            class _:
                method = chainable.updater(argument)

        assert str(err.value) == "target must be callable"
