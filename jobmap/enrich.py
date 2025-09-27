from __future__ import annotations

import time
from typing import Iterable, List, Optional, Dict, Any

from .http import HttpClient
from .models import EnrichedJob, JobPosting, CompanyInfo, GeoPoint


class CrunchbaseEnricher:
    def __init__(self, api_key: Optional[str], http: HttpClient) -> None:
        self.api_key = api_key
        self.http = http

    def _search_org(self, company_name: str) -> Optional[Dict[str, Any]]:
        if not self.api_key:
            return None
        try:
            # Crunchbase v4 search organizations
            url = "https://api.crunchbase.com/api/v4/searches/organizations"
            payload = {
                "field_ids": ["identifier", "website", "location_identifiers", "short_description"],
                "query": [{"type": "predicate", "field_id": "identifier", "operator_id": "includes", "values": [company_name]}],
                "limit": 1,
            }
            # Using GET with params is simpler; but v4 search is POST. Use Session directly.
            resp = self.http.session.post(url, json=payload, params={"user_key": self.api_key}, timeout=20)
            resp.raise_for_status()
            data = resp.json()
            hits = data.get("entities", [])
            return hits[0] if hits else None
        except Exception:
            return None

    def _org_details(self, permalink: str) -> Optional[Dict[str, Any]]:
        if not self.api_key:
            return None
        try:
            url = f"https://api.crunchbase.com/api/v4/entities/organizations/{permalink}"
            data = self.http.get_json(url, params={"user_key": self.api_key, "field_ids": "identifier,website,location_identifiers,rank_org"})
            return data
        except Exception:
            return None


class Geocoder:
    def __init__(self, http: HttpClient) -> None:
        self.http = http

    def geocode(self, text: Optional[str]) -> Optional[GeoPoint]:
        if not text:
            return None
        try:
            data = self.http.get_json("https://nominatim.openstreetmap.org/search", params={"q": text, "format": "json", "limit": 1})
            if isinstance(data, list) and data:
                item = data[0]
                return GeoPoint(latitude=float(item["lat"]), longitude=float(item["lon"]))
        except Exception:
            return None
        return None


def enrich_jobs(jobs: Iterable[JobPosting], enricher: CrunchbaseEnricher, geocoder: Geocoder) -> List[EnrichedJob]:
    results: List[EnrichedJob] = []
    for job in jobs:
        company = CompanyInfo(name=job.company_name)
        resolved_address: Optional[str] = None
        resolved_point: Optional[GeoPoint] = None

        # Try Crunchbase first
        hit = enricher._search_org(job.company_name)
        if hit:
            ident = hit.get("identifier", {})
            company.crunchbase_permalink = ident.get("permalink")
            company.name = ident.get("value") or company.name
            # Crunchbase may not give HQ address directly without more fields; fallback to job location text

        # Resolve address text preference: Crunchbase not providing; so use job location
        resolved_address = job.location_text

        # Geocode address text
        resolved_point = geocoder.geocode(resolved_address)

        results.append(EnrichedJob(job=job, company=company, resolved_address_text=resolved_address, resolved_point=resolved_point))
    return results

