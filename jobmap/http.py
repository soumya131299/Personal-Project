from __future__ import annotations

import time
from typing import Any, Dict, Optional

import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type


class HttpClient:
    def __init__(self, user_agent: str) -> None:
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": user_agent,
            "Accept": "application/json, */*;q=0.1",
        })

    @retry(wait=wait_exponential(multiplier=0.5, min=0.5, max=8),
           stop=stop_after_attempt(5),
           retry=retry_if_exception_type((requests.RequestException,)))
    def get_json(self, url: str, params: Optional[Dict[str, Any]] = None, timeout: float = 20.0) -> Dict[str, Any]:
        response = self.session.get(url, params=params, timeout=timeout)
        response.raise_for_status()
        return response.json()

