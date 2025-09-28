from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException

from .data import seed_founders, seed_vcs
from .matching import rank_vcs_for_founder
from .models import Founder, VC, MatchRequest, MatchResponse


router = APIRouter()


_FOUNDERS: List[Founder] = seed_founders()
_VCS: List[VC] = seed_vcs()
_FOUNDER_INDEX: Dict[str, Founder] = {f.id: f for f in _FOUNDERS}
_VC_INDEX: Dict[str, VC] = {v.id: v for v in _VCS}


@router.get("/founders", response_model=List[Founder])
def list_founders() -> List[Founder]:
    return _FOUNDERS


@router.get("/vcs", response_model=List[VC])
def list_vcs() -> List[VC]:
    return _VCS


@router.get("/match/founder/{founder_id}", response_model=MatchResponse)
def match_for_founder(founder_id: str, top_k: int = 5) -> MatchResponse:
    founder = _FOUNDER_INDEX.get(founder_id)
    if not founder:
        raise HTTPException(status_code=404, detail="Founder not found")
    matches = rank_vcs_for_founder(founder, _VCS, top_k=top_k)
    return MatchResponse(founder_id=founder.id, matches=matches)


@router.post("/match", response_model=MatchResponse)
def match_custom_founder(req: MatchRequest) -> MatchResponse:
    matches = rank_vcs_for_founder(req.founder, _VCS, top_k=req.top_k)
    return MatchResponse(founder_id=req.founder.id, matches=matches)

