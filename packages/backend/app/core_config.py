from functools import lru_cache

from meridian_core import SearchEngine


@lru_cache(maxsize=1)
def get_engine() -> SearchEngine:
    return SearchEngine()
