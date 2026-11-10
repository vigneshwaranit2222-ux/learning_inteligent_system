from typing import Optional, List
from sqlalchemy import String, Integer, Float, Boolean, ForeignKey, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import UUIDMixin, TimestampMixin

class Resume(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "resumes"

    learner_id: Mapped[str] = mapped_column(String(36), ForeignKey("learners.id", ondelete="CASCADE"), nullable=False)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_hash: Mapped[str] = mapped_column(String(64), index=True, nullable=False) # SHA-256
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    parsed_sections: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    processing_status: Mapped[str] = mapped_column(String(50), default="pending") # pending, processed, failed
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    learner: Mapped["Learner"] = relationship("Learner", back_populates="resumes")

class Course(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "courses"

    title: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    provider: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    difficulty: Mapped[str] = mapped_column(String(50), default="intermediate") # beginner, intermediate, advanced
    estimated_hours: Mapped[int] = mapped_column(Integer, default=10)
    url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    modules: Mapped[List["CourseModule"]] = relationship("CourseModule", back_populates="course", cascade="all, delete-orphan")
    learning_outcomes: Mapped[List["LearningOutcome"]] = relationship("LearningOutcome", back_populates="course", cascade="all, delete-orphan")
    completions: Mapped[List["CourseCompletion"]] = relationship("CourseCompletion", back_populates="course", cascade="all, delete-orphan")
    assessments: Mapped[List["Assessment"]] = relationship("Assessment", back_populates="course")

class CourseModule(Base, UUIDMixin):
    __tablename__ = "course_modules"

    course_id: Mapped[str] = mapped_column(String(36), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, default=1)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    course: Mapped["Course"] = relationship("Course", back_populates="modules")

class LearningOutcome(Base, UUIDMixin):
    __tablename__ = "learning_outcomes"

    course_id: Mapped[str] = mapped_column(String(36), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    skill_id: Mapped[str] = mapped_column(String(36), ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)
    target_proficiency: Mapped[int] = mapped_column(Integer, default=2) # 1-4
    outcome_statement: Mapped[str] = mapped_column(Text, nullable=False)

    course: Mapped["Course"] = relationship("Course", back_populates="learning_outcomes")
    skill: Mapped["Skill"] = relationship("Skill", back_populates="learning_outcomes")

class CourseCompletion(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "course_completions"

    learner_id: Mapped[str] = mapped_column(String(36), ForeignKey("learners.id", ondelete="CASCADE"), nullable=False)
    course_id: Mapped[str] = mapped_column(String(36), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    completion_date: Mapped[str] = mapped_column(String(50), nullable=False)
    certificate_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    grade: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    verified_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    learner: Mapped["Learner"] = relationship("Learner", back_populates="course_completions")
    course: Mapped["Course"] = relationship("Course", back_populates="completions")

class Assessment(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "assessments"

    course_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("courses.id", ondelete="SET NULL"), nullable=True)
    skill_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("skills.id", ondelete="SET NULL"), nullable=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    passing_score: Mapped[float] = mapped_column(Float, default=70.0)
    time_limit_minutes: Mapped[int] = mapped_column(Integer, default=30)

    course: Mapped[Optional["Course"]] = relationship("Course", back_populates="assessments")
    questions: Mapped[List["AssessmentQuestion"]] = relationship("AssessmentQuestion", back_populates="assessment", cascade="all, delete-orphan")
    results: Mapped[List["AssessmentResult"]] = relationship("AssessmentResult", back_populates="assessment", cascade="all, delete-orphan")

class AssessmentQuestion(Base, UUIDMixin):
    __tablename__ = "assessment_questions"

    assessment_id: Mapped[str] = mapped_column(String(36), ForeignKey("assessments.id", ondelete="CASCADE"), nullable=False)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    question_type: Mapped[str] = mapped_column(String(50), default="mcq") # mcq, code
    options: Mapped[List[str]] = mapped_column(JSON, nullable=False) # list of string options
    correct_answer: Mapped[str] = mapped_column(Text, nullable=False)
    explanation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    assessment: Mapped["Assessment"] = relationship("Assessment", back_populates="questions")

class AssessmentResult(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "assessment_results"

    learner_id: Mapped[str] = mapped_column(String(36), ForeignKey("learners.id", ondelete="CASCADE"), nullable=False)
    assessment_id: Mapped[str] = mapped_column(String(36), ForeignKey("assessments.id", ondelete="CASCADE"), nullable=False)
    score_percentage: Mapped[float] = mapped_column(Float, nullable=False)
    passed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    answers: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    taken_at: Mapped[str] = mapped_column(String(50), nullable=False)

    learner: Mapped["Learner"] = relationship("Learner", back_populates="assessment_results")
    assessment: Mapped["Assessment"] = relationship("Assessment", back_populates="results")

class PracticalProject(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "practical_projects"

    learner_id: Mapped[str] = mapped_column(String(36), ForeignKey("learners.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    repository_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    live_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    demonstrated_skills: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    complexity_level: Mapped[int] = mapped_column(Integer, default=2) # 1-4
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    review_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    learner: Mapped["Learner"] = relationship("Learner", back_populates="projects")
