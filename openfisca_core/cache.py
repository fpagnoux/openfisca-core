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

    def get_memory_usage(self, variables: Optional[List[str]] = None):
        usage_by_variable = {
            variable: storage.get_memory_usage()
            for variable, storage in self._storage_by_variable.items()
            if variables is None or variable in variables
        }

        total_nb_bytes = sum(
            variable_usage['total_nb_bytes']
            for variable_usage in usage_by_variable.values()
        )
        return {
            'by_variable': usage_by_variable,
            'total_nb_bytes': total_nb_bytes,
            }


    def get_known_periods(self, variable: str) -> List[Period]:
        pass
