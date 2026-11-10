from typing import Optional, List
from sqlalchemy import String, Integer, Float, Boolean, ForeignKey, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import UUIDMixin, TimestampMixin

class SkillCategory(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "skill_categories"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    skills: Mapped[List["Skill"]] = relationship("Skill", back_populates="category")

class Skill(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "skills"

    category_id: Mapped[str] = mapped_column(String(36), ForeignKey("skill_categories.id", ondelete="RESTRICT"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    popularity_score: Mapped[float] = mapped_column(Float, default=1.0)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=True)

    category: Mapped["SkillCategory"] = relationship("SkillCategory", back_populates="skills")
    aliases: Mapped[List["SkillAlias"]] = relationship("SkillAlias", back_populates="skill", cascade="all, delete-orphan")
    learner_skills: Mapped[List["LearnerSkill"]] = relationship("LearnerSkill", back_populates="skill")
    job_requirements: Mapped[List["JobRequirement"]] = relationship("JobRequirement", back_populates="skill")
    learning_outcomes: Mapped[List["LearningOutcome"]] = relationship("LearningOutcome", back_populates="skill")
    learning_resources: Mapped[List["LearningResource"]] = relationship("LearningResource", back_populates="skill")

class SkillAlias(Base, UUIDMixin):
    __tablename__ = "skill_aliases"

    skill_id: Mapped[str] = mapped_column(String(36), ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)
    alias: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    normalized_alias: Mapped[str] = mapped_column(String(100), index=True, nullable=False)

    skill: Mapped["Skill"] = relationship("Skill", back_populates="aliases")

class LearnerSkill(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "learner_skills"

    learner_id: Mapped[str] = mapped_column(String(36), ForeignKey("learners.id", ondelete="CASCADE"), nullable=False)
    skill_id: Mapped[str] = mapped_column(String(36), ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)
    proficiency_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False) # 1: Beginner, 2: Intermediate, 3: Advanced, 4: Expert
    confidence_score: Mapped[float] = mapped_column(Float, default=0.5, nullable=False) # 0.0 - 1.0
    years_experience: Mapped[float] = mapped_column(Float, default=0.0)
    last_used_date: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    evidence_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    learner: Mapped["Learner"] = relationship("Learner", back_populates="skills")
    skill: Mapped["Skill"] = relationship("Skill", back_populates="learner_skills")
    evidence_list: Mapped[List["SkillEvidence"]] = relationship("SkillEvidence", back_populates="learner_skill", cascade="all, delete-orphan")

class SkillEvidence(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "skill_evidence"

    learner_skill_id: Mapped[str] = mapped_column(String(36), ForeignKey("learner_skills.id", ondelete="CASCADE"), nullable=False)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False) # resume, course, assessment, project
    source_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    text_snippet: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    source_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    learner_skill: Mapped["LearnerSkill"] = relationship("LearnerSkill", back_populates="evidence_list")
