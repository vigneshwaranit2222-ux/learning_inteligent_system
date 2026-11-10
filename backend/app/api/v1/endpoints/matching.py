from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, delete
from app.core.database import get_db
from app.models.user import Learner
from app.models.job import JobDescription, JobRequirement, SkillMatch, SkillGap
from app.models.skill import LearnerSkill, Skill
from app.schemas.job import MatchingResultResponse, SkillMatchItem, SkillGapItem
from app.api.deps import get_current_learner, create_audit_log
from ai_engine.matching.matcher import skill_matcher

router = APIRouter(prefix="/matching", tags=["Skill Matching & Gap Analysis"])

@router.post("/match/{job_id}", response_model=MatchingResultResponse)
def match_learner_with_job(
    job_id: str,
    learner: Learner = Depends(get_current_learner),
    db: Session = Depends(get_db)
):
    job = db.scalar(select(JobDescription).where(JobDescription.id == job_id))
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job description not found")

    requirements = job.requirements
    if not requirements:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Job description has no configured skill requirements")

    # Fetch learner's current demonstrated skills
    learner_skills_records = db.scalars(
        select(LearnerSkill).where(LearnerSkill.learner_id == learner.id)
    ).all()

    learner_skills_map: Dict[str, Dict[str, Any]] = {}
    for ls in learner_skills_records:
        if ls.skill:
            learner_skills_map[ls.skill.name] = {
                "proficiency_level": ls.proficiency_level,
                "confidence_score": ls.confidence_score,
                "evidence_summary": ls.evidence_summary or "",
                "category": ls.skill.category.name if ls.skill.category else "General"
            }

    # Format job requirements for matching engine
    job_reqs_data = []
    for r in requirements:
        if r.skill:
            job_reqs_data.append({
                "skill_id": r.skill_id,
                "skill_name": r.skill.name,
                "required_level": r.required_level,
                "requirement_type": r.requirement_type,
                "category": r.skill.category.name if r.skill.category else "General"
            })

    # Execute deterministic matching
    match_result = skill_matcher.match_learner_against_job(learner_skills_map, job_reqs_data)

    # Persist matches and gaps in database (clear previous for this job/learner combo)
    db.execute(delete(SkillMatch).where(SkillMatch.learner_id == learner.id, SkillMatch.job_id == job.id))
    db.execute(delete(SkillGap).where(SkillGap.learner_id == learner.id, SkillGap.job_id == job.id))
    db.flush()

    for m in match_result["matches"]:
        sm = SkillMatch(
            learner_id=learner.id,
            job_id=job.id,
            skill_id=m["skill_id"],
            match_type=m["match_type"],
            learner_level=m["learner_level"],
            required_level=m["required_level"],
            score_delta=m["score_delta"],
            confidence=m["confidence"]
        )
        db.add(sm)

    for g in match_result["gaps"]:
        sg = SkillGap(
            learner_id=learner.id,
            job_id=job.id,
            skill_id=g["skill_id"],
            required_level=g["required_level"],
            current_level=g["current_level"],
            gap_severity=g["gap_severity"]
        )
        db.add(sg)

    db.commit()

    create_audit_log(
        db, learner.user_id, "SKILL_MATCHING_EVALUATED", "job_descriptions", job.id,
        details={"readiness_score": match_result["readiness_score"], "gaps_count": len(match_result["gaps"])}
    )

    return MatchingResultResponse(
        job_id=job.id,
        job_title=job.title,
        company_name=job.company_name,
        learner_id=learner.id,
        total_required_skills=match_result["total_required_skills"],
        matched_count=match_result["matched_count"],
        partial_count=match_result["partial_count"],
        missing_count=match_result["missing_count"],
        readiness_score=match_result["readiness_score"],
        matches=[SkillMatchItem(**item) for item in match_result["matches"]],
        gaps=[SkillGapItem(**item) for item in match_result["gaps"]]
    )
