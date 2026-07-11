# Meridian

Meridian is a semantic search product built on Exa with a shared Python core, FastAPI web API, React app, and Typer CLI.

It turns the single-query Exa tutorial into a reusable product surface: neural, keyword, and auto search; full-content retrieval; similarity search; cited answer synthesis; saved history and collections; quota-aware caching; and Markdown, JSON, and CSV exports.

## Quickstart

```bash
python -m pip install -e ".[dev]"
cd packages/frontend && npm install
copy .env.example .env
set EXA_API_KEY=your_exa_key
make dev
```

CLI:

```bash
meridian search "semantic search benchmarks" --type neural --num-results 5
meridian answer "What is semantic search?"
meridian repl
```

## Assumptions

- The Exa Python SDK remains the live provider boundary. Tests use mocked clients and fixtures, so CI never spends quota.
- The default answer provider is extractive and keyless. Set `LLM_API_KEY` and swap to `OpenAICompatibleProvider` for model synthesis.
- Local SQLite files under `MERIDIAN_HOME` hold cache, quota, history, and collections. On Windows the default is `%LOCALAPPDATA%\Meridian`; no telemetry is sent by default.

## API key

Create an Exa account, generate an API key in the Exa dashboard, and set `EXA_API_KEY` in your shell or `.env`. Meridian never commits, logs, or returns this value.

## Development

```bash
make install
make test
make lint
make typecheck
```

## Adding filters

Add the public field to `SearchFilters`, validate it in `filters.py`, include it in `exa_kwargs`, mirror the frontend control in `src/lib/api.ts`, and add a row to `API.md`.

## Swapping the LLM provider

Implement the `LLMProvider` protocol in `meridian_core.llm.providers`, pass it to `AnswerSynthesizer`, and keep citation markers mapped to the provided source indexes.

## Known limitations and next steps

- Browser extension for "Search with Meridian" on selected text.
- Multi-user accounts with per-user quota allocation.
- Scheduled saved-search alerts.
- Slack or Discord bot front end.
