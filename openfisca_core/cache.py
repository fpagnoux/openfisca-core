# -*- coding: utf-8 -*-

from typing import Optional, List, Dict
from collections import defaultdict

from openfisca_core.types import Array
from openfisca_core.periods import Period
from openfisca_core.data_storage import Storage, InMemoryStorage


class Cache:

    def __init__(self) -> None:
        self._storage_by_variable: Dict[str, Storage] = defaultdict(lambda: InMemoryStorage())

    def get_cached_array(self, variable: str, period: Period) -> Optional[Array]:
        return self._storage_by_variable[variable].get(period)

    def put_in_cache(self, variable: str, period: Period, value: Array) -> None:
        self._storage_by_variable[variable].put(value, period)

    def delete_arrays(self, variable: str, period: Optional[Period] = None) -> None:
        self._storage_by_variable[variable].delete(period)

    def get_known_periods(self, variable: str) -> List[Period]:
        pass
