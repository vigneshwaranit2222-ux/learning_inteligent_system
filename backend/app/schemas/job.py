from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from app.schemas.skill import SkillSchema

class JobRoleSchema(BaseModel):
    id: str
    title: str
    industry: str
    standard_code: Optional[str] = None

    class Config:
        from_attributes = True

class JobRequirementSchema(BaseModel):
    id: str
    skill_id: str
    skill: SkillSchema
    required_level: int
    requirement_type: str # mandatory, preferred, optional
    importance_weight: float

    class Config:
        from_attributes = True

class JobDescriptionSchema(BaseModel):
    id: str
    role_id: str
    role: JobRoleSchema
    title: str
    company_name: str
    location: Optional[str] = None
    employment_type: str
    experience_required: Optional[str] = None
    raw_text: str
    source_url: Optional[str] = None
    is_active: bool
    requirements: List[JobRequirementSchema] = []
    created_at: datetime

    class Config:
        from_attributes = True

class JobCreateRequest(BaseModel):
    role_title: str
    title: str
    company_name: str
    location: Optional[str] = None
    employment_type: str = "Full-time"
    experience_required: Optional[str] = "2-4 years"
    raw_text: str
    source_url: Optional[str] = None

class SkillMatchItem(BaseModel):
    skill_id: str
    skill_name: str
    category: str
    match_type: str # matched, partial, missing, insufficient, exceeds
    learner_level: int
    required_level: int
    requirement_type: str # mandatory, preferred, optional
    importance_weight: float
    score_delta: float
    confidence: float
    evidence_snippet: Optional[str] = None

class SkillGapItem(BaseModel):
    skill_id: str
    skill_name: str
    category: str
    required_level: int
    current_level: int
    gap_severity: str # critical, moderate, minor
    requirement_type: str

class MatchingResultResponse(BaseModel):
    job_id: str
    job_title: str
    company_name: str
    learner_id: str
    total_required_skills: int
    matched_count: int
    partial_count: int
    missing_count: int
    readiness_score: float # 0.0 - 100.0
    matches: List[SkillMatchItem]
    gaps: List[SkillGapItem]
