## JobMap: Plan Jobs on a Map

JobMap is a small Python toolchain that:
- Fetches job postings (LinkedIn via SerpAPI, or from a CSV you provide)
- Enriches companies with HQ/location info (Crunchbase optional) and geocodes addresses
- Outputs an interactive HTML map and GeoJSON for planning

### Quickstart
1. Create and activate a Python 3.10+ environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and fill keys if available.
4. Run an example LinkedIn search with SerpAPI:
   ```bash
   python -m jobmap.cli fetch-and-map --query "software engineer" --location "San Francisco Bay Area" --max-results 50 --out-dir outputs
   ```

This produces:
- `outputs/jobs.json` — normalized jobs
- `outputs/jobs.geojson` — geocoded features
- `outputs/map.html` — interactive Folium map

### Inputs
- SerpAPI LinkedIn: requires `SERPAPI_API_KEY`. The tool uses SerpAPI's LinkedIn Jobs engine. You provide a search `--query` and optional `--location`.
- CSV: alternatively, provide `--csv-path path/to/jobs.csv` with columns: `title,company,location,url,posted_at` (headers required). Dates are optional.

### Optional Enrichment
- Crunchbase (recommended): set `CRUNCHBASE_API_KEY` to enrich companies with HQ addresses. If unavailable, the pipeline will geocode the job location text instead.
- Geocoding: OpenStreetMap Nominatim is used by default. Respect the usage policy; do not hammer it. The tool includes conservative retries and rate limits.

### Compliance and Notes
- Do not scrape LinkedIn directly. This tool uses SerpAPI as a proxy data provider; ensure your usage complies with SerpAPI, LinkedIn, and Crunchbase terms.
- Provide a valid user agent in `.env` to be polite to public endpoints.
- Results from third-party APIs may be incomplete; the pipeline is best-effort and resilient to missing fields.

### CLI Help
```bash
python -m jobmap.cli --help
```

### Development
```bash
python -m jobmap.cli fetch-and-map --query "data engineer" --location "New York, NY" --out-dir outputs
```

