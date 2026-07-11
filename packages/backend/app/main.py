from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from meridian_core import SearchFilters
from meridian_core.errors import MeridianError
from meridian_core.export import export_answer, export_results

from .core_config import get_engine

app = FastAPI(title="Meridian API", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


class QueryRequest(BaseModel):
    query: str
    filters: SearchFilters = SearchFilters()


class SimilarRequest(BaseModel):
    url: str
    filters: SearchFilters = SearchFilters()


class SaveRequest(BaseModel):
    collection: str
    result: dict
    note: str = ""


class ReorderRequest(BaseModel):
    positions: list[int]


def safe_call(func):
    try:
        return func()
    except MeridianError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/health")
def health() -> dict:
    return {"ok": True}


@app.post("/api/search")
def search(request: QueryRequest) -> dict:
    def run() -> dict:
        engine = get_engine()
        results = engine.search_and_contents(request.query, request.filters)
        return {"results": [item.model_dump() for item in results], "autoprompt": engine.last_autoprompt}

    return safe_call(run)


@app.post("/api/answer")
def answer(request: QueryRequest) -> dict:
    return safe_call(lambda: get_engine().answer(request.query, request.filters).model_dump(mode="json"))


@app.post("/api/similar")
def similar(request: SimilarRequest) -> dict:
    return safe_call(lambda: {"results": [item.model_dump() for item in get_engine().find_similar(request.url, request.filters)]})


@app.get("/api/history")
def history() -> dict:
    return {"items": get_engine().history.list()}


@app.post("/api/history/{item_id}/rerun")
def rerun(item_id: int) -> dict:
    engine = get_engine()
    item = engine.history.get(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="History entry not found.")
    return safe_call(lambda: {"results": [result.model_dump() for result in engine.search_and_contents(item["query"], item["filters"])]})


@app.get("/api/collections")
def collections() -> dict:
    return {"items": get_engine().collections.list()}


@app.get("/api/collections/{name}")
def collection(name: str) -> dict:
    return get_engine().collections.show(name)


@app.post("/api/collections")
def save_collection(request: SaveRequest) -> dict:
    from meridian_core.results import SearchResult

    result = SearchResult(**request.result)
    get_engine().collections.add_result(request.collection, result, request.note)
    return {"ok": True}


@app.post("/api/collections/{name}/reorder")
def reorder_collection(name: str, request: ReorderRequest) -> dict:
    return safe_call(lambda: get_engine().collections.reorder(name, request.positions))


@app.get("/api/quota")
def quota() -> dict:
    return get_engine().quota_snapshot()


@app.get("/api/cache/stats")
def cache_stats() -> dict:
    return get_engine().cache_stats()


@app.post("/api/export/results/{fmt}")
def export_result_list(fmt: str, request: QueryRequest) -> dict:
    results = safe_call(lambda: get_engine().search_and_contents(request.query, request.filters))
    return {"content": export_results(results, fmt)}


@app.post("/api/export/answer/{fmt}")
def export_answer_view(fmt: str, request: QueryRequest) -> dict:
    answered = safe_call(lambda: get_engine().answer(request.query, request.filters))
    return {"content": export_answer(answered, fmt)}
