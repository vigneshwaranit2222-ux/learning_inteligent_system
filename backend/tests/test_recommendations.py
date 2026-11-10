import pytest
from ai_engine.recommendation.recommender import recommendation_engine

def test_recommendation_generation():
    gaps = [
        {
            "skill_name": "Docker",
            "required_level": 2,
            "current_level": 0,
            "gap_severity": "critical",
            "requirement_type": "mandatory"
        }
    ]

    recs = recommendation_engine.generate_recommendations_for_gaps(gaps)
    assert len(recs) > 0
    first_rec = recs[0]
    assert first_rec["skill_name"] == "Docker"
    assert first_rec["priority"] == "high"
    assert "url" in first_rec
    assert "outcome" in first_rec or "expected_outcome" in first_rec
