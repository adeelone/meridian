from meridian_core.answer import AnswerSynthesizer
from meridian_core.results import SearchResult


class BrokenThenFixedProvider:
    def __init__(self) -> None:
        self.calls = 0

    def synthesize(self, query: str, passages: list[dict], corrective: bool = False) -> str:
        self.calls += 1
        return "Bad citation [9]." if self.calls == 1 else "Grounded citation [1]."


def test_invalid_citation_regenerates_once() -> None:
    result = SearchResult(id="1", title="A", url="https://example.com", text="Useful source text.")
    provider = BrokenThenFixedProvider()
    answered = AnswerSynthesizer(provider).answer("q", [result])
    assert answered.verified is True
    assert provider.calls == 2


class UncitedThenFixedProvider:
    def __init__(self) -> None:
        self.calls = 0

    def synthesize(self, query: str, passages: list[dict], corrective: bool = False) -> str:
        self.calls += 1
        return "This sentence has no citation." if self.calls == 1 else "This sentence is cited [1]."


def test_uncited_sentence_regenerates_once() -> None:
    result = SearchResult(id="1", title="A", url="https://example.com", text="Useful source text.")
    provider = UncitedThenFixedProvider()
    answered = AnswerSynthesizer(provider).answer("q", [result])
    assert answered.verified is True
    assert provider.calls == 2
