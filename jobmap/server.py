from __future__ import annotations

from pathlib import Path
from typing import Optional, List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .config import get_settings
from .http import HttpClient
from .fetchers import SerpApiLinkedInFetcher
from .enrich import CrunchbaseEnricher, Geocoder, enrich_jobs
from .mapgen import write_geojson, write_map


class FetchRequest(BaseModel):
    query: Optional[str] = None
    location: Optional[str] = None
    max_results: int = 50


class FetchResponse(BaseModel):
    jobs_count: int
    geojson_url: str
    map_url: str


def create_app() -> FastAPI:
    app = FastAPI(title="JobMap Server", version="1.0.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    outputs_dir = Path("outputs")
    outputs_dir.mkdir(parents=True, exist_ok=True)
    app.mount("/outputs", StaticFiles(directory=str(outputs_dir)), name="outputs")

    @app.get("/")
    def root():
        return {"status": "ok", "message": "JobMap server running"}

    @app.post("/api/fetch-map", response_model=FetchResponse)
    def fetch_map(body: FetchRequest) -> FetchResponse:
        settings = get_settings()
        http = HttpClient(settings.http_user_agent)

        jobs: List = []
        if body.query:
            if not settings.serpapi_api_key:
                raise HTTPException(status_code=400, detail="SERPAPI_API_KEY not configured on server")
            fetcher = SerpApiLinkedInFetcher(settings.serpapi_api_key, http)
            jobs.extend(list(fetcher.fetch(query=body.query, location=body.location, max_results=body.max_results)))

        if not jobs:
            raise HTTPException(status_code=400, detail="No jobs fetched. Provide a query.")

        enricher = CrunchbaseEnricher(settings.crunchbase_api_key, http)
        geocoder = Geocoder(http)
        enriched = enrich_jobs(jobs, enricher, geocoder)

        geojson_path = outputs_dir / "jobs.geojson"
        map_path = outputs_dir / "map.html"
        write_geojson(enriched, geojson_path)
        write_map(enriched, map_path)

        return FetchResponse(
            jobs_count=len(jobs),
            geojson_url=f"/outputs/{geojson_path.name}",
            map_url=f"/outputs/{map_path.name}",
        )

    return app


app = create_app()

