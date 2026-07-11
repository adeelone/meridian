from meridian_core.filters import SearchFilters, normalized_cache_key


def test_equivalent_domain_filters_share_cache_key() -> None:
    a = SearchFilters(include_domains=["https://www.tiktok.com"])
    b = SearchFilters(include_domains=["tiktok.com"])
    assert normalized_cache_key("search", "query", a) == normalized_cache_key("search", "query", b)
