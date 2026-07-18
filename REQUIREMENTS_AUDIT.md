# Requirements Audit

Source: `C:\Users\adeem\Downloads\meridian-codex-prompt.md`

## Summary

- PASS: 36
- PARTIAL: 3
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
| Collection reorder | PASS | `CollectionStore.reorder`, backend route, and CLI command reorder saved items. |
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
| Production Docker deployment | PASS | `Dockerfile` and `compose.yml` build the React app, install the Python service, persist `/data`, and serve API plus UI from one container. |
| Production CORS controls | PASS | `MERIDIAN_CORS_ORIGINS` replaces unconditional wildcard CORS for browser deployments. |
| Frontend lint script | PASS | ESLint 9 flat config is present and `npm run lint` validates TS/TSX source. |
| Full Exa category surface | PARTIAL | Current common categories are typed; automatic discovery of future SDK categories is not implemented. |
| Autoprompt preview | PASS | Backend preserves Exa autoprompt metadata when returned, and the web UI displays it. |
| Web export buttons | PASS | Frontend exposes Markdown export buttons for result and answer modes. |
| Exact sentence-level citation enforcement | PASS | Answer validation now regenerates when any generated sentence lacks a valid citation marker. |
| Redis cache backend | PARTIAL | Backend interface exists; Redis implementation is optional and not covered in default tests. |
| Pre-commit/Husky install flow | PARTIAL | Config files exist; hook installation depends on developers running `make install`/`npm install`. |

## Changes Made During This Pass

- Removed redundant package/class docstrings.
- Wired the web result `Save` action to the collections API.
- Changed CLI collection export to use the real Markdown/JSON/CSV exporters.
- Added collection reorder support in core/backend/CLI.
- Added web export buttons and Exa autoprompt metadata display.
- Tightened answer verification so uncited sentences trigger regeneration.
- Added a Docker production path, same-origin frontend serving from FastAPI, configurable CORS, and a working ESLint 9 frontend lint configuration.
