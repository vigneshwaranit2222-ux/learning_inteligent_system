import pytest
from ai_engine.proficiency.evaluator import proficiency_evaluator

def test_resume_only_guardrail():
    # An individual claiming 10 years of experience on resume alone with NO projects or assessments
    # must be capped at Level 2 (Intermediate)
    res = proficiency_evaluator.evaluate_skill_proficiency(
        skill_name="Python",
        years_experience=10.0,
        projects=[],
        assessments=[],
        has_resume_mention=True
    )
    assert res["proficiency_level"] <= 2
    assert res["guardrail_applied"] is True

def test_advanced_proficiency_with_assessment_and_project():
    # With verified project and assessment, level can advance to 3 or 4
    res = proficiency_evaluator.evaluate_skill_proficiency(
        skill_name="FastAPI",
        years_experience=3.0,
        projects=[{"complexity_level": 3, "verified": True, "repository_url": "https://github.com/test/repo"}],
        assessments=[{"score_percentage": 95.0, "passed": True}],
        course_completions=[{"id": "c1", "title": "FastAPI Mastery"}]
    )
    assert res["proficiency_level"] >= 3
    assert res["confidence_score"] >= 0.8
