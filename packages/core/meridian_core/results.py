from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field


class SearchResult(BaseModel):
    id: str
    title: str
    url: str
    domain: str = ""
    author: str | None = None
    published_date: str | None = None
    score: float | None = None
    text: str | None = None
    highlights: list[str] = Field(default_factory=list)
    summary: str | None = None

    @property
    def display_author(self) -> str:
        return self.author or "Unknown author"

    @classmethod
    def from_exa(cls, item: Any) -> "SearchResult":
        data = item if isinstance(item, dict) else vars(item)
        url = str(data.get("url") or "")
        domain = url.split("/")[2].replace("www.", "") if "://" in url else ""
        return cls(
            id=str(data.get("id") or url),
            title=str(data.get("title") or "Untitled result"),
            url=url,
            domain=str(data.get("domain") or domain),
            author=data.get("author") or None,
            published_date=data.get("published_date") or data.get("publishedDate"),
            score=data.get("score"),
            text=data.get("text"),
            highlights=list(data.get("highlights") or []),
            summary=data.get("summary"),
        )


class Source(BaseModel):
    index: int
    id: str
    title: str
    url: str
    snippet: str


class AnsweredQuery(BaseModel):
    query: str
    answer: str
    sources: list[Source]
    verified: bool = True
    warning: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class QuotaSnapshot(BaseModel):
    limit: int
    used_period: int
    used_today: int
    remaining: int
    cache_hits_today: int
    warning: str | None = None
