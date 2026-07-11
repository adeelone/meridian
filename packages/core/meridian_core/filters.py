from __future__ import annotations

import hashlib
import json
import re
from datetime import date
from typing import Any, Literal
from urllib.parse import urlparse

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

SearchType = Literal["neural", "keyword", "auto"]

ALLOWED_CATEGORIES = {
    "company",
    "news",
    "pdf",
    "papers",
    "tweet",
    "github",
    "movies",
    "songs",
    "personal site",
    "linkedin profile",
    "financial report",
}


def normalize_domain(value: str) -> str:
    raw = (value or "").strip().lower()
    if not raw:
        raise ValueError("Domain cannot be empty.")
    parsed = urlparse(raw if "://" in raw else f"//{raw}", scheme="https")
    domain = parsed.netloc or parsed.path
    domain = domain.split("/")[0].split(":")[0].strip(".")
    if domain.startswith("www."):
        domain = domain[4:]
    if not re.fullmatch(r"(?!-)[a-z0-9-]{1,63}(?<!-)(\.(?!-)[a-z0-9-]{1,63}(?<!-))+", domain):
        raise ValueError(f"Invalid domain filter: {value}")
    return domain


class SearchFilters(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    num_results: int = Field(default=10, ge=1, le=50)
    type: SearchType = "auto"
    use_autoprompt: bool = False
    category: str | None = None
    include_domains: list[str] = Field(default_factory=list)
    exclude_domains: list[str] = Field(default_factory=list)
    start_published_date: date | None = None
    end_published_date: date | None = None
    start_crawl_date: date | None = None
    end_crawl_date: date | None = None
    include_text: list[str] = Field(default_factory=list)
    exclude_text: list[str] = Field(default_factory=list)
    force_refresh: bool = False

    @field_validator("category")
    @classmethod
    def validate_category(cls, value: str | None) -> str | None:
        if value is None or value == "":
            return None
        normalized = value.strip().lower()
        if normalized not in ALLOWED_CATEGORIES:
            allowed = ", ".join(sorted(ALLOWED_CATEGORIES))
            raise ValueError(f"Unsupported category '{value}'. Allowed categories: {allowed}.")
        return normalized

    @field_validator("include_domains", "exclude_domains", mode="before")
    @classmethod
    def normalize_domains(cls, value: Any) -> list[str]:
        if value in (None, ""):
            return []
        items = value.split(",") if isinstance(value, str) else list(value)
        normalized = [normalize_domain(item) for item in items if str(item).strip()]
        return sorted(dict.fromkeys(normalized))

    @field_validator("include_text", "exclude_text", mode="before")
    @classmethod
    def normalize_text_filters(cls, value: Any) -> list[str]:
        if value in (None, ""):
            return []
        items = value.split(",") if isinstance(value, str) else list(value)
        return [str(item).strip() for item in items if str(item).strip()]

    @model_validator(mode="after")
    def validate_ranges(self) -> "SearchFilters":
        if self.start_published_date and self.end_published_date:
            if self.start_published_date > self.end_published_date:
                raise ValueError("start_published_date must be before end_published_date.")
        if self.start_crawl_date and self.end_crawl_date:
            if self.start_crawl_date > self.end_crawl_date:
                raise ValueError("start_crawl_date must be before end_crawl_date.")
        overlap = set(self.include_domains) & set(self.exclude_domains)
        if overlap:
            raise ValueError(f"Domains cannot be both included and excluded: {', '.join(sorted(overlap))}.")
        return self

    def exa_kwargs(self) -> dict[str, Any]:
        payload = self.model_dump(exclude={"force_refresh"}, exclude_none=True)
        if payload["type"] == "auto":
            payload.pop("type")
        return payload

    def normalized_payload(self) -> dict[str, Any]:
        return self.model_dump(mode="json", exclude={"force_refresh"}, exclude_none=True)


def normalized_cache_key(method: str, query_or_url: str, filters: SearchFilters, extra: dict[str, Any] | None = None) -> str:
    payload = {
        "method": method,
        "target": (query_or_url or "").strip(),
        "filters": filters.normalized_payload(),
        "extra": extra or {},
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()
