from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, HttpUrl

class CourseModuleSchema(BaseModel):
    id: str
    title: str
    order_index: int
    description: Optional[str] = None

    class Config:
        from_attributes = True

class LearningOutcomeSchema(BaseModel):
    id: str
    skill_id: str
    target_proficiency: int
    outcome_statement: str

    class Config:
        from_attributes = True

class CourseSchema(BaseModel):
    id: str
    title: str
    provider: str
    code: Optional[str] = None
    description: Optional[str] = None
    difficulty: str
    estimated_hours: int
    url: Optional[str] = None
    modules: List[CourseModuleSchema] = []
    learning_outcomes: List[LearningOutcomeSchema] = []

    class Config:
        from_attributes = True

class CourseCreate(BaseModel):
    title: str
    provider: str
    code: Optional[str] = None
    description: Optional[str] = None
    difficulty: str = "intermediate"
    estimated_hours: int = 10
    url: Optional[str] = None
    outcomes: List[Dict[str, Any]] = [] # list of {skill_id: str, target_proficiency: int, outcome_statement: str}

class CourseCompletionCreate(BaseModel):
    course_id: str
    completion_date: str
    certificate_url: Optional[str] = None
    grade: Optional[str] = None

class CourseCompletionResponse(BaseModel):
    id: str
    learner_id: str
    course_id: str
    course: CourseSchema
    completion_date: str
    certificate_url: Optional[str] = None
    grade: Optional[str] = None
    verified_by: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class AssessmentQuestionSchema(BaseModel):
    id: str
    question_text: str
    question_type: str
    options: List[str]
    explanation: Optional[str] = None

    class Config:
        from_attributes = True

class AssessmentSchema(BaseModel):
    id: str
    course_id: Optional[str] = None
    skill_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    passing_score: float
    time_limit_minutes: int
    questions: List[AssessmentQuestionSchema] = []

    class Config:
        from_attributes = True

class AssessmentSubmission(BaseModel):
    assessment_id: str
    answers: Dict[str, str] # question_id -> selected_option

class AssessmentResultResponse(BaseModel):
    id: str
    assessment_id: str
    assessment_title: str
    score_percentage: float
    passed: bool
    total_questions: int
    correct_count: int
    taken_at: str

class PracticalProjectCreate(BaseModel):
    title: str
    description: str
    repository_url: Optional[str] = None
    live_url: Optional[str] = None
    demonstrated_skills: List[str] = []
    complexity_level: int = 2

class PracticalProjectResponse(BaseModel):
    id: str
    learner_id: str
    title: str
    description: str
    repository_url: Optional[str] = None
    live_url: Optional[str] = None
    demonstrated_skills: Optional[List[str]] = None
    complexity_level: int
    verified: bool
    review_notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
