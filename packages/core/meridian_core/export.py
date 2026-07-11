from __future__ import annotations

import csv
import io
import json

from .results import AnsweredQuery, SearchResult


def export_results(results: list[SearchResult], fmt: str) -> str:
    if fmt == "json":
        return json.dumps([result.model_dump() for result in results], indent=2, default=str)
    if fmt == "csv":
        buffer = io.StringIO()
        writer = csv.DictWriter(buffer, fieldnames=["title", "url", "domain", "author", "published_date", "score"])
        writer.writeheader()
        for result in results:
            writer.writerow({
                "title": result.title,
                "url": result.url,
                "domain": result.domain,
                "author": result.display_author,
                "published_date": result.published_date or "",
                "score": result.score or "",
            })
        return buffer.getvalue()
    if fmt == "markdown":
        return "\n".join(f"- [{r.title}]({r.url}) - {r.display_author}" for r in results)
    raise ValueError("Format must be markdown, json, or csv.")


def export_answer(answer: AnsweredQuery, fmt: str) -> str:
    if fmt == "json":
        return answer.model_dump_json(indent=2)
    if fmt == "csv":
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(["index", "title", "url", "snippet"])
        for source in answer.sources:
            writer.writerow([source.index, source.title, source.url, source.snippet])
        return buffer.getvalue()
    if fmt == "markdown":
        sources = "\n".join(f"{source.index}. [{source.title}]({source.url})" for source in answer.sources)
        return f"{answer.answer}\n\n## Sources\n{sources}\n"
    raise ValueError("Format must be markdown, json, or csv.")
