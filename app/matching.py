import math
import re
from collections import Counter
from typing import Dict, Iterable, List, Tuple

from .models import Founder, VC, MatchBreakdown, MatchResult


_STOPWORDS = {
    "a",
    "an",
    "the",
    "and",
    "or",
    "of",
    "for",
    "to",
    "in",
    "on",
    "with",
    "by",
    "at",
    "from",
    "about",
    "as",
    "into",
    "over",
    "after",
}


def _normalize_token(token: str) -> str:
    token = token.lower()
    token = re.sub(r"[^a-z0-9\-\+]+", "", token)
    return token


def _tokenize(text: str) -> List[str]:
    if not text:
        return []
    # Split on non-word boundaries, normalize and drop stopwords/empties
    raw_tokens = re.split(r"[^a-zA-Z0-9\+\-]+", text)
    tokens = []
    for t in raw_tokens:
        n = _normalize_token(t)
        if n and n not in _STOPWORDS:
            tokens.append(n)
    return tokens


def _bag_of_words(texts: Iterable[str]) -> Counter:
    counter: Counter = Counter()
    for text in texts:
        counter.update(_tokenize(text))
    return counter


def _cosine_similarity(a: Counter, b: Counter) -> float:
    if not a or not b:
        return 0.0
    # Dot product
    common = set(a.keys()) & set(b.keys())
    dot = sum(a[t] * b[t] for t in common)
    # Norms
    norm_a = math.sqrt(sum(v * v for v in a.values()))
    norm_b = math.sqrt(sum(v * v for v in b.values()))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def _jaccard(list_a: Iterable[str], list_b: Iterable[str]) -> float:
    set_a = {s.strip().lower() for s in list_a if s}
    set_b = {s.strip().lower() for s in list_b if s}
    if not set_a and not set_b:
        return 0.0
    inter = len(set_a & set_b)
    union = len(set_a | set_b)
    return inter / union if union else 0.0


def _geo_score(founder: Founder, vc: VC) -> float:
    # Simple geography heuristic
    founder_cand = [
        founder.hometown_city or "",
        founder.hometown_country or "",
    ]
    founder_cand = [c.lower() for c in founder_cand if c]
    if not founder_cand:
        return 0.0
    geos = [g.lower() for g in vc.geographies]
    if not geos:
        return 0.0
    if any(c in geos for c in founder_cand):
        return 1.0
    if "global" in geos:
        return 0.6
    return 0.0


def _portfolio_sectors(vc: VC) -> List[str]:
    sectors: List[str] = []
    for p in vc.portfolio:
        sectors.extend(p.sectors)
    return sectors


def compute_match(
    founder: Founder,
    vc: VC,
    weights: Dict[str, float] | None = None,
) -> MatchResult:
    # Default weights sum to 1.0
    default_weights: Dict[str, float] = {
        "sectors": 0.35,
        "stages": 0.20,
        "geography": 0.15,
        "background_thesis": 0.15,
        "portfolio": 0.15,
    }
    w = {**default_weights, **(weights or {})}

    sectors_score = _jaccard(founder.sectors, vc.sectors)
    stages_score = _jaccard(founder.stages, vc.stages)
    geography_score = _geo_score(founder, vc)

    founder_text_parts = list(founder.background)
    if founder.bio:
        founder_text_parts.append(founder.bio)
    vc_text_parts = list(vc.backgrounds)
    if vc.investment_thesis:
        vc_text_parts.append(vc.investment_thesis)
    background_thesis_score = _cosine_similarity(
        _bag_of_words(founder_text_parts), _bag_of_words(vc_text_parts)
    )

    portfolio_score = _jaccard(founder.sectors, _portfolio_sectors(vc))

    final_score = (
        sectors_score * w["sectors"]
        + stages_score * w["stages"]
        + geography_score * w["geography"]
        + background_thesis_score * w["background_thesis"]
        + portfolio_score * w["portfolio"]
    )

    breakdown = MatchBreakdown(
        sectors=round(sectors_score, 4),
        stages=round(stages_score, 4),
        geography=round(geography_score, 4),
        background_thesis=round(background_thesis_score, 4),
        portfolio=round(portfolio_score, 4),
    )
    return MatchResult(
        founder_id=founder.id,
        vc_id=vc.id,
        score_percent=round(final_score * 100.0, 2),
        breakdown=breakdown,
    )


def rank_vcs_for_founder(
    founder: Founder, vcs: List[VC], top_k: int = 5, weights: Dict[str, float] | None = None
) -> List[MatchResult]:
    results = [compute_match(founder, vc, weights) for vc in vcs]
    results.sort(key=lambda r: r.score_percent, reverse=True)
    return results[: max(top_k, 1)]

