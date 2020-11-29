import pytest

from maybe_async import maybe_async

pytestmark = pytest.mark.asyncio


async def test_simple():
    def callback():
        return 42

    async def async_callback():
        return 42

    @maybe_async
    def f(callback):
        return callback()

    assert f(callback) == 42
    assert await f(async_callback) == 42


async def async_f():
    return 1


def sync_f():
    return 2


global_var = 3


async def test_global_vars():
    @maybe_async
    def f():
        return async_f() + sync_f() + global_var

    assert await f() == 6


async def test_nonlocal_vars():
    async def async_f():
        return 1

    def sync_f():
        return 2

    nonlocal_var = 3

    @maybe_async
    def f():
        return async_f() + sync_f() + nonlocal_var

    assert await f() == 6


async def test_method():
    class C:
        @maybe_async
        def method(self, x):
            return x

    assert C().method(123) == 123

    class C:
        @maybe_async
        def method(self, x):
            async_f()
            return x

    assert await C().method(123) == 123


async def test_conditional():
    @maybe_async
    def f(run_async):
        if run_async:
            async_f()
        return 123

    assert f(False) == 123
    assert await f(True) == 123



async def test_nested():
    async def async_f():
        return 123

    def wrapper():
        return async_f()

    @maybe_async
    def f():
        return wrapper()

    assert await f() == 123


async def test_call():
    async def async_f():
        return 123

    def callback(arg):
        return arg

    @maybe_async
    def f():
        return callback(async_f())

    assert await f() == 123


async def test_empty_func():
    @maybe_async
    def f():
        pass

    assert f() is None
