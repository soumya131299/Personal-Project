from __future__ import annotations

from datetime import datetime
from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field


class GeoPoint(BaseModel):
    latitude: float
    longitude: float


class CompanyInfo(BaseModel):
    name: str
    crunchbase_permalink: Optional[str] = None
    domain: Optional[str] = None
    hq_address_text: Optional[str] = None
    hq_geopoint: Optional[GeoPoint] = None


class JobPosting(BaseModel):
    title: str
    company_name: str
    location_text: Optional[str] = None
    job_url: Optional[str] = None
    posted_at: Optional[datetime] = None
    remote: Optional[bool] = None
    source: str = Field(default="unknown")
    raw: Dict[str, Any] = Field(default_factory=dict)


class EnrichedJob(BaseModel):
    job: JobPosting
    company: CompanyInfo
    resolved_address_text: Optional[str] = None
    resolved_point: Optional[GeoPoint] = None

    def to_geojson_feature(self) -> Dict[str, Any]:
        properties = {
            "title": self.job.title,
            "company": self.company.name,
            "job_url": self.job.job_url,
            "posted_at": self.job.posted_at.isoformat() if self.job.posted_at else None,
            "remote": self.job.remote,
            "source": self.job.source,
            "resolved_address": self.resolved_address_text,
            "crunchbase": self.company.crunchbase_permalink,
        }
        geometry = None
        if self.resolved_point is not None:
            geometry = {
                "type": "Point",
                "coordinates": [self.resolved_point.longitude, self.resolved_point.latitude],
            }
        return {"type": "Feature", "geometry": geometry, "properties": properties}

