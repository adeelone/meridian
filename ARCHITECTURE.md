# Architecture

`meridian_core` is the only layer that talks to Exa. The FastAPI backend and Typer CLI both instantiate `SearchEngine`, so filter validation, domain normalization, caching, quota accounting, history, collections, and answer synthesis stay consistent.

The request path is:

1. UI or CLI sends a query plus `SearchFilters`.
2. Pydantic normalizes domains, validates dates and categories, and creates a normalized cache key.
3. Cache is checked before quota accounting.
4. Non-cached calls pass through token-bucket limiting and persisted quota tracking.
5. Exa responses are converted into typed `SearchResult` objects.
6. Answer mode uses retrieved content plus `AnswerSynthesizer` and verifies citation indexes.

SQLite is the default local persistence layer because it is inspectable, portable, and enough for a single-user tool. Redis can be substituted behind the cache interface.
