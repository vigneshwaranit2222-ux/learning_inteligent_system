import os
import uuid
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.core.config import settings
from app.core.database import get_db
from app.models.user import User, Learner
from app.models.course import Resume
from app.models.skill import Skill, LearnerSkill, SkillEvidence
from app.api.deps import get_current_learner, create_audit_log
from app.services.ingestion.document_parser import document_parser
from ai_engine.extraction.extractor import extractor
from ai_engine.proficiency.evaluator import proficiency_evaluator

router = APIRouter(prefix="/resumes", tags=["Resumes"])

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc", ".txt", ".md"}

@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    learner: Learner = Depends(get_current_learner),
    db: Session = Depends(get_db)
):
    # Validate extension
    filename = file.filename or "uploaded_resume.txt"
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '{ext}'. Allowed formats: {list(ALLOWED_EXTENSIONS)}"
        )

    # Read content & validate size
    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE_MB}MB."
        )

    # Compute SHA-256
    file_hash = document_parser.compute_sha256(content)

    # Check duplicate
    existing_resume = db.scalar(
        select(Resume).where(Resume.learner_id == learner.id, Resume.file_hash == file_hash)
    )
    if existing_resume:
        return {
            "message": "Resume with identical content already processed.",
            "resume_id": existing_resume.id,
            "filename": existing_resume.filename,
            "status": existing_resume.processing_status,
            "is_duplicate": True
        }

    # Save to disk
    stored_filename = f"{uuid.uuid4()}_{filename}"
    file_path = os.path.join(settings.UPLOAD_DIR, stored_filename)
    with open(file_path, "wb") as f:
        f.write(content)

    # Parse text
    try:
        raw_text, _ = document_parser.parse_document(file_path, filename)
        parsed_sections = document_parser.segment_resume_sections(raw_text)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to parse document text: {str(e)}"
        )

    # Create Resume entity
    resume = Resume(
        learner_id=learner.id,
        filename=filename,
        file_hash=file_hash,
        mime_type=file.content_type or "application/octet-stream",
        file_path=file_path,
        raw_text=raw_text,
        parsed_sections=parsed_sections,
        processing_status="processed"
    )
    db.add(resume)
    db.flush()

    # Extract Skills
    extracted_skills = extractor.extract_skills_from_text(raw_text, source_type="resume")
    skills_linked = 0

    for item in extracted_skills:
        canonical_name = item["canonical_name"]
        skill = db.scalar(select(Skill).where(Skill.name == canonical_name))
        if not skill:
            continue

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
                confidence_score=item["confidence"]
            )
            db.add(learner_skill)
            db.flush()

        # Add evidence record
        evidence = SkillEvidence(
            learner_skill_id=learner_skill.id,
            source_type="resume",
            source_id=resume.id,
            text_snippet=item["evidence_snippet"],
            confidence=item["confidence"],
            source_metadata={
                "start_char": item.get("start_char"),
                "end_char": item.get("end_char"),
                "extraction_method": item.get("extraction_method")
            }
        )
        db.add(evidence)

        # Evaluate proficiency
        eval_res = proficiency_evaluator.evaluate_skill_proficiency(
            skill_name=skill.name,
            years_experience=learner.years_of_experience,
            has_resume_mention=True
        )
        learner_skill.proficiency_level = eval_res["proficiency_level"]
        learner_skill.confidence_score = eval_res["confidence_score"]
        learner_skill.evidence_summary = eval_res["explanation"]
        skills_linked += 1

    db.commit()
    db.refresh(resume)

    create_audit_log(
        db, learner.user_id, "RESUME_UPLOADED", "resumes", resume.id,
        details={"filename": filename, "skills_extracted": len(extracted_skills)}
    )

    return {
        "message": f"Resume uploaded and processed successfully. Extracted {skills_linked} skills.",
        "resume_id": resume.id,
        "filename": filename,
        "total_skills_extracted": skills_linked,
        "skills": extracted_skills
    }

@router.get("/list")
def list_resumes(learner: Learner = Depends(get_current_learner), db: Session = Depends(get_db)):
    resumes = db.scalars(
        select(Resume)
        .where(Resume.learner_id == learner.id)
        .order_by(Resume.created_at.desc())
    ).all()
    return [
        {
            "id": r.id,
            "filename": r.filename,
            "created_at": r.created_at,
            "processing_status": r.processing_status,
            "file_hash": r.file_hash
        }
        for r in resumes
    ]

@router.get("/{resume_id}")
def get_resume_details(resume_id: str, learner: Learner = Depends(get_current_learner), db: Session = Depends(get_db)):
    resume = db.scalar(
        select(Resume).where(Resume.id == resume_id, Resume.learner_id == learner.id)
    )
    if not resume:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume record not found")
    return {
        "id": resume.id,
        "filename": resume.filename,
        "raw_text": resume.raw_text,
        "parsed_sections": resume.parsed_sections,
        "created_at": resume.created_at
    }
