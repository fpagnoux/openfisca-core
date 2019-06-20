# -*- coding: utf-8 -*-

from typing import Optional, List

from openfisca_core.types import Array
from openfisca_core.periods import Period

class Cache:

    def get_cached_array(self, variable_name: str, period: Period) -> Optional[Array]:
        pass

    def put_in_cache(self, variable_name: str, period: Period, value: Array) -> None:
        pass

    def delete_arrays(self, variable_name: str, period: Optional[Period] = None) -> None:
        pass

    def get_known_periods(self, variable_name: str) -> List[Period]:
        pass
