from typing import Optional, List
from sqlalchemy import String, Boolean, Float, ForeignKey, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import UUIDMixin, TimestampMixin

class User(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), default="learner", nullable=False) # admin, learner, mentor
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    learner_profile: Mapped[Optional["Learner"]] = relationship("Learner", back_populates="user", uselist=False, cascade="all, delete-orphan")
    audit_logs: Mapped[List["AuditLog"]] = relationship("AuditLog", back_populates="user")

class Learner(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "learners"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    headline: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    target_role: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    years_of_experience: Mapped[float] = mapped_column(Float, default=0.0)
    education_level: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    github_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    linkedin_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="learner_profile")
    resumes: Mapped[List["Resume"]] = relationship("Resume", back_populates="learner", cascade="all, delete-orphan")
    skills: Mapped[List["LearnerSkill"]] = relationship("LearnerSkill", back_populates="learner", cascade="all, delete-orphan")
    course_completions: Mapped[List["CourseCompletion"]] = relationship("CourseCompletion", back_populates="learner", cascade="all, delete-orphan")
    assessment_results: Mapped[List["AssessmentResult"]] = relationship("AssessmentResult", back_populates="learner", cascade="all, delete-orphan")
    projects: Mapped[List["PracticalProject"]] = relationship("PracticalProject", back_populates="learner", cascade="all, delete-orphan")
    skill_matches: Mapped[List["SkillMatch"]] = relationship("SkillMatch", back_populates="learner", cascade="all, delete-orphan")
    skill_gaps: Mapped[List["SkillGap"]] = relationship("SkillGap", back_populates="learner", cascade="all, delete-orphan")
    recommendations: Mapped[List["Recommendation"]] = relationship("Recommendation", back_populates="learner", cascade="all, delete-orphan")
    career_reports: Mapped[List["CareerReport"]] = relationship("CareerReport", back_populates="learner", cascade="all, delete-orphan")

class AuditLog(Base, UUIDMixin):
    __tablename__ = "audit_logs"

    user_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_name: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    details: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[str] = mapped_column(String(50), nullable=False)

    user: Mapped[Optional["User"]] = relationship("User", back_populates="audit_logs")
