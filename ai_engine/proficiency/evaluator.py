from typing import Dict, List, Any, Optional

class ProficiencyEvaluator:
    """
    Deterministic Multi-Evidence Learner Proficiency Engine.
    Evaluates verified evidence from 4 distinct sources:
    - Work Experience (Weight: 0.40)
    - Practical Projects (Weight: 0.30)
    - Assessments (Weight: 0.20)
    - Course Completions (Weight: 0.10)
    """

    @staticmethod
    def calculate_experience_score(years: float) -> float:
        if years >= 4.0:
            return 4.0
        elif years >= 2.0:
            return 3.0
        elif years >= 1.0:
            return 2.0
        elif years > 0.0:
            return 1.0
        return 0.0

    @staticmethod
    def calculate_project_score(projects: List[Dict[str, Any]]) -> float:
        if not projects:
            return 0.0
        max_level = 0.0
        for p in projects:
            complexity = float(p.get("complexity_level", 1))
            is_verified = bool(p.get("verified", False))
            has_repo = bool(p.get("repository_url"))
            score = complexity
            if is_verified:
                score = min(4.0, score + 0.5)
            elif not has_repo:
                score = max(1.0, score - 0.5)
            max_level = max(max_level, score)
        return min(4.0, max_level)

    @staticmethod
    def calculate_assessment_score(assessments: List[Dict[str, Any]]) -> float:
        if not assessments:
            return 0.0
        # Average top scores for the skill
        scores = [float(a.get("score_percentage", 0.0)) for a in assessments]
        max_score = max(scores) if scores else 0.0
        if max_score >= 90.0:
            return 4.0
        elif max_score >= 75.0:
            return 3.0
        elif max_score >= 60.0:
            return 2.0
        elif max_score >= 40.0:
            return 1.0
        return 0.5

    @staticmethod
    def calculate_course_score(completions: List[Dict[str, Any]]) -> float:
        if not completions:
            return 0.0
        count = len(completions)
        if count >= 3:
            return 3.5
        elif count >= 2:
            return 2.5
        return 2.0

    def evaluate_skill_proficiency(
        self,
        skill_name: str,
        years_experience: float = 0.0,
        projects: Optional[List[Dict[str, Any]]] = None,
        assessments: Optional[List[Dict[str, Any]]] = None,
        course_completions: Optional[List[Dict[str, Any]]] = None,
        has_resume_mention: bool = True
    ) -> Dict[str, Any]:
        projects = projects or []
        assessments = assessments or []
        course_completions = course_completions or []

        e_exp = self.calculate_experience_score(years_experience)
        e_proj = self.calculate_project_score(projects)
        e_ass = self.calculate_assessment_score(assessments)
        e_course = self.calculate_course_score(course_completions)

        w_exp, w_proj, w_ass, w_course = 0.40, 0.30, 0.20, 0.10

        # Weighted aggregate
        raw_score = (
            w_exp * e_exp +
            w_proj * e_proj +
            w_ass * e_ass +
            w_course * e_course
        )

        # Baseline: If mentioned in resume but no other evidence yet, give baseline 1.5
        if has_resume_mention and raw_score < 1.0:
            raw_score = 1.2

        # GUARDRAIL: Unverified resume claims or experience alone CANNOT establish Advanced (3) or Expert (4)
        guardrail_applied = False
        if e_proj == 0.0 and e_ass == 0.0:
            if years_experience >= 4.0 or raw_score > 2.0:
                guardrail_applied = True
            raw_score = min(raw_score, 2.0)

        # Determine discrete integer level (1: Beginner, 2: Intermediate, 3: Advanced, 4: Expert)
        level = max(1, min(4, round(raw_score)))

        # Confidence calculation based on evidence diversity
        evidence_sources_count = sum([
            1 if years_experience > 0 else 0,
            1 if len(projects) > 0 else 0,
            1 if len(assessments) > 0 else 0,
            1 if len(course_completions) > 0 else 0
        ])
        confidence = min(1.0, 0.4 + (0.15 * evidence_sources_count))

        # Human-readable evidence explanation
        level_labels = {1: "Beginner", 2: "Intermediate", 3: "Advanced", 4: "Expert"}
        explanation_parts = [
            f"Evaluated as {level_labels[level]} (Level {level}) based on:"
        ]
        if years_experience > 0:
            explanation_parts.append(f"{years_experience:.1f} yrs demonstrated experience (component score: {e_exp:.1f})")
        if projects:
            explanation_parts.append(f"{len(projects)} practical project(s) (component score: {e_proj:.1f})")
        if assessments:
            explanation_parts.append(f"{len(assessments)} assessment submission(s) (component score: {e_ass:.1f})")
        if course_completions:
            explanation_parts.append(f"{len(course_completions)} course completion(s) (component score: {e_course:.1f})")
        if guardrail_applied:
            explanation_parts.append("Note: Score capped at Intermediate pending hands-on project or assessment verification.")

        explanation = "; ".join(explanation_parts)

        return {
            "skill_name": skill_name,
            "proficiency_level": level,
            "proficiency_label": level_labels[level],
            "raw_score": round(raw_score, 2),
            "confidence_score": round(confidence, 2),
            "explanation": explanation,
            "components": {
                "experience_component": e_exp,
                "project_component": e_proj,
                "assessment_component": e_ass,
                "course_component": e_course
            },
            "guardrail_applied": guardrail_applied
        }

proficiency_evaluator = ProficiencyEvaluator()
