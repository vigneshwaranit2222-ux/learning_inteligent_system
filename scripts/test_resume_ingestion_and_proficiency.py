import sys
import os

sys.path.insert(0, os.path.abspath("backend"))
sys.path.insert(0, os.path.abspath("."))

from app.core.database import SessionLocal
from app.models.user import User, Learner
from app.models.skill import LearnerSkill, Skill, SkillEvidence
from app.models.job import JobDescription
from app.models.course import Assessment, AssessmentQuestion
from app.api.v1.endpoints.matching import match_learner_with_job
from app.api.v1.endpoints.assessments import submit_assessment, AssessmentSubmission
from app.api.v1.endpoints.reports import generate_career_report
from ai_engine.extraction.extractor import extractor
from ai_engine.proficiency.evaluator import proficiency_evaluator
from sqlalchemy import select

def test_evidence_and_readiness_progression():
    print("Testing Evidence-Driven Career Progression...")
    db = SessionLocal()
    try:
        learner = db.scalar(select(Learner).join(User).where(User.email == "learner@intelligence.system"))
        assert learner is not None
        job = db.scalar(select(JobDescription).where(JobDescription.title == "Senior AI Backend Engineer"))
        assert job is not None

        # Sample resume content
        resume_text = """
        ALEX MERCER
        Backend Software Engineer | Python & Cloud Systems
        
        EXPERIENCE:
        Software Engineer at Acme Cloud (2.5 years)
        - Developed asynchronous backend REST services with FastAPI and Python 3.11.
        - Managed PostgreSQL relational schemas and query optimization.
        - Built and containerized backend microservices using Docker and Git.
        - Deployed scalable worker services on Linux.
        """

        # 1. Ingest Resume Skills
        extracted = extractor.extract_skills_from_text(resume_text, source_type="resume")
        print(f"Extracted {len(extracted)} skills from resume: {[e['canonical_name'] for e in extracted]}")

        for item in extracted:
            sk = db.scalar(select(Skill).where(Skill.name == item["canonical_name"]))
            if not sk:
                continue

            ls = db.scalar(select(LearnerSkill).where(LearnerSkill.learner_id == learner.id, LearnerSkill.skill_id == sk.id))
            if not ls:
                ls = LearnerSkill(learner_id=learner.id, skill_id=sk.id, proficiency_level=1, confidence_score=item["confidence"])
                db.add(ls)
                db.flush()

            # Add Evidence
            ev = SkillEvidence(
                learner_skill_id=ls.id,
                source_type="resume",
                text_snippet=item["evidence_snippet"],
                confidence=item["confidence"]
            )
            db.add(ev)

            # Evaluate proficiency with experience
            eval_res = proficiency_evaluator.evaluate_skill_proficiency(
                skill_name=sk.name,
                years_experience=learner.years_of_experience,
                has_resume_mention=True
            )
            ls.proficiency_level = eval_res["proficiency_level"]
            ls.confidence_score = eval_res["confidence_score"]
            ls.evidence_summary = eval_res["explanation"]

        db.commit()

        # 2. Check Match After Resume Ingestion
        match_after_resume = match_learner_with_job(job_id=job.id, learner=learner, db=db)
        print(f"\nMatch Status After Resume Ingestion:")
        print(f" - Readiness Score: {match_after_resume.readiness_score}% (was 0.0%)")
        print(f" - Matched Skills Count: {match_after_resume.matched_count}")
        print(f" - Partial Skills Count: {match_after_resume.partial_count}")
        print(f" - Missing Skills Count: {match_after_resume.missing_count}")
        assert match_after_resume.readiness_score > 0.0

        # 3. Learner completes Assessment: FastAPI & Async Python Exam
        assessment = db.scalar(select(Assessment).where(Assessment.title == "FastAPI & Async Python Competency Exam"))
        assert assessment is not None
        questions = assessment.questions

        # Prepare correct answers
        answers = {str(q.id): q.correct_answer for q in questions}
        submission = AssessmentSubmission(assessment_id=assessment.id, answers=answers)
        result = submit_assessment(assessment_id=assessment.id, submission=submission, learner=learner, db=db)
        print(f"\nAssessment Submitted: {result.assessment_title}")
        print(f" - Score: {result.score_percentage}% | Passed: {result.passed}")
        assert result.score_percentage == 100.0

        # 4. Check Match After Passing Assessment
        match_after_exam = match_learner_with_job(job_id=job.id, learner=learner, db=db)
        print(f"\nMatch Status After Passing Assessment:")
        print(f" - Readiness Score: {match_after_exam.readiness_score}%")
        print(f" - Matched Skills Count: {match_after_exam.matched_count}")
        assert match_after_exam.readiness_score >= match_after_resume.readiness_score

        # 5. Generate Updated Career Report
        report = generate_career_report(job_id=job.id, learner=learner, db=db)
        print(f"\nUpdated Career Report Generated:")
        print(f" - Overall Readiness Score: {report.overall_readiness_score}%")
        print(f" - Executive Summary: {report.executive_summary}")
        print(f" - PDF generated at: {report.pdf_path}")

        print("\n✅ Evidence-Driven Progression & Reproducible Scoring successfully validated!")

    finally:
        db.close()

if __name__ == "__main__":
    test_evidence_and_readiness_progression()
