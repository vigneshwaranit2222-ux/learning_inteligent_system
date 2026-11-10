from typing import List, Dict, Any
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.core.database import get_db
from app.models.course import Assessment, AssessmentQuestion, AssessmentResult
from app.models.skill import Skill, LearnerSkill, SkillEvidence
from app.models.user import Learner
from app.schemas.course import AssessmentSchema, AssessmentSubmission, AssessmentResultResponse
from app.api.deps import get_current_learner, create_audit_log
from ai_engine.proficiency.evaluator import proficiency_evaluator

router = APIRouter(prefix="/assessments", tags=["Assessments"])

@router.get("/", response_model=List[AssessmentSchema])
def list_assessments(db: Session = Depends(get_db)):
    assessments = db.scalars(select(Assessment)).all()
    return assessments

@router.get("/{assessment_id}", response_model=AssessmentSchema)
def get_assessment(assessment_id: str, db: Session = Depends(get_db)):
    assessment = db.scalar(select(Assessment).where(Assessment.id == assessment_id))
    if not assessment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found")
    return assessment

@router.post("/{assessment_id}/submit", response_model=AssessmentResultResponse)
def submit_assessment(
    assessment_id: str,
    submission: AssessmentSubmission,
    learner: Learner = Depends(get_current_learner),
    db: Session = Depends(get_db)
):
    assessment = db.scalar(select(Assessment).where(Assessment.id == assessment_id))
    if not assessment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found")

    questions = assessment.questions
    if not questions:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Assessment has no questions configured")

    correct_count = 0
    total_questions = len(questions)

    for q in questions:
        submitted_ans = submission.answers.get(str(q.id)) or submission.answers.get(q.question_text)
        if submitted_ans and submitted_ans.strip().lower() == q.correct_answer.strip().lower():
            correct_count += 1

    score_percentage = round((correct_count / total_questions) * 100.0, 1)
    passed = score_percentage >= assessment.passing_score

    now_iso = datetime.now(timezone.utc).isoformat()
    result = AssessmentResult(
        learner_id=learner.id,
        assessment_id=assessment.id,
        score_percentage=score_percentage,
        passed=passed,
        answers=submission.answers,
        taken_at=now_iso
    )
    db.add(result)
    db.flush()

    # If linked to a skill, update learner proficiency
    if assessment.skill_id:
        skill = db.scalar(select(Skill).where(Skill.id == assessment.skill_id))
        if skill:
            learner_skill = db.scalar(
                select(LearnerSkill).where(
                    LearnerSkill.learner_id == learner.id,
                    LearnerSkill.skill_id == skill.id
                )
            )
            if not learner_skill:
                learner_skill = LearnerSkill(
                    learner_id=learner.id,
                    skill_id=skill.id,
                    proficiency_level=1,
                    confidence_score=0.85
                )
                db.add(learner_skill)
                db.flush()

            evidence = SkillEvidence(
                learner_skill_id=learner_skill.id,
                source_type="assessment",
                source_id=assessment.id,
                text_snippet=f"Scored {score_percentage}% on assessment: {assessment.title} (Status: {'Passed' if passed else 'Failed'}).",
                confidence=0.9
            )
            db.add(evidence)

            # Re-evaluate proficiency
            eval_res = proficiency_evaluator.evaluate_skill_proficiency(
                skill_name=skill.name,
                years_experience=learner.years_of_experience,
                assessments=[{"score_percentage": score_percentage, "passed": passed}]
            )
            learner_skill.proficiency_level = max(learner_skill.proficiency_level, eval_res["proficiency_level"])
            learner_skill.confidence_score = eval_res["confidence_score"]
            learner_skill.evidence_summary = eval_res["explanation"]

    db.commit()
    db.refresh(result)
    create_audit_log(
        db, learner.user_id, "ASSESSMENT_SUBMITTED", "assessments", assessment.id,
        details={"score": score_percentage, "passed": passed}
    )

    return AssessmentResultResponse(
        id=result.id,
        assessment_id=assessment.id,
        assessment_title=assessment.title,
        score_percentage=score_percentage,
        passed=passed,
        total_questions=total_questions,
        correct_count=correct_count,
        taken_at=now_iso
    )

@router.get("/my/history", response_model=List[AssessmentResultResponse])
def get_assessment_history(
    learner: Learner = Depends(get_current_learner),
    db: Session = Depends(get_db)
):
    results = db.scalars(
        select(AssessmentResult)
        .where(AssessmentResult.learner_id == learner.id)
        .order_by(AssessmentResult.created_at.desc())
    ).all()

    return [
        AssessmentResultResponse(
            id=r.id,
            assessment_id=r.assessment_id,
            assessment_title=r.assessment.title if r.assessment else "Assessment",
            score_percentage=r.score_percentage,
            passed=r.passed,
            total_questions=len(r.assessment.questions) if r.assessment else 1,
            correct_count=int(round((r.score_percentage / 100.0) * (len(r.assessment.questions) if r.assessment else 1))),
            taken_at=r.taken_at
        )
        for r in results
    ]
