from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import select, delete
from app.core.database import get_db
from app.models.user import Learner
from app.models.job import JobDescription, SkillGap
from app.models.course import Course
from app.models.skill import Skill
from app.models.recommendation import Recommendation, RecommendationEvidence, LearningResource
from app.schemas.recommendation import RecommendationResponse
from app.api.deps import get_current_learner, create_audit_log
from ai_engine.recommendation.recommender import recommendation_engine

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])

class StatusUpdateRequest(BaseModel):
    status: str # active, in_progress, completed, dismissed

@router.post("/generate/{job_id}", response_model=List[RecommendationResponse])
def generate_recommendations(
    job_id: str,
    learner: Learner = Depends(get_current_learner),
    db: Session = Depends(get_db)
):
    job = db.scalar(select(JobDescription).where(JobDescription.id == job_id))
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job description not found")

    gaps = db.scalars(
        select(SkillGap).where(SkillGap.learner_id == learner.id, SkillGap.job_id == job.id)
    ).all()

    if not gaps:
        # Check if matching has been run
        return []

    # Prepare gaps for recommendation engine
    gaps_data = []
    for g in gaps:
        skill = db.scalar(select(Skill).where(Skill.id == g.skill_id))
        if skill:
            gaps_data.append({
                "skill_name": skill.name,
                "required_level": g.required_level,
                "current_level": g.current_level,
                "gap_severity": g.gap_severity,
                "requirement_type": "mandatory" if g.gap_severity == "critical" else "preferred"
            })

    # Available internal courses
    available_courses = [
        {"id": c.id, "title": c.title, "description": c.description, "provider": c.provider, "estimated_hours": c.estimated_hours}
        for c in db.scalars(select(Course)).all()
    ]

    rec_items = recommendation_engine.generate_recommendations_for_gaps(gaps_data, available_courses)

    # Persist in DB
    created_recs = []
    for item in rec_items:
        skill = db.scalar(select(Skill).where(Skill.name == item["skill_name"]))
        if not skill:
            continue

        # Look up or create learning resource
        res = db.scalar(select(LearningResource).where(LearningResource.title == item["resource_title"]))
        if not res:
            res = LearningResource(
                skill_id=skill.id,
                title=item["resource_title"],
                resource_type=item["resource_type"],
                provider=item["provider"],
                url=item["url"],
                estimated_hours=item["estimated_hours"],
                target_level=item["target_level"]
            )
            db.add(res)
            db.flush()

        # Check existing recommendation
        existing = db.scalar(
            select(Recommendation).where(
                Recommendation.learner_id == learner.id,
                Recommendation.skill_id == skill.id,
                Recommendation.resource_id == res.id
            )
        )
        if not existing:
            rec = Recommendation(
                learner_id=learner.id,
                job_id=job.id,
                skill_id=skill.id,
                resource_id=res.id,
                priority=item["priority"],
                reason=item["reason"],
                expected_outcome=item["expected_outcome"],
                status="active"
            )
            db.add(rec)
            db.flush()

            evidence = RecommendationEvidence(
                recommendation_id=rec.id,
                gap_reason=item["reason"],
                current_level=item["current_level"],
                target_level=item["target_level"],
                calculation_trace={"gap_delta": item["target_level"] - item["current_level"]}
            )
            db.add(evidence)
            created_recs.append(rec)
        else:
            created_recs.append(existing)

    db.commit()
    create_audit_log(
        db, learner.user_id, "RECOMMENDATIONS_GENERATED", "recommendations", job.id,
        details={"count": len(created_recs)}
    )

    # Re-query with eager relationships
    results = db.scalars(
        select(Recommendation)
        .where(Recommendation.learner_id == learner.id)
        .order_by(Recommendation.created_at.desc())
    ).all()
    return results

@router.get("/", response_model=List[RecommendationResponse])
def list_recommendations(
    learner: Learner = Depends(get_current_learner),
    db: Session = Depends(get_db)
):
    recs = db.scalars(
        select(Recommendation)
        .where(Recommendation.learner_id == learner.id)
        .order_by(Recommendation.created_at.desc())
    ).all()
    return recs

@router.patch("/{recommendation_id}/status", response_model=RecommendationResponse)
def update_recommendation_status(
    recommendation_id: str,
    req: StatusUpdateRequest,
    learner: Learner = Depends(get_current_learner),
    db: Session = Depends(get_db)
):
    rec = db.scalar(
        select(Recommendation).where(
            Recommendation.id == recommendation_id,
            Recommendation.learner_id == learner.id
        )
    )
    if not rec:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recommendation not found")
    rec.status = req.status
    db.commit()
    db.refresh(rec)
    return rec
