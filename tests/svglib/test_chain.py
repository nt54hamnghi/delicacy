import pytest

from delicacy.svglib.utils.chain import ChainableUpdaterError, chainable


class Test:
    __test__ = False

    def __init__(self):
        self._storage = "starting"

    @chainable
    def test(self, value):
        return value

    @chainable
    def another(self):
        return "another"

    @chainable.updater
    def _update_storage(self, value):
        self._storage += f"_{value}"


def test_simple_checks():
    test = Test()
    registed_updater = chainable._updater_registry.get(Test.__name__)

    assert registed_updater is not None
    assert callable(registed_updater)

    assert isinstance(Test.test, chainable)
    assert isinstance(Test.another, chainable)

    assert callable(test.test)
    assert callable(test.another)


def test_chainable_result():
    test = Test()
    assert test._storage == "starting"

    test = test.test("calling_test")
    assert isinstance(test, Test)
    assert test._storage == "starting_calling_test"

    test = test.another()
    assert isinstance(test, Test)
    assert test._storage == "starting_calling_test_another"


def test_disallowed_patching_managed_class():
    # monkey-patch function to the Test class
    Test.patched = chainable(lambda self: "")
    test = Test()
    with pytest.raises(AttributeError) as err:
        test.patched()
    assert str(err.value) == "chainable must be used in class definition"


def test_set_chained_method_fail():
    test = Test()
    with pytest.raises(AttributeError) as err:
        test.test = lambda _: 0
    assert str(err.value) == "setter not available for chainned methods"


def test__get__mising_target():
    test = Test()

    Test.missing_target = chainable(None)

    with pytest.raises(AttributeError) as err:
        test.missing_target()

    assert str(err.value) == "target method is missing"

    del Test.missing_target


def test__get__mising_updater():
    class AnotherTest:
        @chainable
        def another_test(self):
            ...

    atest = AnotherTest()

    with pytest.raises(AttributeError) as err:
        atest.another_test()

    assert str(err.value) == "updater method is missing"


def test_register_updater_fail():
    with pytest.raises(ChainableUpdaterError) as err:
        chainable.updater(lambda _: 0)

    assert str(err.value) == "fail to identify the managed class"
