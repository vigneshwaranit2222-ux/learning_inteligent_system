from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth, learners, resumes, courses,
    assessments, skills, jobs, matching,
    recommendations, reports, admin
)

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(learners.router)
api_router.include_router(resumes.router)
api_router.include_router(courses.router)
api_router.include_router(assessments.router)
api_router.include_router(skills.router)
api_router.include_router(jobs.router)
api_router.include_router(matching.router)
api_router.include_router(recommendations.router)
api_router.include_router(reports.router)
api_router.include_router(admin.router)
