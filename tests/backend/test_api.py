from fastapi.testclient import TestClient

import app.main as main
from meridian_core.results import AnsweredQuery, SearchResult, Source


def test_health() -> None:
    client = TestClient(app)
    assert client.get("/health").json() == {"ok": True}


app = main.app


class FakeEngine:
    def __init__(self) -> None:
        self.result = SearchResult(id="1", title="Title", url="https://example.com", text="Text")
        self.last_autoprompt = "rewritten"
        self.answered = AnsweredQuery(
            query="q",
            answer="Answer [1].",
            sources=[Source(index=1, id="1", title="Title", url="https://example.com", snippet="Text")],
        )

    def search_and_contents(self, query, filters):
        return [self.result]

    def answer(self, query, filters):
        return self.answered

    def find_similar(self, url, filters):
        return [self.result]

    @property
    def history(self):
        class Store:
            def list(self):
                return [{"id": 1, "query": "q", "filters": {}, "result_count": 1}]

            def get(self, item_id):
                return {"id": item_id, "query": "q", "filters": {}, "result_count": 1}

        return Store()

    @property
    def collections(self):
        class Store:
            def list(self):
                return [{"name": "Research", "count": 1}]

            def show(self, name):
                return {"name": name, "items": [{"position": 1, "result": FakeEngine().result.model_dump(), "note": ""}]}

            def add_result(self, name, result, note):
                return None

            def reorder(self, name, positions):
                return {"name": name, "items": positions}

        return Store()

    def quota_snapshot(self):
        return {"limit": 1000, "remaining": 999}

    def cache_stats(self):
        return {"entries": 1}


def test_api_routes(monkeypatch) -> None:
    monkeypatch.setattr(main, "get_engine", lambda: FakeEngine())
    client = TestClient(app)
    assert client.post("/api/search", json={"query": "q", "filters": {}}).json()["results"][0]["title"] == "Title"
    assert client.post("/api/answer", json={"query": "q", "filters": {}}).json()["answer"] == "Answer [1]."
    assert client.post("/api/similar", json={"url": "https://example.com", "filters": {}}).json()["results"][0]["id"] == "1"
    assert client.get("/api/history").json()["items"][0]["query"] == "q"
    assert client.post("/api/history/1/rerun").json()["results"][0]["title"] == "Title"
    assert client.get("/api/collections").json()["items"][0]["name"] == "Research"
    assert client.get("/api/collections/Research").json()["name"] == "Research"
    assert client.post("/api/collections", json={"collection": "Research", "result": FakeEngine().result.model_dump(), "note": ""}).json()["ok"] is True
    assert client.post("/api/collections/Research/reorder", json={"positions": [1]}).json()["items"] == [1]
    assert client.get("/api/quota").json()["remaining"] == 999
    assert client.get("/api/cache/stats").json()["entries"] == 1
    assert "Title" in client.post("/api/export/results/markdown", json={"query": "q", "filters": {}}).json()["content"]
    assert "Sources" in client.post("/api/export/answer/markdown", json={"query": "q", "filters": {}}).json()["content"]
