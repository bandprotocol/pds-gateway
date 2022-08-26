from app.utils import cache
from pytimeparse.timeparse import timeparse
import pytest
import time

CACHE_CAPACITY = 3
TTL_TIME = "1s"


@pytest.fixture
def cache_data():
    return cache.Cache(CACHE_CAPACITY, timeparse(TTL_TIME))


def test_normal_cache_data(cache_data):
    cache_data.set_data(hash("1"), {"a": "b"})
    assert cache_data.get_data(hash("1")) == {"a": "b"}


def test_cache_data_same_hash(cache_data):
    cache_data.set_data(hash("1"), "data 1 ...")
    assert cache_data.get_data(hash("1")) == "data 1 ..."

    cache_data.set_data(hash("1"), "data 2 ...")
    assert cache_data.get_data(hash("1")) == "data 2 ..."


def test_cache_data_out_of_capacity(cache_data):
    cache_data.set_data(hash("1"), "data 1 ...")
    cache_data.set_data(hash("2"), "data 2 ...")
    cache_data.set_data(hash("3"), "data 3 ...")
    cache_data.set_data(hash("4"), "data 4 ...")

    assert cache_data.get_data(hash("1")) == None


def test_cache_data_not_found(cache_data):
    assert cache_data.get_data(hash("99")) == None


def test_cache_data_expire(cache_data):
    cache_data.set_data(hash("1"), "data ...")
    time.sleep(1.1)

    assert cache_data.get_data(hash("1")) == None
