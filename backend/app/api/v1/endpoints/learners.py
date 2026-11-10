from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from app.core.database import get_db
from app.models.user import User, Learner
from app.models.skill import LearnerSkill, Skill, SkillCategory, SkillEvidence
from app.models.course import CourseCompletion, AssessmentResult, PracticalProject
from app.models.job import SkillMatch, SkillGap, JobDescription
from app.models.recommendation import Recommendation, CareerReport
from app.schemas.user import LearnerResponse, LearnerProfileUpdate
from app.schemas.skill import LearnerSkillResponse
from app.schemas.course import PracticalProjectCreate, PracticalProjectResponse
from app.schemas.recommendation import DashboardStatsResponse
from app.api.deps import get_current_user, get_current_learner, create_audit_log
from ai_engine.proficiency.evaluator import proficiency_evaluator

router = APIRouter(prefix="/learners", tags=["Learners"])

@router.get("/profile", response_model=LearnerResponse)
def get_learner_profile(learner: Learner = Depends(get_current_learner), db: Session = Depends(get_db)):
    db.refresh(learner)
    return learner

@router.put("/profile", response_model=LearnerResponse)
def update_learner_profile(
    req: LearnerProfileUpdate,
    learner: Learner = Depends(get_current_learner),
    db: Session = Depends(get_db)
):
    update_data = req.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(learner, field, val)
    db.commit()
    db.refresh(learner)
    create_audit_log(db, learner.user_id, "LEARNER_PROFILE_UPDATED", "learners", learner.id)
    return learner

@router.get("/skills", response_model=List[LearnerSkillResponse])
def get_learner_skills(learner: Learner = Depends(get_current_learner), db: Session = Depends(get_db)):
    skills = db.scalars(
        select(LearnerSkill)
        .where(LearnerSkill.learner_id == learner.id)
        .order_by(LearnerSkill.proficiency_level.desc())
    ).all()
    return skills

@router.post("/projects", response_model=PracticalProjectResponse, status_code=status.HTTP_201_CREATED)
def add_practical_project(
    req: PracticalProjectCreate,
    learner: Learner = Depends(get_current_learner),
    db: Session = Depends(get_db)
):
    project = PracticalProject(
        learner_id=learner.id,
        title=req.title,
        description=req.description,
        repository_url=req.repository_url,
        live_url=req.live_url,
        demonstrated_skills=req.demonstrated_skills,
        complexity_level=req.complexity_level,
        verified=bool(req.repository_url) # Verified if public repository is linked
    )
    db.add(project)
    db.flush()

    # If project lists skills, re-evaluate proficiency for those skills
    for sk_name in req.demonstrated_skills:
        skill = db.scalar(select(Skill).where(Skill.name == sk_name))
        if skill:
            learner_skill = db.scalar(
                select(LearnerSkill)
                .where(LearnerSkill.learner_id == learner.id, LearnerSkill.skill_id == skill.id)
            )
            if not learner_skill:
                learner_skill = LearnerSkill(
                    learner_id=learner.id,
                    skill_id=skill.id,
                    proficiency_level=1,
                    confidence_score=0.7
                )
                db.add(learner_skill)
                db.flush()

            # Add evidence
            evidence = SkillEvidence(
                learner_skill_id=learner_skill.id,
                source_type="project",
                source_id=project.id,
                text_snippet=f"Implemented in practical project: {project.title}. Complexity level {project.complexity_level}.",
                confidence=0.85
            )
            db.add(evidence)

            # Re-evaluate
            eval_res = proficiency_evaluator.evaluate_skill_proficiency(
                skill_name=skill.name,
                years_experience=learner.years_of_experience,
                projects=[{"complexity_level": project.complexity_level, "verified": project.verified, "repository_url": project.repository_url}]
            )
            learner_skill.proficiency_level = eval_res["proficiency_level"]
            learner_skill.confidence_score = eval_res["confidence_score"]
            learner_skill.evidence_summary = eval_res["explanation"]

    db.commit()
    db.refresh(project)
    create_audit_log(db, learner.user_id, "PROJECT_ADDED", "practical_projects", project.id)
    return project

@router.get("/projects", response_model=List[PracticalProjectResponse])
def get_learner_projects(learner: Learner = Depends(get_current_learner), db: Session = Depends(get_db)):
    projects = db.scalars(
        select(PracticalProject)
        .where(PracticalProject.learner_id == learner.id)
        .order_by(PracticalProject.created_at.desc())
    ).all()
    return projects

@router.get("/dashboard", response_model=DashboardStatsResponse)
def get_learner_dashboard_stats(
    learner: Learner = Depends(get_current_learner),
    db: Session = Depends(get_db)
):
    total_skills = db.scalar(
        select(func.count(LearnerSkill.id)).where(LearnerSkill.learner_id == learner.id)
    ) or 0

    completed_courses = db.scalar(
        select(func.count(CourseCompletion.id)).where(CourseCompletion.learner_id == learner.id)
    ) or 0

    assessments_completed = db.scalar(
        select(func.count(AssessmentResult.id)).where(AssessmentResult.learner_id == learner.id)
    ) or 0

    practical_projects = db.scalar(
        select(func.count(PracticalProject.id)).where(PracticalProject.learner_id == learner.id)
    ) or 0

    active_recommendations = db.scalar(
        select(func.count(Recommendation.id)).where(
            Recommendation.learner_id == learner.id,
            Recommendation.status == "active"
        )
    ) or 0

    # Retrieve most recent report or match
    latest_report = db.scalar(
        select(CareerReport)
        .where(CareerReport.learner_id == learner.id)
        .order_by(CareerReport.generated_at.desc())
    )

    matched_skills = 0
    skill_gaps = 0
    readiness_score = 0.0
    target_job_title = learner.target_role or "Software Engineer"

    if latest_report:
        readiness_score = latest_report.overall_readiness_score
        target_job_title = latest_report.job.title if latest_report.job else target_job_title
        matched_skills = latest_report.breakdown.get("matched_count", 0)
        skill_gaps = len(latest_report.breakdown.get("gaps", []))
    else:
        # Check active matches
        matched_skills = db.scalar(
            select(func.count(SkillMatch.id)).where(
                SkillMatch.learner_id == learner.id,
                SkillMatch.match_type.in_(["matched", "exceeds"])
            )
        ) or 0
        skill_gaps = db.scalar(
            select(func.count(SkillGap.id)).where(SkillGap.learner_id == learner.id)
        ) or 0

    return DashboardStatsResponse(
        total_skills_identified=total_skills,
        matched_job_skills=matched_skills,
        skill_gaps=skill_gaps,
        career_readiness_score=readiness_score,
        completed_courses=completed_courses,
        assessments_completed=assessments_completed,
        active_recommendations=active_recommendations,
        practical_projects=practical_projects,
        target_job_title=target_job_title
    )
