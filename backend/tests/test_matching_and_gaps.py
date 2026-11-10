import pytest
from ai_engine.matching.matcher import skill_matcher

def test_skill_matching_and_readiness_calculation():
    learner_skills = {
        "Python": {"proficiency_level": 3, "confidence_score": 0.9, "category": "Programming"},
        "FastAPI": {"proficiency_level": 2, "confidence_score": 0.9, "category": "Backend Development"}
    }

    job_requirements = [
        {"skill_name": "Python", "required_level": 3, "requirement_type": "mandatory", "category": "Programming"},
        {"skill_name": "FastAPI", "required_level": 3, "requirement_type": "mandatory", "category": "Backend Development"},
        {"skill_name": "Docker", "required_level": 2, "requirement_type": "mandatory", "category": "DevOps"}
    ]

    res = skill_matcher.match_learner_against_job(learner_skills, job_requirements)
    assert res["matched_count"] == 1 # Python
    assert res["partial_count"] == 1 # FastAPI (L2 vs required L3)
    assert res["missing_count"] == 1 # Docker

    # Readiness calculation check:
    # Python: 1.5 * 3 = 4.5 demonstrated / 4.5 req
    # FastAPI: 1.5 * min(2, 3) = 3.0 demonstrated / 4.5 req
    # Docker: 1.5 * 0 = 0.0 demonstrated / 3.0 req
    # Total demonstrated = 7.5; Total req = 12.0
    # Expected score = (7.5 / 12.0) * 100 = 62.5%
    assert abs(res["readiness_score"] - 62.5) < 0.1

    # Verify gaps
    gap_skills = [g["skill_name"] for g in res["gaps"]]
    assert "FastAPI" in gap_skills
    assert "Docker" in gap_skills
