from __future__ import annotations

import json

from rich.console import Console
from rich.table import Table

from meridian_core.export import export_answer, export_results
from meridian_core.results import AnsweredQuery, SearchResult

console = Console()


def results(results: list[SearchResult], fmt: str) -> None:
    if fmt in {"json", "markdown", "csv"}:
        console.print(export_results(results, fmt))
        return
    table = Table(title="Meridian results")
    table.add_column("Title")
    table.add_column("Domain")
    table.add_column("Author")
    table.add_column("Score")
    for result in results:
        score = "" if result.score is None else f"{result.score:.2f}"
        table.add_row(result.title, result.domain, result.display_author, score)
    console.print(table)


def answer(answered: AnsweredQuery, fmt: str) -> None:
    if fmt in {"json", "markdown", "csv"}:
        console.print(export_answer(answered, fmt))
        return
    console.print(answered.answer)
    if answered.warning:
        console.print(f"[yellow]{answered.warning}[/yellow]")
    source_table = Table(title="Sources")
    source_table.add_column("#")
    source_table.add_column("Title")
    source_table.add_column("URL")
    for source in answered.sources:
        source_table.add_row(str(source.index), source.title, source.url)
    console.print(source_table)


def payload(data: dict) -> None:
    console.print(json.dumps(data, indent=2, default=str))
