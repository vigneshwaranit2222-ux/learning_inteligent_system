from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from app.core.database import get_db
from app.models.user import User, Learner, AuditLog
from app.models.course import Resume, Course, AssessmentResult
from app.models.job import JobDescription
from app.models.skill import Skill
from app.models.recommendation import Recommendation, CareerReport, ProcessingJob
from app.schemas.user import UserResponse
from app.schemas.admin import SystemAnalyticsResponse, AuditLogResponse, ProcessingJobResponse
from app.api.deps import get_current_admin, create_audit_log

router = APIRouter(prefix="/admin", tags=["Admin Portal"])

class UserStatusUpdate(BaseModel):
    is_active: bool

@router.get("/analytics", response_model=SystemAnalyticsResponse)
def get_system_analytics(admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    total_users = db.scalar(select(func.count(User.id))) or 0
    total_learners = db.scalar(select(func.count(Learner.id))) or 0
    total_resumes = db.scalar(select(func.count(Resume.id))) or 0
    total_skills = db.scalar(select(func.count(Skill.id))) or 0
    total_courses = db.scalar(select(func.count(Course.id))) or 0
    total_assessments = db.scalar(select(func.count(AssessmentResult.id))) or 0
    total_jobs = db.scalar(select(func.count(JobDescription.id))) or 0
    total_recs = db.scalar(select(func.count(Recommendation.id))) or 0
    total_reports = db.scalar(select(func.count(CareerReport.id))) or 0
    recent_activity = db.scalar(select(func.count(AuditLog.id))) or 0

    return SystemAnalyticsResponse(
        total_users=total_users,
        total_learners=total_learners,
        total_resumes_uploaded=total_resumes,
        total_skills_cataloged=total_skills,
        total_courses_available=total_courses,
        total_assessments_taken=total_assessments,
        total_job_descriptions=total_jobs,
        total_recommendations_generated=total_recs,
        total_career_reports=total_reports,
        recent_activity_count=recent_activity
    )

@router.get("/users", response_model=List[UserResponse])
def list_system_users(
    skip: int = 0,
    limit: int = 50,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    users = db.scalars(select(User).order_by(User.created_at.desc()).offset(skip).limit(limit)).all()
    return users

@router.patch("/users/{user_id}/status", response_model=UserResponse)
def update_user_status(
    user_id: str,
    req: UserStatusUpdate,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    user = db.scalar(select(User).where(User.id == user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user.is_active = req.is_active
    db.commit()
    db.refresh(user)
    create_audit_log(
        db, admin.id, "USER_STATUS_UPDATED", "users", user.id,
        details={"new_status": req.is_active}
    )
    return user

@router.get("/audit-logs", response_model=List[AuditLogResponse])
def get_audit_logs(
    skip: int = 0,
    limit: int = 50,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    logs = db.scalars(select(AuditLog).order_by(AuditLog.created_at.desc()).offset(skip).limit(limit)).all()
    return logs

@router.get("/processing-jobs", response_model=List[ProcessingJobResponse])
def get_processing_jobs(
    skip: int = 0,
    limit: int = 50,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    jobs = db.scalars(select(ProcessingJob).order_by(ProcessingJob.created_at.desc()).offset(skip).limit(limit)).all()
    return jobs
