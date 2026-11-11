from datetime import date

from kb_server import _apply_recency, _freshness_factor

TODAY = date(2026, 8, 28)


def test_freshness_factor_decays_but_keeps_a_floor():
    current = _freshness_factor("2026-08-28", TODAY)
    two_years = _freshness_factor("2024-08-28", TODAY)
    very_old = _freshness_factor("2010-01-01", TODAY)

    assert current == 1.0
    assert 0.84 < two_years < 0.86
    assert 0.70 <= very_old < two_years


def test_invalid_or_missing_dates_are_conservatively_downgraded():
    assert _freshness_factor("", TODAY) == 0.75
    assert _freshness_factor("unknown", TODAY) == 0.75


def test_recency_breaks_close_relevance_ties_in_favor_of_newer_docs():
    scores = {1: 0.030, 2: 0.031}
    dates = {1: "2026-08-01", 2: "2022-08-01"}

    reranked = _apply_recency(scores, dates, TODAY)

    assert reranked[1] > reranked[2]


def test_high_relevance_old_doc_can_still_beat_weak_new_doc():
    scores = {1: 0.020, 2: 0.032}
    dates = {1: "2026-08-01", 2: "2020-08-01"}

    reranked = _apply_recency(scores, dates, TODAY)

    assert reranked[2] > reranked[1]
