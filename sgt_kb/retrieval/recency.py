"""Gentle document-date weighting shared by retrieval entry points."""
from datetime import date, datetime, timezone


RECENCY_HALF_LIFE_DAYS = 730
RECENCY_FLOOR = 0.70
UNDATED_FACTOR = 0.75


def _freshness_factor(value: str, today: date | None = None) -> float:
    """将文档日期转为温和的时间衰减系数，避免旧文压过同等相关的新文。"""
    if not value:
        return UNDATED_FACTOR
    try:
        published = date.fromisoformat(value[:10])
    except (TypeError, ValueError):
        return UNDATED_FACTOR
    age_days = max(0, ((today or datetime.now(timezone.utc).date()) - published).days)
    decay = 0.5 ** (age_days / RECENCY_HALF_LIFE_DAYS)
    return RECENCY_FLOOR + (1.0 - RECENCY_FLOOR) * decay


def _apply_recency(
    rrf_scores: dict[int, float],
    dates: dict[int, str],
    today: date | None = None,
) -> dict[int, float]:
    return {
        cid: score * _freshness_factor(dates.get(cid, ""), today)
        for cid, score in rrf_scores.items()
    }
