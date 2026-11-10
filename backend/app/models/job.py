from typing import Optional, List
from sqlalchemy import String, Integer, Float, Boolean, ForeignKey, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import UUIDMixin, TimestampMixin

class JobRole(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "job_roles"

    title: Mapped[str] = mapped_column(String(150), unique=True, index=True, nullable=False)
    industry: Mapped[str] = mapped_column(String(100), default="Information Technology")
    standard_code: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    job_descriptions: Mapped[List["JobDescription"]] = relationship("JobDescription", back_populates="role")

class JobDescription(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "job_descriptions"

    role_id: Mapped[str] = mapped_column(String(36), ForeignKey("job_roles.id", ondelete="RESTRICT"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    company_name: Mapped[str] = mapped_column(String(150), nullable=False)
    location: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    employment_type: Mapped[str] = mapped_column(String(50), default="Full-time")
    experience_required: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    file_hash: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    source_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    role: Mapped["JobRole"] = relationship("JobRole", back_populates="job_descriptions")
    requirements: Mapped[List["JobRequirement"]] = relationship("JobRequirement", back_populates="job", cascade="all, delete-orphan")
    matches: Mapped[List["SkillMatch"]] = relationship("SkillMatch", back_populates="job", cascade="all, delete-orphan")
    gaps: Mapped[List["SkillGap"]] = relationship("SkillGap", back_populates="job", cascade="all, delete-orphan")
    career_reports: Mapped[List["CareerReport"]] = relationship("CareerReport", back_populates="job", cascade="all, delete-orphan")

class JobRequirement(Base, UUIDMixin):
    __tablename__ = "job_requirements"

    job_id: Mapped[str] = mapped_column(String(36), ForeignKey("job_descriptions.id", ondelete="CASCADE"), nullable=False)
    skill_id: Mapped[str] = mapped_column(String(36), ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)
    required_level: Mapped[int] = mapped_column(Integer, default=2) # 1-4
    requirement_type: Mapped[str] = mapped_column(String(50), default="mandatory") # mandatory, preferred, optional
    importance_weight: Mapped[float] = mapped_column(Float, default=1.0)

    job: Mapped["JobDescription"] = relationship("JobDescription", back_populates="requirements")
    skill: Mapped["Skill"] = relationship("Skill", back_populates="job_requirements")

class SkillMatch(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "skill_matches"

    learner_id: Mapped[str] = mapped_column(String(36), ForeignKey("learners.id", ondelete="CASCADE"), nullable=False)
    job_id: Mapped[str] = mapped_column(String(36), ForeignKey("job_descriptions.id", ondelete="CASCADE"), nullable=False)
    skill_id: Mapped[str] = mapped_column(String(36), ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)
    match_type: Mapped[str] = mapped_column(String(50), nullable=False) # matched, partial, missing, insufficient, exceeds
    learner_level: Mapped[int] = mapped_column(Integer, default=0)
    required_level: Mapped[int] = mapped_column(Integer, default=1)
    score_delta: Mapped[float] = mapped_column(Float, default=0.0)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)

    learner: Mapped["Learner"] = relationship("Learner", back_populates="skill_matches")
    job: Mapped["JobDescription"] = relationship("JobDescription", back_populates="matches")
    skill: Mapped["Skill"] = relationship("Skill")

class SkillGap(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "skill_gaps"

    learner_id: Mapped[str] = mapped_column(String(36), ForeignKey("learners.id", ondelete="CASCADE"), nullable=False)
    job_id: Mapped[str] = mapped_column(String(36), ForeignKey("job_descriptions.id", ondelete="CASCADE"), nullable=False)
    skill_id: Mapped[str] = mapped_column(String(36), ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)
    required_level: Mapped[int] = mapped_column(Integer, nullable=False)
    current_level: Mapped[int] = mapped_column(Integer, default=0)
    gap_severity: Mapped[str] = mapped_column(String(50), default="moderate") # critical, moderate, minor

    learner: Mapped["Learner"] = relationship("Learner", back_populates="skill_gaps")
    job: Mapped["JobDescription"] = relationship("JobDescription", back_populates="gaps")
    skill: Mapped["Skill"] = relationship("Skill")
