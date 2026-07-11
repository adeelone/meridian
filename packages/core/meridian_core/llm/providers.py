from __future__ import annotations

import os
import re
from typing import Protocol


class LLMProvider(Protocol):
    def synthesize(self, query: str, passages: list[dict], corrective: bool = False) -> str: ...


class ExtractiveLLMProvider:
    """No-key default that produces grounded answers directly from retrieved passages."""

    def synthesize(self, query: str, passages: list[dict], corrective: bool = False) -> str:
        if not passages:
            return ""
        sentences: list[str] = []
        for source in passages[:4]:
            text = re.sub(r"\s+", " ", source.get("snippet") or source.get("text") or "").strip()
            if not text:
                continue
            sentence = text.split(". ")[0].strip()
            if sentence and not sentence.endswith("."):
                sentence += "."
            sentences.append(f"{sentence} [{source['index']}]")
        return " ".join(sentences) or f"No usable passage text was available for '{query}'."


class OpenAICompatibleProvider:
    def __init__(self, api_key_env: str = "LLM_API_KEY", model: str = "gpt-4.1-mini") -> None:
        self.api_key = os.getenv(api_key_env)
        self.model = model
        if not self.api_key:
            raise RuntimeError(f"{api_key_env} is required for OpenAICompatibleProvider.")

    def synthesize(self, query: str, passages: list[dict], corrective: bool = False) -> str:
        from openai import OpenAI

        context = "\n".join(f"[{p['index']}] {p['title']} {p['url']}\n{p['snippet']}" for p in passages)
        correction = " Previous output had invalid citations; use only listed citation numbers." if corrective else ""
        prompt = (
            "Answer only from the supplied passages. Every factual sentence must include a citation like [1]."
            f"{correction}\n\nQuestion: {query}\n\nPassages:\n{context}"
        )
        client = OpenAI(api_key=self.api_key)
        response = client.responses.create(model=self.model, input=prompt)
        return response.output_text
