from typing import Optional, List
from sqlalchemy import String, Integer, Float, ForeignKey, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import UUIDMixin, TimestampMixin

class LearningResource(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "learning_resources"

    skill_id: Mapped[str] = mapped_column(String(36), ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(50), nullable=False) # course, tutorial, documentation, project, certification
    provider: Mapped[str] = mapped_column(String(100), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    estimated_hours: Mapped[int] = mapped_column(Integer, default=5)
    target_level: Mapped[int] = mapped_column(Integer, default=2) # 1-4

    skill: Mapped["Skill"] = relationship("Skill", back_populates="learning_resources")
    recommendations: Mapped[List["Recommendation"]] = relationship("Recommendation", back_populates="resource")

class Recommendation(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "recommendations"

    learner_id: Mapped[str] = mapped_column(String(36), ForeignKey("learners.id", ondelete="CASCADE"), nullable=False)
    job_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("job_descriptions.id", ondelete="SET NULL"), nullable=True)
    skill_id: Mapped[str] = mapped_column(String(36), ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)
    resource_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("learning_resources.id", ondelete="SET NULL"), nullable=True)
    priority: Mapped[str] = mapped_column(String(50), default="high") # high, medium, low
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    expected_outcome: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="active") # active, in_progress, completed, dismissed

    learner: Mapped["Learner"] = relationship("Learner", back_populates="recommendations")
    resource: Mapped[Optional["LearningResource"]] = relationship("LearningResource", back_populates="recommendations")
    skill: Mapped["Skill"] = relationship("Skill")
    evidence_trail: Mapped[List["RecommendationEvidence"]] = relationship("RecommendationEvidence", back_populates="recommendation", cascade="all, delete-orphan")

class RecommendationEvidence(Base, UUIDMixin):
    __tablename__ = "recommendation_evidence"

    recommendation_id: Mapped[str] = mapped_column(String(36), ForeignKey("recommendations.id", ondelete="CASCADE"), nullable=False)
    gap_reason: Mapped[str] = mapped_column(Text, nullable=False)
    current_level: Mapped[int] = mapped_column(Integer, default=0)
    target_level: Mapped[int] = mapped_column(Integer, default=2)
    calculation_trace: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    recommendation: Mapped["Recommendation"] = relationship("Recommendation", back_populates="evidence_trail")

class CareerReport(Base, UUIDMixin):
    __tablename__ = "career_reports"

    learner_id: Mapped[str] = mapped_column(String(36), ForeignKey("learners.id", ondelete="CASCADE"), nullable=False)
    job_id: Mapped[str] = mapped_column(String(36), ForeignKey("job_descriptions.id", ondelete="CASCADE"), nullable=False)
    overall_readiness_score: Mapped[float] = mapped_column(Float, nullable=False) # 0.0 - 100.0
    breakdown: Mapped[dict] = mapped_column(JSON, nullable=False)
    executive_summary: Mapped[str] = mapped_column(Text, nullable=False)
    calculation_evidence: Mapped[dict] = mapped_column(JSON, nullable=False)
    pdf_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    generated_at: Mapped[str] = mapped_column(String(50), nullable=False)

    learner: Mapped["Learner"] = relationship("Learner", back_populates="career_reports")
    job: Mapped["JobDescription"] = relationship("JobDescription", back_populates="career_reports")

class ProcessingJob(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "processing_jobs"

    job_type: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="pending") # pending, processing, completed, failed
    payload: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    result: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), index=True, nullable=True)
    finished_at: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
