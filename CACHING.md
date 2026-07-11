# Caching

Cache keys are SHA-256 hashes of method name, normalized query or URL, normalized filters, and method options. Equivalent domain filters share the same key, so `www.example.com` and `https://example.com` do not spend quota twice.

Default TTLs:

| Method | TTL |
| --- | --- |
| `search` | 1 hour |
| `search_and_contents` | 1 hour |
| `answer` | 1 hour |
| `find_similar` | 24 hours |
| `get_contents` | 24 hours |

Use `force_refresh=True` in Python or `--no-cache` in the CLI to bypass cache intentionally.
