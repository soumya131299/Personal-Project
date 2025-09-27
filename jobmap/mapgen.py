from __future__ import annotations

import json
from pathlib import Path
from typing import List

import folium

from .models import EnrichedJob


def write_geojson(enriched: List[EnrichedJob], path: Path) -> None:
    fc = {
        "type": "FeatureCollection",
        "features": [e.to_geojson_feature() for e in enriched if e.to_geojson_feature()["geometry"] is not None],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(fc, ensure_ascii=False, indent=2), encoding="utf-8")


def write_map(enriched: List[EnrichedJob], path: Path) -> None:
    points = [e for e in enriched if e.resolved_point is not None]
    if points:
        lat = sum(e.resolved_point.latitude for e in points) / len(points)
        lon = sum(e.resolved_point.longitude for e in points) / len(points)
        m = folium.Map(location=[lat, lon], zoom_start=4)
    else:
        m = folium.Map(location=[20.0, 0.0], zoom_start=2)

    for e in points:
        popup = f"<b>{e.job.title}</b><br>{e.company.name}<br>{e.resolved_address_text or ''}<br><a href='{e.job.job_url or '#'}' target='_blank'>Job Link</a>"
        folium.Marker(
            location=[e.resolved_point.latitude, e.resolved_point.longitude],
            tooltip=f"{e.company.name}: {e.job.title}",
            popup=folium.Popup(popup, max_width=320),
        ).add_to(m)

    path.parent.mkdir(parents=True, exist_ok=True)
    m.save(str(path))

