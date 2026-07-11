import pytest

from meridian_core.filters import SearchFilters, normalize_domain


def test_domain_filter_normalizes_full_url() -> None:
    filters = SearchFilters(include_domains=["https://www.tiktok.com"])
    assert filters.include_domains == ["tiktok.com"]


def test_bare_domain_passes_through() -> None:
    assert normalize_domain("example.com") == "example.com"


def test_malformed_domain_raises_clear_error() -> None:
    with pytest.raises(ValueError, match="Invalid domain"):
        normalize_domain("not a domain")
