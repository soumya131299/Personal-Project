from typing import List, Dict, Optional

from pydantic import BaseModel, Field


class PortfolioCompany(BaseModel):
    name: str
    sectors: List[str] = Field(default_factory=list)
    description: Optional[str] = None


class Founder(BaseModel):
    id: str
    name: str
    hometown_city: Optional[str] = None
    hometown_country: Optional[str] = None
    background: List[str] = Field(default_factory=list)
    bio: Optional[str] = None
    sectors: List[str] = Field(default_factory=list)
    stages: List[str] = Field(default_factory=list)


class VC(BaseModel):
    id: str
    name: str
    fund_name: Optional[str] = None
    hq_city: Optional[str] = None
    hq_country: Optional[str] = None
    geographies: List[str] = Field(default_factory=list)
    sectors: List[str] = Field(default_factory=list)
    stages: List[str] = Field(default_factory=list)
    backgrounds: List[str] = Field(default_factory=list)
    investment_thesis: Optional[str] = None
    portfolio: List[PortfolioCompany] = Field(default_factory=list)


class MatchBreakdown(BaseModel):
    sectors: float
    stages: float
    geography: float
    background_thesis: float
    portfolio: float


class MatchResult(BaseModel):
    founder_id: str
    vc_id: str
    score_percent: float
    breakdown: MatchBreakdown


class MatchRequest(BaseModel):
    founder: Founder
    top_k: int = 5


class MatchResponse(BaseModel):
    founder_id: str
    matches: List[MatchResult]

