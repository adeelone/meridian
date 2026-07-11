from __future__ import annotations

import re

from .llm.providers import ExtractiveLLMProvider, LLMProvider
from .results import AnsweredQuery, SearchResult, Source


def citation_numbers(text: str) -> set[int]:
    return {int(match) for match in re.findall(r"\[(\d+)\]", text or "")}


class AnswerSynthesizer:
    def __init__(self, provider: LLMProvider | None = None) -> None:
        self.provider = provider or ExtractiveLLMProvider()

    def answer(self, query: str, results: list[SearchResult]) -> AnsweredQuery:
        sources = [
            Source(index=i + 1, id=result.id, title=result.title, url=result.url, snippet=(result.text or result.summary or " ".join(result.highlights))[:900])
            for i, result in enumerate(results)
            if result.url and (result.text or result.summary or result.highlights)
        ]
        if not sources:
            return AnsweredQuery(query=query, answer="No usable sources were retrieved, so Meridian did not synthesize an answer.", sources=[], verified=True)
        passages = [source.model_dump() for source in sources]
        answer = self.provider.synthesize(query, passages)
        valid = {source.index for source in sources}
        cited = citation_numbers(answer)
        if not cited <= valid:
            answer = self.provider.synthesize(query, passages, corrective=True)
            cited = citation_numbers(answer)
        if not cited <= valid:
            return AnsweredQuery(query=query, answer=answer, sources=sources, verified=False, warning="Meridian could not verify every generated citation.")
        return AnsweredQuery(query=query, answer=answer, sources=sources, verified=True)
