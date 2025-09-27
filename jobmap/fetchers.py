THIS SHOULD BE A LINTER ERRORfrom __future__ import annotations

import csv
from datetime import datetime
from typing import Dict, Any, Generator, Iterable, Optional

from .http import HttpClient
from .models import JobPosting


class SerpApiLinkedInFetcher:
    def __init__(self, api_key: str, http: HttpClient) -> None:
        self.api_key = api_key
        self.http = http

    def fetch(self, query: str, location: Optional[str] = None, max_results: int = 50) -> Iterable[JobPosting]:
        fetched = 0
        start = 0
        while fetched < max_results:
            page_size = min(25, max_results - fetched)
            params = {
                "engine": "linkedin_jobs",
                "q": query,
                "api_key": self.api_key,
                "start": start,
                "count": page_size,
            }
            if location:
                params["location"] = location
            data = self.http.get_json("https://serpapi.com/search", params=params)
            jobs = data.get("jobs_results", [])
            if not jobs:
                break
            for item in jobs:
                title = item.get("title") or ""
                company_name = (item.get("company_name") or item.get("company") or "").strip()
                job_url = item.get("link") or item.get("job_link")
                loc_text = item.get("location")
                posted_str = item.get("extensions", [])
                posted_at = None
                if isinstance(posted_str, list):
                    # SerpAPI often has relative times in extensions; ignore precise parsing
                    posted_at = None
                yield JobPosting(
                    title=title,
                    company_name=company_name,
                    location_text=loc_text,
                    job_url=job_url,
                    posted_at=posted_at,
                    source="serpapi_linkedin",
                    raw=item,
                )
                fetched += 1
                if fetched >= max_results:
                    break
            start += page_size


class CsvFetcher:
    def __init__(self, path: str) -> None:
        self.path = path

    def fetch(self) -> Iterable[JobPosting]:
        with open(self.path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                posted_at = None
                posted_raw = row.get("posted_at")
                if posted_raw:
                    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y"):
                        try:
                            posted_at = datetime.strptime(posted_raw, fmt)
                            break
                        except Exception:
                            continue
                yield JobPosting(
                    title=row.get("title", ""),
                    company_name=row.get("company", ""),
                    location_text=row.get("location") or None,
                    job_url=row.get("url") or None,
                    posted_at=posted_at,
                    source="csv",
                    raw=row,
                )

