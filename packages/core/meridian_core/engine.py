from __future__ import annotations

import os
from typing import Any, Callable

from dotenv import load_dotenv
from pydantic import ValidationError

from .answer import AnswerSynthesizer
from .cache.sqlite_backend import SQLiteCacheBackend
from .collections import CollectionStore
from .errors import ConfigurationError, MeridianError, SearchProviderError
from .filters import SearchFilters, normalized_cache_key
from .history import HistoryStore
from .quota import QuotaTracker
from .results import AnsweredQuery, SearchResult

TTL = {"search": 3600, "search_and_contents": 3600, "find_similar": 86400, "get_contents": 86400, "answer": 3600}


class SearchEngine:
    def __init__(
        self,
        api_key: str | None = None,
        client: Any | None = None,
        cache: Any | None = None,
        quota: QuotaTracker | None = None,
        history: HistoryStore | None = None,
        collections: CollectionStore | None = None,
        answerer: AnswerSynthesizer | None = None,
    ) -> None:
        load_dotenv()
        self.api_key = api_key or os.getenv("EXA_API_KEY")
        self._client = client
        self.cache = cache or SQLiteCacheBackend()
        self.quota = quota or QuotaTracker(limit=int(os.getenv("MERIDIAN_QUOTA_LIMIT", "1000")))
        self.history = history or HistoryStore()
        self.collections = collections or CollectionStore()
        self.answerer = answerer or AnswerSynthesizer()

    @property
    def client(self) -> Any:
        if self._client is None:
            if not self.api_key:
                raise ConfigurationError("EXA_API_KEY is missing. Set it in the environment or .env before making live search requests.")
            try:
                from exa_py import Exa
            except ImportError as exc:
                raise ConfigurationError("exa_py is not installed. Run `make install` before live search.") from exc
            self._client = Exa(self.api_key)
        return self._client

    def _filters(self, filters: SearchFilters | dict | None = None, **kwargs: Any) -> SearchFilters:
        try:
            if isinstance(filters, SearchFilters):
                base = filters.model_dump()
                base.update(kwargs)
                return SearchFilters(**base)
            return SearchFilters(**(filters or {}), **kwargs)
        except ValidationError as exc:
            raise MeridianError(str(exc)) from exc

    def _cached(self, method: str, target: str, filters: SearchFilters, call: Callable[[], dict | list], extra: dict[str, Any] | None = None) -> dict | list:
        key = normalized_cache_key(method, target, filters, extra)
        if not filters.force_refresh:
            cached = self.cache.get(key)
            if cached is not None:
                return cached
        self.quota.check()
        try:
            data = call()
        except Exception as exc:
            message = str(exc).lower()
            if "auth" in message or "api key" in message:
                raise SearchProviderError("Exa authentication failed. Check EXA_API_KEY without exposing the key.") from exc
            if "rate" in message or "429" in message:
                raise SearchProviderError("Exa rate limit reached. Wait or use cached results.") from exc
            if "timeout" in message or "timed out" in message:
                raise SearchProviderError("Exa request timed out. Try a smaller result count or retry later.") from exc
            raise SearchProviderError(f"Exa request failed: {exc}") from exc
        self.quota.record_call(method)
        self.cache.set(key, data, TTL.get(method, 3600))
        return data

    @staticmethod
    def _extract_results(payload: Any) -> list[Any]:
        if isinstance(payload, list):
            return payload
        if isinstance(payload, dict):
            return payload.get("results") or []
        return getattr(payload, "results", [])

    @staticmethod
    def _serialize_payload(payload: Any) -> dict | list:
        if isinstance(payload, (dict, list)):
            return payload
        if hasattr(payload, "model_dump"):
            return payload.model_dump()
        if hasattr(payload, "dict"):
            return payload.dict()
        if hasattr(payload, "results"):
            return {"results": [vars(item) if not isinstance(item, dict) else item for item in payload.results]}
        return vars(payload)

    def search(self, query: str, filters: SearchFilters | dict | None = None, **kwargs: Any) -> list[SearchResult]:
        query = query.strip()
        if not query:
            raise MeridianError("Search query cannot be empty.")
        search_filters = self._filters(filters, **kwargs)

        def call() -> dict | list:
            payload = self.client.search(query, **search_filters.exa_kwargs())
            return self._serialize_payload(payload)

        payload = self._cached("search", query, search_filters, call)
        results = [SearchResult.from_exa(item) for item in self._extract_results(payload)]
        self.history.add(query, search_filters.normalized_payload(), len(results))
        return results

    def search_and_contents(self, query: str, filters: SearchFilters | dict | None = None, **kwargs: Any) -> list[SearchResult]:
        query = query.strip()
        if not query:
            raise MeridianError("Search query cannot be empty.")
        search_filters = self._filters(filters, **kwargs)

        def call() -> dict | list:
            payload = self.client.search_and_contents(query, **search_filters.exa_kwargs())
            return self._serialize_payload(payload)

        payload = self._cached("search_and_contents", query, search_filters, call)
        results = [SearchResult.from_exa(item) for item in self._extract_results(payload)]
        self.history.add(query, search_filters.normalized_payload(), len(results))
        return results

    def find_similar(self, url: str, filters: SearchFilters | dict | None = None, **kwargs: Any) -> list[SearchResult]:
        url = url.strip()
        if not url:
            raise MeridianError("URL cannot be empty.")
        search_filters = self._filters(filters, **kwargs)

        def call() -> dict | list:
            payload = self.client.find_similar(url, **search_filters.exa_kwargs())
            return self._serialize_payload(payload)

        payload = self._cached("find_similar", url, search_filters, call)
        return [SearchResult.from_exa(item) for item in self._extract_results(payload)]

    def get_contents(self, ids: list[str], **options: Any) -> list[SearchResult]:
        if not ids:
            raise MeridianError("At least one result id is required.")
        filters = SearchFilters()
        target = ",".join(sorted(ids))

        def call() -> dict | list:
            payload = self.client.get_contents(ids, **options)
            return self._serialize_payload(payload)

        payload = self._cached("get_contents", target, filters, call, extra=options)
        return [SearchResult.from_exa(item) for item in self._extract_results(payload)]

    def answer(self, query: str, filters: SearchFilters | dict | None = None, **kwargs: Any) -> AnsweredQuery:
        search_filters = self._filters(filters, **kwargs)

        def call() -> dict:
            if hasattr(self.client, "answer"):
                try:
                    payload = self.client.answer(query, **search_filters.exa_kwargs())
                    serialized = self._serialize_payload(payload)
                    if isinstance(serialized, dict) and serialized.get("answer"):
                        return serialized
                except Exception:
                    pass
            results = self.search_and_contents(query, search_filters)
            return self.answerer.answer(query, results).model_dump(mode="json")

        payload = self._cached("answer", query, search_filters, call)
        if isinstance(payload, dict) and "sources" in payload:
            return AnsweredQuery(**payload)
        results = self.search_and_contents(query, search_filters)
        return self.answerer.answer(query, results)

    def quota_snapshot(self) -> dict:
        return self.quota.snapshot(cache_hits_today=self.cache.stats().get("hits_today", 0)).model_dump()

    def cache_stats(self) -> dict:
        return self.cache.stats()
