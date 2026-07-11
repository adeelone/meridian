import json

from meridian_core.collections import CollectionStore
from meridian_core.export import export_answer, export_results
from meridian_core.history import HistoryStore
from meridian_core.results import AnsweredQuery, SearchResult, Source
from tests.helpers import state_dir


def test_export_results_all_formats() -> None:
    result = SearchResult(id="1", title="Title", url="https://example.com", author=None, score=0.5)
    assert "Unknown author" in export_results([result], "markdown")
    assert json.loads(export_results([result], "json"))[0]["title"] == "Title"
    assert "title,url,domain" in export_results([result], "csv")


def test_export_answer_all_formats() -> None:
    answered = AnsweredQuery(
        query="q",
        answer="Answer [1].",
        sources=[Source(index=1, id="1", title="Source", url="https://example.com", snippet="Snippet")],
    )
    assert "## Sources" in export_answer(answered, "markdown")
    assert json.loads(export_answer(answered, "json"))["verified"] is True
    assert "Source" in export_answer(answered, "csv")


def test_history_store_add_list_get() -> None:
    store = HistoryStore(state_dir("history") / "history.sqlite3")
    item_id = store.add("query", {"type": "auto"}, 3)
    assert store.get(item_id)["query"] == "query"
    assert store.list()[0]["result_count"] == 3


def test_collection_store_add_list_show() -> None:
    store = CollectionStore(state_dir("collections") / "collections.sqlite3")
    result = SearchResult(id="1", title="Title", url="https://example.com")
    store.add_result("Research", result, "note")
    assert store.list()[0]["count"] == 1
    shown = store.show("Research")
    assert shown["items"][0]["note"] == "note"
