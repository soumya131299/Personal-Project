from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer
from rich import print

from .config import get_settings
from .http import HttpClient
from .fetchers import SerpApiLinkedInFetcher, CsvFetcher
from .enrich import CrunchbaseEnricher, Geocoder, enrich_jobs
from .mapgen import write_geojson, write_map


app = typer.Typer(add_completion=False, help="JobMap CLI")


@app.command()
def fetch_and_map(
    query: Optional[str] = typer.Option(None, help="Job search query for LinkedIn via SerpAPI"),
    location: Optional[str] = typer.Option(None, help="Location filter for LinkedIn"),
    max_results: int = typer.Option(50, help="Maximum number of results to fetch"),
    csv_path: Optional[Path] = typer.Option(None, help="Optional CSV input path with headers: title,company,location,url,posted_at"),
    out_dir: Path = typer.Option(Path("outputs"), help="Output directory for artifacts"),
):
    settings = get_settings()
    http = HttpClient(settings.http_user_agent)

    jobs = []
    if csv_path:
        print(f"[bold green]Reading CSV[/bold green]: {csv_path}")
        jobs.extend(CsvFetcher(str(csv_path)).fetch())
    if query:
        if not settings.serpapi_api_key:
            print("[yellow]SERPAPI_API_KEY not set; skipping LinkedIn fetch[/yellow]")
        else:
            print(f"[bold green]Fetching from SerpAPI[/bold green]: query='{query}', location='{location or ''}'")
            fetcher = SerpApiLinkedInFetcher(settings.serpapi_api_key, http)
            jobs.extend(fetcher.fetch(query=query, location=location, max_results=max_results))

    if not jobs:
        print("[red]No jobs to process. Provide --csv-path or --query[/red]")
        raise typer.Exit(code=1)

    out_dir.mkdir(parents=True, exist_ok=True)
    jobs_json = out_dir / "jobs.json"
    print(f"[bold blue]Writing[/bold blue] {jobs_json}")
    jobs_json.write_text(
        json.dumps([j.model_dump() for j in jobs], ensure_ascii=False, indent=2), encoding="utf-8"
    )

    enricher = CrunchbaseEnricher(settings.crunchbase_api_key, http)
    geocoder = Geocoder(http)
    print("[bold green]Enriching and geocoding[/bold green] ...")
    enriched = enrich_jobs(jobs, enricher, geocoder)

    geojson_path = out_dir / "jobs.geojson"
    html_path = out_dir / "map.html"
    write_geojson(enriched, geojson_path)
    write_map(enriched, html_path)
    print(f"[bold blue]Wrote[/bold blue] {geojson_path} and {html_path}")


def main() -> None:
    app()


if __name__ == "__main__":
    main()

