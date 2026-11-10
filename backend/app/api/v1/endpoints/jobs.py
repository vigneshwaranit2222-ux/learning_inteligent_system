import hashlib
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import select, or_
from app.core.database import get_db
from app.models.job import JobRole, JobDescription, JobRequirement
from app.models.skill import Skill
from app.schemas.job import JobDescriptionSchema, JobCreateRequest
from app.api.deps import get_current_user, create_audit_log
from ai_engine.extraction.extractor import extractor

router = APIRouter(prefix="/jobs", tags=["Job Descriptions"])

@router.get("/", response_model=List[JobDescriptionSchema])
def list_jobs(
    query: Optional[str] = None,
    location: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    stmt = select(JobDescription).where(JobDescription.is_active == True)
    if query:
        stmt = stmt.where(
            or_(
                JobDescription.title.ilike(f"%{query}%"),
                JobDescription.company_name.ilike(f"%{query}%"),
                JobDescription.raw_text.ilike(f"%{query}%")
            )
        )
    if location:
        stmt = stmt.where(JobDescription.location.ilike(f"%{location}%"))
    stmt = stmt.offset(skip).limit(limit)
    jobs = db.scalars(stmt).all()
    return jobs

@router.get("/{job_id}", response_model=JobDescriptionSchema)
def get_job_details(job_id: str, db: Session = Depends(get_db)):
    job = db.scalar(select(JobDescription).where(JobDescription.id == job_id))
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job description not found")
    return job

@router.post("/", response_model=JobDescriptionSchema, status_code=status.HTTP_201_CREATED)
def create_job(
    req: JobCreateRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Role
    role = db.scalar(select(JobRole).where(JobRole.title == req.role_title))
    if not role:
        role = JobRole(title=req.role_title, industry="Information Technology")
        db.add(role)
        db.flush()

    file_hash = hashlib.sha256(req.raw_text.strip().encode("utf-8")).hexdigest()

    job_desc = JobDescription(
        role_id=role.id,
        title=req.title,
        company_name=req.company_name,
        location=req.location,
        employment_type=req.employment_type,
        experience_required=req.experience_required,
        raw_text=req.raw_text.strip(),
        file_hash=file_hash,
        source_url=req.source_url,
        is_active=True
    )
    db.add(job_desc)
    db.flush()

    # Automatically extract requirements from the raw text
    extracted = extractor.extract_skills_from_text(req.raw_text, source_type="job_description")
    for item in extracted:
        sk = db.scalar(select(Skill).where(Skill.name == item["canonical_name"]))
        if sk:
            jr = JobRequirement(
                job_id=job_desc.id,
                skill_id=sk.id,
                required_level=2,
                requirement_type="mandatory",
                importance_weight=1.5
            )
            db.add(jr)

    db.commit()
    db.refresh(job_desc)
    create_audit_log(db, current_user.id, "JOB_DESCRIPTION_CREATED", "job_descriptions", job_desc.id)
    return job_desc
