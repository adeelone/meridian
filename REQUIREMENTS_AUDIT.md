# Requirements Audit

Source: `C:\Users\adeem\Downloads\meridian-codex-prompt.md`

## Summary

- PASS: 29
- PARTIAL: 7
- FAIL: 0

## Results

| Requirement | Status | Evidence |
| --- | --- | --- |
| No hardcoded API keys | PASS | `SearchEngine` reads `EXA_API_KEY`; `.env.example` contains empty keys only. |
| Clear missing-key behavior | PASS | `SearchEngine.client` raises `ConfigurationError` before live Exa calls. |
| User-safe provider errors | PASS | Auth, rate limit, timeout, and generic provider failures are mapped in `engine.py`. |
| Typed filters | PASS | `SearchFilters` validates search type, category, domains, dates, text filters, and result count. |
| Domain normalization | PASS | Core, CLI, backend models, frontend chip helper, and tests normalize full URLs to bare domains. |
| Search method | PASS | `SearchEngine.search` calls Exa through the shared engine with cache/quota/history. |
| Search plus contents | PASS | `SearchEngine.search_and_contents` uses the native Exa method. |
| Similarity search | PASS | `SearchEngine.find_similar`, backend route, CLI command, and frontend side panel are wired. |
| Contents retrieval | PASS | `SearchEngine.get_contents` is implemented with cache/quota handling. |
| Answer synthesis | PASS | `AnswerSynthesizer` builds cited answers from retrieved source text. |
| Exa Answer endpoint support | PASS | `SearchEngine.answer` uses `client.answer` when present and falls back to RAG. |
| Citation integrity check | PASS | Invalid citation indexes trigger one regeneration before warning. |
| Typed result objects | PASS | `SearchResult`, `Source`, `AnsweredQuery`, and `QuotaSnapshot` are Pydantic models. |
| SQLite cache | PASS | `SQLiteCacheBackend` stores TTL-bound cache entries and hit counts. |
| Cache key normalization | PASS | Cache keys hash normalized method, target, filters, and options. |
| Cache stats | PASS | CLI and backend expose cache stats. |
| Quota tracker | PASS | `QuotaTracker` persists real API calls and exposes period/today/remaining counts. |
| Token bucket | PASS | `TokenBucket` blocks local bursts before provider calls. |
| History | PASS | Search history is persisted, listed, and rerunnable through API/CLI. |
| Collections | PASS | Results can be saved to named local collections from backend, CLI, and web UI. |
| Collection export | PASS | CLI collection export now uses Markdown, JSON, or CSV result exporters. |
| Result export | PASS | Result lists export as Markdown, JSON, and CSV. |
| Answer export | PASS | Answers export with source lists in Markdown, JSON, and CSV. |
| CLI argument parsing | PASS | Typer powers search, answer, similar, history, collections, quota, cache, and REPL commands. |
| CLI repeated-use REPL | PASS | `meridian repl` handles empty input and repeated queries without exiting. |
| FastAPI backend | PASS | Routes cover search, answer, similar, history, collections, quota, cache, and export. |
| Frontend search controls | PASS | React UI includes search bar, mode buttons, autoprompt toggle, and filter panel. |
| Frontend result cards | PASS | Cards render title, domain, author fallback, date, relevance bar, snippet, and actions. |
| `author: None` display | PASS | Core display property and UI use `Unknown author`, never literal `None`. |
| Quota dashboard | PASS | Web UI shows remaining quota, used-today, cache hits, and warning text. |
| Security/privacy docs | PASS | `SECURITY.md` documents key handling, local persistence, and reporting. |
| API mapping docs | PASS | `API.md` maps Python SDK snake_case to REST camelCase fields. |
| Testing without live Exa calls | PASS | Tests use fake clients and fixtures; CI does not require `EXA_API_KEY`. |
| GitHub repo hygiene and CI | PASS | `.github`, Dependabot, release workflow, branch protection, and green `main` CI are in place. |
| Full Exa category surface | PARTIAL | Current common categories are typed; automatic discovery of future SDK categories is not implemented. |
| Autoprompt preview | PARTIAL | Toggle is wired through filters; UI does not yet display Exa's rewritten prompt separately. |
| Reorder collection items | PARTIAL | Collection items preserve insertion order but no reorder command/UI exists yet. |
| Web export buttons | PARTIAL | Backend export routes exist; frontend does not yet expose download/export controls. |
| Exact sentence-level citation enforcement | PARTIAL | Citation indexes are verified, but the checker does not parse every factual sentence. |
| Redis cache backend | PARTIAL | Backend interface exists; Redis implementation is optional and not covered in default tests. |
| Pre-commit/Husky install flow | PARTIAL | Config files exist; hook installation depends on developers running `make install`/`npm install`. |

## Changes Made During This Pass

- Removed redundant package/class docstrings.
- Wired the web result `Save` action to the collections API.
- Changed CLI collection export to use the real Markdown/JSON/CSV exporters.
