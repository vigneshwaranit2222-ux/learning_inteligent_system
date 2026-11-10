from app.core.database import Base
from app.models.base import UUIDMixin, TimestampMixin
from app.models.user import User, Learner, AuditLog
from app.models.skill import SkillCategory, Skill, SkillAlias, LearnerSkill, SkillEvidence
from app.models.course import (
    Resume, Course, CourseModule, LearningOutcome,
    CourseCompletion, Assessment, AssessmentQuestion,
    AssessmentResult, PracticalProject
)
from app.models.job import JobRole, JobDescription, JobRequirement, SkillMatch, SkillGap
from app.models.recommendation import (
    LearningResource, Recommendation, RecommendationEvidence,
    CareerReport, ProcessingJob
)

__all__ = [
    "Base",
    "UUIDMixin",
    "TimestampMixin",
    "User",
    "Learner",
    "AuditLog",
    "SkillCategory",
    "Skill",
    "SkillAlias",
    "LearnerSkill",
    "SkillEvidence",
    "Resume",
    "Course",
    "CourseModule",
    "LearningOutcome",
    "CourseCompletion",
    "Assessment",
    "AssessmentQuestion",
    "AssessmentResult",
    "PracticalProject",
    "JobRole",
    "JobDescription",
    "JobRequirement",
    "SkillMatch",
    "SkillGap",
    "LearningResource",
    "Recommendation",
    "RecommendationEvidence",
    "CareerReport",
    "ProcessingJob"
]
