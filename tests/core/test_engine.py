from meridian_core import SearchEngine
from meridian_core.cache.sqlite_backend import SQLiteCacheBackend
from meridian_core.collections import CollectionStore
from meridian_core.history import HistoryStore
from meridian_core.quota import QuotaTracker, TokenBucket
from tests.helpers import state_dir


class FakeResponse:
    results = [{"id": "1", "title": "Result", "url": "https://example.com/a", "author": None, "score": 0.9, "text": "Example text."}]


class FakeClient:
    def __init__(self) -> None:
        self.calls = 0
        self.last_kwargs = None

    def search(self, query: str, **kwargs):
        self.calls += 1
        self.last_kwargs = kwargs
        return FakeResponse()

    def search_and_contents(self, query: str, **kwargs):
        self.calls += 1
        self.last_kwargs = kwargs
        return FakeResponse()

    def find_similar(self, url: str, **kwargs):
        self.calls += 1
        return FakeResponse()


def make_engine(path, client):
    return SearchEngine(
        api_key="test",
        client=client,
        cache=SQLiteCacheBackend(path / "cache.sqlite3"),
        quota=QuotaTracker(path / "quota.sqlite3", bucket=TokenBucket(capacity=10, tokens=10)),
        history=HistoryStore(path / "history.sqlite3"),
        collections=CollectionStore(path / "collections.sqlite3"),
    )


def test_search_uses_normalized_filters_and_display_author() -> None:
    client = FakeClient()
    engine = make_engine(state_dir("engine-a"), client)
    results = engine.search("hello", include_domains=["https://www.tiktok.com"])
    assert client.last_kwargs["include_domains"] == ["tiktok.com"]
    assert results[0].display_author == "Unknown author"


def test_cache_prevents_second_provider_call() -> None:
    client = FakeClient()
    engine = make_engine(state_dir("engine-b"), client)
    engine.search("hello", include_domains=["https://www.tiktok.com"])
    engine.search("hello", include_domains=["tiktok.com"])
    assert client.calls == 1
