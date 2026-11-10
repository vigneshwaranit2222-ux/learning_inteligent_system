from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel

class SystemAnalyticsResponse(BaseModel):
    total_users: int
    total_learners: int
    total_resumes_uploaded: int
    total_skills_cataloged: int
    total_courses_available: int
    total_assessments_taken: int
    total_job_descriptions: int
    total_recommendations_generated: int
    total_career_reports: int
    recent_activity_count: int

class ProcessingJobResponse(BaseModel):
    id: str
    job_type: str
    status: str
    payload: Optional[Dict[str, Any]] = None
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    correlation_id: Optional[str] = None
    created_at: datetime
    finished_at: Optional[str] = None

    class Config:
        from_attributes = True

class AuditLogResponse(BaseModel):
    id: str
    user_id: Optional[str] = None
    action: str
    entity_name: str
    entity_id: Optional[str] = None
    correlation_id: Optional[str] = None
    ip_address: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    created_at: str

    class Config:
        from_attributes = True
