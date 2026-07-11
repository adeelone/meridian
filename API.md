# API Reference

| Meridian filter | Type | Default | Exa Python SDK | REST field |
| --- | --- | --- | --- | --- |
| `num_results` | int 1-50 | 10 | `num_results` | `numResults` |
| `type` | `neural`, `keyword`, `auto` | `auto` | `type` | `type` |
| `use_autoprompt` | bool | false | `use_autoprompt` | `useAutoprompt` |
| `category` | string | null | `category` | `category` |
| `include_domains` | string list | [] | `include_domains` | `includeDomains` |
| `exclude_domains` | string list | [] | `exclude_domains` | `excludeDomains` |
| `start_published_date` | date | null | `start_published_date` | `startPublishedDate` |
| `end_published_date` | date | null | `end_published_date` | `endPublishedDate` |
| `start_crawl_date` | date | null | `start_crawl_date` | `startCrawlDate` |
| `end_crawl_date` | date | null | `end_crawl_date` | `endCrawlDate` |
| `include_text` | string list | [] | `include_text` | `includeText` |
| `exclude_text` | string list | [] | `exclude_text` | `excludeText` |

Domain filters are always normalized before they reach Exa. For example, `https://www.tiktok.com` becomes `tiktok.com`.
