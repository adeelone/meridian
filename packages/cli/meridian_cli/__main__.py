from __future__ import annotations

import shlex
from datetime import date
from typing import Any, Optional

import typer
from rich.console import Console

from meridian_core import SearchEngine, SearchFilters
from meridian_core.errors import MeridianError

from . import render

app = typer.Typer(help="Meridian semantic search CLI.")
history_app = typer.Typer(help="Search history commands.")
collections_app = typer.Typer(help="Saved collection commands.")
cache_app = typer.Typer(help="Cache commands.")
app.add_typer(history_app, name="history")
app.add_typer(collections_app, name="collections")
app.add_typer(cache_app, name="cache")
console = Console()


def engine() -> SearchEngine:
    return SearchEngine()


def make_filters(
    type: str = "auto",
    num_results: int = 10,
    include_domains: Optional[str] = None,
    exclude_domains: Optional[str] = None,
    category: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    autoprompt: bool = False,
    no_cache: bool = False,
) -> SearchFilters:
    payload: dict[str, Any] = {
        "type": type,
        "num_results": num_results,
        "include_domains": include_domains.split(",") if include_domains else [],
        "exclude_domains": exclude_domains.split(",") if exclude_domains else [],
        "category": category,
        "start_published_date": date.fromisoformat(start_date) if start_date else None,
        "end_published_date": date.fromisoformat(end_date) if end_date else None,
        "use_autoprompt": autoprompt,
        "force_refresh": no_cache,
    }
    return SearchFilters(**payload)


def fail(exc: Exception) -> None:
    console.print(f"[red]{exc}[/red]")
    raise typer.Exit(code=1)


@app.command()
def search(
    query: str,
    type: str = typer.Option("auto"),
    num_results: int = typer.Option(10),
    include_domains: Optional[str] = typer.Option(None),
    exclude_domains: Optional[str] = typer.Option(None),
    category: Optional[str] = typer.Option(None),
    start_date: Optional[str] = typer.Option(None),
    end_date: Optional[str] = typer.Option(None),
    autoprompt: bool = typer.Option(False),
    json_output: bool = typer.Option(False, "--json"),
    markdown: bool = typer.Option(False, "--markdown"),
    no_cache: bool = typer.Option(False, "--no-cache"),
) -> None:
    fmt = "json" if json_output else "markdown" if markdown else "table"
    try:
        render.results(engine().search(query, make_filters(type, num_results, include_domains, exclude_domains, category, start_date, end_date, autoprompt, no_cache)), fmt)
    except Exception as exc:
        fail(exc)


@app.command()
def answer(
    query: str,
    type: str = typer.Option("auto"),
    num_results: int = typer.Option(8),
    include_domains: Optional[str] = typer.Option(None),
    exclude_domains: Optional[str] = typer.Option(None),
    category: Optional[str] = typer.Option(None),
    json_output: bool = typer.Option(False, "--json"),
    markdown: bool = typer.Option(False, "--markdown"),
) -> None:
    fmt = "json" if json_output else "markdown" if markdown else "table"
    try:
        render.answer(engine().answer(query, make_filters(type, num_results, include_domains, exclude_domains, category)), fmt)
    except Exception as exc:
        fail(exc)


@app.command()
def similar(url: str, json_output: bool = typer.Option(False, "--json"), markdown: bool = typer.Option(False, "--markdown")) -> None:
    try:
        render.results(engine().find_similar(url), "json" if json_output else "markdown" if markdown else "table")
    except Exception as exc:
        fail(exc)


@history_app.command("list")
def history_list() -> None:
    render.payload({"items": engine().history.list()})


@history_app.command("rerun")
def history_rerun(item_id: int) -> None:
    eng = engine()
    item = eng.history.get(item_id)
    if not item:
        fail(MeridianError("History entry not found."))
        return
    render.results(eng.search(item["query"], item["filters"]), "table")


@collections_app.command("list")
def collections_list() -> None:
    render.payload({"items": engine().collections.list()})


@collections_app.command("show")
def collections_show(name: str) -> None:
    render.payload(engine().collections.show(name))


@collections_app.command("export")
def collections_export(name: str, fmt: str = typer.Option("markdown")) -> None:
    collection = engine().collections.show(name)
    results = [item["result"] for item in collection["items"]]
    render.payload({"format": fmt, "items": results})


@app.command()
def quota() -> None:
    render.payload(engine().quota_snapshot())


@cache_app.command("stats")
def cache_stats() -> None:
    render.payload(engine().cache_stats())


@app.command()
def repl() -> None:
    console.print("Meridian REPL. Type search text, `:history`, `:quota`, or `:quit`.")
    eng = engine()
    while True:
        line = console.input("meridian> ").strip()
        if not line:
            console.print("Enter a query or command; empty input was ignored.")
            continue
        if line in {":quit", "quit", "exit"}:
            break
        if line == ":history":
            render.payload({"items": eng.history.list()})
            continue
        if line == ":quota":
            render.payload(eng.quota_snapshot())
            continue
        try:
            parts = shlex.split(line)
            query = " ".join(parts)
            render.results(eng.search(query), "table")
        except Exception as exc:
            console.print(f"[red]{exc}[/red]")


if __name__ == "__main__":
    app()
