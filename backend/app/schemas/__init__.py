from app.schemas.auth import (
    Token, TokenPayload, LoginRequest, RegisterRequest,
    RefreshTokenRequest, ForgotPasswordRequest, ResetPasswordRequest
)
from app.schemas.user import (
    UserBase, UserCreate, UserUpdate, UserResponse,
    LearnerProfileBase, LearnerProfileCreate, LearnerProfileUpdate, LearnerResponse
)
from app.schemas.skill import (
    SkillCategorySchema, SkillCategoryCreate, SkillAliasSchema,
    SkillSchema, SkillCreate, SkillEvidenceResponse, LearnerSkillResponse,
    ExtractedSkillItem, SkillExtractionResult
)
from app.schemas.course import (
    CourseModuleSchema, LearningOutcomeSchema, CourseSchema, CourseCreate,
    CourseCompletionCreate, CourseCompletionResponse,
    AssessmentQuestionSchema, AssessmentSchema, AssessmentSubmission, AssessmentResultResponse,
    PracticalProjectCreate, PracticalProjectResponse
)
from app.schemas.job import (
    JobRoleSchema, JobRequirementSchema, JobDescriptionSchema, JobCreateRequest,
    SkillMatchItem, SkillGapItem, MatchingResultResponse
)
from app.schemas.recommendation import (
    LearningResourceSchema, RecommendationEvidenceSchema, RecommendationResponse,
    CareerReportResponse, DashboardStatsResponse
)
from app.schemas.admin import (
    SystemAnalyticsResponse, ProcessingJobResponse, AuditLogResponse
)
