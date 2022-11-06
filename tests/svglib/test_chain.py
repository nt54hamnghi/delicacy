import pytest

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
    Test.patched = chainable(lambda self: "")
    with pytest.raises(AttributeError) as err:
        Test().patched()
    assert str(err.value) == "chainable must be used in class definition"


def test_set_chained_method_fail():
    test = Test()
    with pytest.raises(AttributeError) as err:
        test.method = lambda _: 0
    assert str(err.value) == "setter not available for chained methods"


def test_set_updater_fail():
    test = Test()
    with pytest.raises(AttributeError) as err:
        test._update = lambda _: 0
    assert str(err.value) == "setter not available for updater methods"


def test_mising_updater():
    with pytest.raises(RuntimeError):

        class AnotherTest:
            @chainable
            def another_test(self):
                ...


def test_use_updater_in_non_chainable_class():
    with pytest.raises(RuntimeError):

        class AnotherTest:
            @chainable.updater
            def another_test(self):
                ...


@pytest.mark.parametrize("arg", (None, type(None), 0))
class TestInitFail:
    def test__init__chainable_fail(self, arg):
        with pytest.raises(TypeError) as err:

            class Another:
                attr = chainable(arg)

                @chainable.updater
                def _update(self):
                    ...

        assert str(err.value) == "target must be callable"

    def test__init__updater_fail(self, arg):
        with pytest.raises(TypeError) as err:

            class Another:
                attr = chainable.updater(arg)

        assert str(err.value) == "target must be callable"
