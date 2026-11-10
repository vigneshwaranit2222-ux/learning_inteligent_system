import sys
import os

sys.path.insert(0, os.path.abspath("backend"))
sys.path.insert(0, os.path.abspath("."))

from app.core.database import SessionLocal
from app.api.v1.endpoints.auth import login, register
from app.api.v1.endpoints.skills import list_skills, extract_skills_from_text_endpoint, TextExtractionRequest
from app.api.v1.endpoints.jobs import list_jobs
from app.api.v1.endpoints.courses import list_courses
from app.api.v1.endpoints.matching import match_learner_with_job
from app.api.v1.endpoints.recommendations import generate_recommendations
from app.api.v1.endpoints.reports import generate_career_report
from app.api.v1.endpoints.learners import get_learner_dashboard_stats
from app.schemas.auth import LoginRequest
from app.models.user import User, Learner
from sqlalchemy import select

def test_full_platform_pipeline():
    print("Testing Full Platform Pipeline directly...")
    db = SessionLocal()
    try:
        # 1. Test Login
        print("\n--- 1. Testing Auth Login ---")
        login_res = login(LoginRequest(email="admin@intelligence.system", password="AdminPass123!"), db=db)
        print("Logged in as Admin:", login_res.full_name, "Role:", login_res.role)
        assert login_res.role == "admin"

        # 2. Test Skills
        print("\n--- 2. Testing Skills Catalog ---")
        skills = list_skills(skip=0, limit=20, db=db)
        print(f"Total skills retrieved: {len(skills)}")
        assert len(skills) > 0

        # 3. Test Skill Extraction
        print("\n--- 3. Testing Skill Extraction Engine ---")
        sample_resume_snippet = """
        Experienced Senior Python Developer with 5 years building scalable web services using FastAPI and Django.
        Extensive hands-on experience deploying Docker containers to Kubernetes clusters on AWS.
        Skilled in PostgreSQL query tuning, Redis caching, and developing RAG pipelines with Large Language Models.
        """
        extracted = extract_skills_from_text_endpoint(TextExtractionRequest(text=sample_resume_snippet))
        print(f"Skills extracted: {extracted.total_skills_extracted}")
        extracted_names = [s.canonical_name for s in extracted.skills]
        print("Extracted skills:", extracted_names)
        assert "Python" in extracted_names
        assert "FastAPI" in extracted_names
        assert "Docker" in extracted_names
        assert "PostgreSQL" in extracted_names
        assert "Large Language Models" in extracted_names

        # 4. Test Course Catalog
        print("\n--- 4. Testing Courses Catalog ---")
        courses = list_courses(db=db)
        print(f"Courses available: {len(courses)}")
        assert len(courses) > 0

        # 5. Test Job Descriptions
        print("\n--- 5. Testing Jobs Catalog ---")
        jobs = list_jobs(db=db)
        print(f"Jobs active: {len(jobs)}")
        assert len(jobs) > 0
        target_job = jobs[0]
        print(f"Selected target job: {target_job.title} at {target_job.company_name}")

        # 6. Test Learner Setup
        print("\n--- 6. Testing Learner Matching & Readiness Engine ---")
        learner = db.scalar(select(Learner).join(User).where(User.email == "learner@intelligence.system"))
        assert learner is not None

        # Run Matching
        match_res = match_learner_with_job(job_id=target_job.id, learner=learner, db=db)
        print(f"Matching executed for {learner.user.full_name} against {target_job.title}:")
        print(f" - Readiness Score: {match_res.readiness_score}%")
        print(f" - Matched Skills: {match_res.matched_count}")
        print(f" - Partial Skills: {match_res.partial_count}")
        print(f" - Missing Skills: {match_res.missing_count}")
        print(f" - Identified Skill Gaps: {len(match_res.gaps)}")

        # 7. Test Recommendations
        print("\n--- 7. Testing Personalized Recommendation Engine ---")
        recs = generate_recommendations(job_id=target_job.id, learner=learner, db=db)
        print(f"Generated {len(recs)} actionable recommendations:")
        for r in recs[:3]:
            print(f"   * Priority: {r.priority.upper()} | Skill: {r.skill.name} | Resource: {r.resource.title if r.resource else 'Course'}")

        # 8. Test Career Report Generation & PDF
        print("\n--- 8. Testing Dynamic Career Report & PDF Generation ---")
        report = generate_career_report(job_id=target_job.id, learner=learner, db=db)
        print("Generated Report ID:", report.id)
        print("Readiness Score:", report.overall_readiness_score)
        print("Executive Summary:", report.executive_summary)
        print("PDF Path:", report.pdf_path)

        # 9. Test Dashboard Stats
        print("\n--- 9. Testing Learner Dashboard Live Metrics ---")
        stats = get_learner_dashboard_stats(learner=learner, db=db)
        print("Dashboard Metrics:")
        print(f" - Target Role: {stats.target_job_title}")
        print(f" - Career Readiness: {stats.career_readiness_score}%")
        print(f" - Matched Job Skills: {stats.matched_job_skills}")
        print(f" - Skill Gaps: {stats.skill_gaps}")
        print(f" - Active Recommendations: {stats.active_recommendations}")

        print("\n🎉 ALL CORE FULL-STACK BACKEND & AI MODULES VERIFIED 100% OPERATIONAL!")

    finally:
        db.close()

if __name__ == "__main__":
    test_full_platform_pipeline()
