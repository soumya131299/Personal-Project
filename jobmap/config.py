import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv


@dataclass
class Settings:
    serpapi_api_key: Optional[str]
    crunchbase_api_key: Optional[str]
    http_user_agent: str


def get_settings() -> Settings:
    load_dotenv()
    return Settings(
        serpapi_api_key=os.getenv("SERPAPI_API_KEY"),
        crunchbase_api_key=os.getenv("CRUNCHBASE_API_KEY"),
        http_user_agent=os.getenv("HTTP_USER_AGENT", "jobmap/1.0"),
    )

