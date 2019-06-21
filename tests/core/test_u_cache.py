from pytest import fixture
from numpy import asarray as array
from numpy.testing import assert_equal

from openfisca_core.cache import Cache
from openfisca_core import periods

period = periods.period(2018)


@fixture
def cache():
    return Cache()


def test_does_not_retrieve(cache):
    value = cache.get_cached_array('toto', period)
    assert value is None


def test_retrieve(cache):
    value_to_cache = array([10, 20])
    cache.put_in_cache('toto', period, value_to_cache)
    value_from_cache = cache.get_cached_array('toto', period)
    assert_equal(value_to_cache, value_from_cache)


def test_delete(cache):
    value_to_cache = array([10, 20])
    cache.put_in_cache('toto', period, value_to_cache)
    cache.delete_arrays('toto', period)
    value_from_cache = cache.get_cached_array('toto', period)
    assert value_from_cache is None


def test_retrieve_eternity(cache):
    value_to_cache = array([10, 20])
    cache.put_in_cache('toto', periods.ETERNITY_PERIOD, value_to_cache)
    value_from_cache = cache.get_cached_array('toto', period)
    assert_equal(value_to_cache, value_from_cache)


def test_get_memory_usage(cache):
    value_1 = array([10, 20])
    value_2 = array([30, 40])
    value_3 = array([50, 60])

    cache.put_in_cache('toto', period, value_1)
    cache.put_in_cache('toto', period.last_month, value_2)
    cache.put_in_cache('tata', period.last_month, value_3)

    memory_usage = cache.get_memory_usage()

    assert memory_usage['total_nb_bytes'] > 0
    assert len(memory_usage['by_variable']) == 2

    usage_toto = memory_usage['by_variable']['toto']

    assert usage_toto['total_nb_bytes'] > 0
    assert usage_toto['nb_arrays'] == 2
    assert usage_toto['nb_cells_by_array'] == 2
    assert usage_toto['cell_size'] > 0
