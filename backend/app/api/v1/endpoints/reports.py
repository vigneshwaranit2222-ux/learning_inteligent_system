import os
from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.core.config import settings
from app.core.database import get_db
from app.models.user import Learner
from app.models.job import JobDescription
from app.models.recommendation import CareerReport, Recommendation
from app.schemas.recommendation import CareerReportResponse
from app.api.deps import get_current_learner, create_audit_log
from app.services.reporting.pdf_generator import pdf_report_generator
from ai_engine.matching.matcher import skill_matcher
from app.api.v1.endpoints.matching import match_learner_with_job

router = APIRouter(prefix="/reports", tags=["Career Readiness Reports"])

@router.post("/generate/{job_id}", response_model=CareerReportResponse, status_code=status.HTTP_201_CREATED)
def generate_career_report(
    job_id: str,
    learner: Learner = Depends(get_current_learner),
    db: Session = Depends(get_db)
):
    job = db.scalar(select(JobDescription).where(JobDescription.id == job_id))
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job description not found")

    # Run matching first to guarantee fresh match & gap data
    matching_result = match_learner_with_job(job_id=job.id, learner=learner, db=db)

    # Fetch active recommendations
    recs = db.scalars(
        select(Recommendation).where(Recommendation.learner_id == learner.id)
    ).all()
    recs_data = [
        {
            "resource_title": r.resource.title if r.resource else r.skill.name,
            "provider": r.resource.provider if r.resource else "Online",
            "estimated_hours": r.resource.estimated_hours if r.resource else 10,
            "expected_outcome": r.expected_outcome,
            "reason": r.reason
        }
        for r in recs[:5]
    ]

    # Generate Executive Summary
    learner_name = learner.user.full_name if learner.user else "Learner"
    score = matching_result.readiness_score
    status_label = "Strong Fit" if score >= 80 else ("Moderate Alignment" if score >= 60 else "Development Opportunity")
    summary = (
        f"Evaluation for {learner_name} against target role '{job.title}' ({job.company_name}) "
        f"indicates an overall career readiness score of {score}% ({status_label}). "
        f"Out of {matching_result.total_required_skills} required competencies, {matching_result.matched_count} are fully matched, "
        f"{matching_result.partial_count} are partially demonstrated, and {matching_result.missing_count} require focused upskilling."
    )

    now_iso = datetime.now(timezone.utc).isoformat()
    pdf_filename = f"career_report_{learner.id[:8]}_{job.id[:8]}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    pdf_path = os.path.join(settings.REPORTS_DIR, pdf_filename)

    # Generate PDF
    pdf_report_generator.generate_career_report_pdf(
        output_path=pdf_path,
        learner_name=learner_name,
        job_title=job.title,
        company_name=job.company_name,
        readiness_score=score,
        matches=[m.model_dump() for m in matching_result.matches],
        gaps=[g.model_dump() for g in matching_result.gaps],
        recommendations=recs_data,
        calculation_trace={"formula": "Deterministic weighted skill coverage"}
    )

    report = CareerReport(
        learner_id=learner.id,
        job_id=job.id,
        overall_readiness_score=score,
        breakdown=matching_result.model_dump(),
        executive_summary=summary,
        calculation_evidence={
            "matched_count": matching_result.matched_count,
            "partial_count": matching_result.partial_count,
            "missing_count": matching_result.missing_count,
            "total_skills": matching_result.total_required_skills
        },
        pdf_path=pdf_path,
        generated_at=now_iso
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    create_audit_log(
        db, learner.user_id, "CAREER_REPORT_GENERATED", "career_reports", report.id,
        details={"score": score, "job_title": job.title}
    )

    return CareerReportResponse(
        id=report.id,
        learner_id=learner.id,
        job_id=job.id,
        job_title=job.title,
        company_name=job.company_name,
        overall_readiness_score=score,
        breakdown=report.breakdown,
        executive_summary=summary,
        calculation_evidence=report.calculation_evidence,
        pdf_path=f"/api/v1/reports/{report.id}/pdf",
        generated_at=report.generated_at
    )

@router.get("/", response_model=List[CareerReportResponse])
def list_reports(
    learner: Learner = Depends(get_current_learner),
    db: Session = Depends(get_db)
):
    reports = db.scalars(
        select(CareerReport)
        .where(CareerReport.learner_id == learner.id)
        .order_by(CareerReport.generated_at.desc())
    ).all()

    return [
        CareerReportResponse(
            id=r.id,
            learner_id=r.learner_id,
            job_id=r.job_id,
            job_title=r.job.title if r.job else "Target Role",
            company_name=r.job.company_name if r.job else "Target Company",
            overall_readiness_score=r.overall_readiness_score,
            breakdown=r.breakdown,
            executive_summary=r.executive_summary,
            calculation_evidence=r.calculation_evidence,
            pdf_path=f"/api/v1/reports/{r.id}/pdf",
            generated_at=r.generated_at
        )
        for r in reports
    ]

@router.get("/{report_id}", response_model=CareerReportResponse)
def get_report(report_id: str, db: Session = Depends(get_db)):
    r = db.scalar(select(CareerReport).where(CareerReport.id == report_id))
    if not r:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    return CareerReportResponse(
        id=r.id,
        learner_id=r.learner_id,
        job_id=r.job_id,
        job_title=r.job.title if r.job else "Target Role",
        company_name=r.job.company_name if r.job else "Target Company",
        overall_readiness_score=r.overall_readiness_score,
        breakdown=r.breakdown,
        executive_summary=r.executive_summary,
        calculation_evidence=r.calculation_evidence,
        pdf_path=f"/api/v1/reports/{r.id}/pdf",
        generated_at=r.generated_at
    )

@router.get("/{report_id}/pdf")
def download_report_pdf(report_id: str, db: Session = Depends(get_db)):
    r = db.scalar(select(CareerReport).where(CareerReport.id == report_id))
    if not r or not r.pdf_path or not os.path.exists(r.pdf_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PDF report file not found on disk")
    return FileResponse(
        r.pdf_path,
        media_type="application/pdf",
        filename=os.path.basename(r.pdf_path)
    )
