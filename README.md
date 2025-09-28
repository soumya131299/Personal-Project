## Presence Matching API

Matches founders to VCs by sectors, stages, geography, backgrounds/thesis, and portfolio signals. Returns a percent match with a transparent breakdown.

### Quickstart

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

If your system lacks `venv`, install it (Debian/Ubuntu): `sudo apt install python3-venv`.

### Endpoints

- GET `/founders` — sample founders
- GET `/vcs` — sample VCs
- GET `/match/founder/{founder_id}?top_k=5` — rank matches for a seeded founder
- POST `/match` — submit a custom founder profile
\- POST `/auth/signup` — create a user (username, email, password)
\- POST `/auth/login` — get a Bearer token
\- GET `/auth/me` — get current user (send `Authorization: Bearer <token>`) 

### POST /match example

```json
{
  "founder": {
    "id": "custom_1",
    "name": "You",
    "hometown_city": "Austin",
    "hometown_country": "USA",
    "background": ["ex-Stripe PM", "Fintech"],
    "bio": "Building embedded lending infrastructure",
    "sectors": ["fintech", "b2b", "infrastructure"],
    "stages": ["pre-seed", "seed"]
  },
  "top_k": 3
}
```

### Sample response

```json
{
  "founder_id": "custom_1",
  "matches": [
    {
      "founder_id": "custom_1",
      "vc_id": "vc_101",
      "score_percent": 82.5,
      "breakdown": {
        "sectors": 0.67,
        "stages": 1.0,
        "geography": 1.0,
        "background_thesis": 0.44,
        "portfolio": 0.5
      }
    }
  ]
}
```

### Weights

Defaults (sum to 1.0):
- sectors: 0.35
- stages: 0.20
- geography: 0.15
- background_thesis: 0.15
- portfolio: 0.15

To customize, extend the `/match` request to accept weight overrides.

### Notes
- Background/thesis uses cosine similarity over simple bag-of-words with stopwords removed.
- Geography matches exact city/country or treats `global` as a partial match.
- Portfolio signal uses sector overlap across portfolio companies.

