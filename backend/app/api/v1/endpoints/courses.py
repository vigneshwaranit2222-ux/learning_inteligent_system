from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import select, or_
from app.core.database import get_db
from app.models.course import Course, CourseCompletion, LearningOutcome
from app.models.skill import Skill, LearnerSkill, SkillEvidence
from app.models.user import Learner
from app.schemas.course import CourseSchema, CourseCompletionCreate, CourseCompletionResponse
from app.api.deps import get_current_learner, create_audit_log
from ai_engine.proficiency.evaluator import proficiency_evaluator

router = APIRouter(prefix="/courses", tags=["Courses"])

@router.get("/", response_model=List[CourseSchema])
def list_courses(
    query: Optional[str] = None,
    difficulty: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    stmt = select(Course)
    if query:
        stmt = stmt.where(
            or_(
                Course.title.ilike(f"%{query}%"),
                Course.description.ilike(f"%{query}%"),
                Course.provider.ilike(f"%{query}%")
            )
        )
    if difficulty:
        stmt = stmt.where(Course.difficulty == difficulty.lower())

    stmt = stmt.offset(skip).limit(limit)
    courses = db.scalars(stmt).all()
    return courses

@router.get("/{course_id}", response_model=CourseSchema)
def get_course_details(course_id: str, db: Session = Depends(get_db)):
    course = db.scalar(select(Course).where(Course.id == course_id))
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return course

@router.post("/complete", response_model=CourseCompletionResponse, status_code=status.HTTP_201_CREATED)
def complete_course(
    req: CourseCompletionCreate,
    learner: Learner = Depends(get_current_learner),
    db: Session = Depends(get_db)
):
    course = db.scalar(select(Course).where(Course.id == req.course_id))
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    existing_completion = db.scalar(
        select(CourseCompletion).where(
            CourseCompletion.learner_id == learner.id,
            CourseCompletion.course_id == course.id
        )
    )
    if existing_completion:
        return existing_completion

    completion = CourseCompletion(
        learner_id=learner.id,
        course_id=course.id,
        completion_date=req.completion_date or datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        certificate_url=req.certificate_url,
        grade=req.grade or "Completed",
        verified_by="System"
    )
    db.add(completion)
    db.flush()

    # Apply learning outcomes to learner skills
    for outcome in course.learning_outcomes:
        skill = db.scalar(select(Skill).where(Skill.id == outcome.skill_id))
        if skill:
            learner_skill = db.scalar(
                select(LearnerSkill).where(
                    LearnerSkill.learner_id == learner.id,
                    LearnerSkill.skill_id == skill.id
                )
            )
            if not learner_skill:
                learner_skill = LearnerSkill(
                    learner_id=learner.id,
                    skill_id=skill.id,
                    proficiency_level=1,
                    confidence_score=0.8
                )
                db.add(learner_skill)
                db.flush()

            # Record evidence
            evidence = SkillEvidence(
                learner_skill_id=learner_skill.id,
                source_type="course",
                source_id=course.id,
                text_snippet=f"Completed course: {course.title} ({course.provider}). Learning outcome: {outcome.outcome_statement}",
                confidence=0.85
            )
            db.add(evidence)

            # Re-evaluate proficiency with course component
            eval_res = proficiency_evaluator.evaluate_skill_proficiency(
                skill_name=skill.name,
                years_experience=learner.years_of_experience,
                course_completions=[{"id": course.id, "title": course.title}]
            )
            learner_skill.proficiency_level = max(learner_skill.proficiency_level, eval_res["proficiency_level"])
            learner_skill.evidence_summary = eval_res["explanation"]

    db.commit()
    db.refresh(completion)
    create_audit_log(db, learner.user_id, "COURSE_COMPLETED", "courses", course.id)
    return completion

@router.get("/my/completions", response_model=List[CourseCompletionResponse])
def get_my_completions(
    learner: Learner = Depends(get_current_learner),
    db: Session = Depends(get_db)
):
    completions = db.scalars(
        select(CourseCompletion)
        .where(CourseCompletion.learner_id == learner.id)
        .order_by(CourseCompletion.created_at.desc())
    ).all()
    return completions
