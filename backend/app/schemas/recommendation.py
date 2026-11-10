from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel
from app.schemas.skill import SkillSchema

class LearningResourceSchema(BaseModel):
    id: str
    skill_id: str
    title: str
    resource_type: str # course, tutorial, documentation, project, certification
    provider: str
    url: str
    estimated_hours: int
    target_level: int
    skill: Optional[SkillSchema] = None

    class Config:
        from_attributes = True

class RecommendationEvidenceSchema(BaseModel):
    gap_reason: str
    current_level: int
    target_level: int
    calculation_trace: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

class RecommendationResponse(BaseModel):
    id: str
    learner_id: str
    job_id: Optional[str] = None
    skill_id: str
    skill: SkillSchema
    resource_id: Optional[str] = None
    resource: Optional[LearningResourceSchema] = None
    priority: str # high, medium, low
    reason: str
    expected_outcome: str
    status: str # active, in_progress, completed, dismissed
    evidence_trail: List[RecommendationEvidenceSchema] = []
    created_at: datetime

    class Config:
        from_attributes = True

class CareerReportResponse(BaseModel):
    id: str
    learner_id: str
    job_id: str
    job_title: str
    company_name: str
    overall_readiness_score: float
    breakdown: Dict[str, Any]
    executive_summary: str
    calculation_evidence: Dict[str, Any]
    pdf_path: Optional[str] = None
    generated_at: str

    class Config:
        from_attributes = True

class DashboardStatsResponse(BaseModel):
    total_skills_identified: int
    matched_job_skills: int
    skill_gaps: int
    career_readiness_score: float
    completed_courses: int
    assessments_completed: int
    active_recommendations: int
    practical_projects: int
    target_job_title: Optional[str] = None
