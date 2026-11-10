from typing import Dict, List, Any, Optional

class SkillMatcher:
    """
    Deterministic Skill Matching and Career Readiness Engine.
    Implements mathematically bounded, explainable gap identification and readiness calculation.
    """

    WEIGHT_MAP = {
        "mandatory": 1.5,
        "preferred": 1.0,
        "optional": 0.5
    }

    def match_learner_against_job(
        self,
        learner_skills: Dict[str, Dict[str, Any]], # canonical_name -> {level: int, confidence: float, evidence: str, category: str}
        job_requirements: List[Dict[str, Any]] # list of {skill_name, required_level, requirement_type, category}
    ) -> Dict[str, Any]:
        """
        Executes deterministic matching between demonstrated learner skills and target job requirements.
        """
        matches: List[Dict[str, Any]] = []
        gaps: List[Dict[str, Any]] = []

        total_weighted_required = 0.0
        total_weighted_demonstrated = 0.0

        matched_count = 0
        partial_count = 0
        missing_count = 0

        for req in job_requirements:
            skill_name = req["skill_name"]
            required_level = int(req.get("required_level", 2))
            req_type = req.get("requirement_type", "mandatory").lower()
            category = req.get("category", "General")
            weight = self.WEIGHT_MAP.get(req_type, 1.0)

            total_weighted_required += weight * required_level

            # Check if learner has this skill
            learner_skill = learner_skills.get(skill_name)

            if learner_skill:
                learner_level = int(learner_skill.get("proficiency_level", 1))
                confidence = float(learner_skill.get("confidence_score", 0.8))
                evidence = learner_skill.get("evidence_summary") or learner_skill.get("evidence_snippet") or ""

                score_delta = float(learner_level - required_level)

                # Cap demonstrated level at required level for the readiness formula
                effective_demonstrated = min(learner_level, required_level)
                total_weighted_demonstrated += weight * effective_demonstrated

                if confidence < 0.4:
                    match_type = "insufficient"
                    partial_count += 1
                elif learner_level > required_level:
                    match_type = "exceeds"
                    matched_count += 1
                elif learner_level == required_level:
                    match_type = "matched"
                    matched_count += 1
                else:
                    match_type = "partial"
                    partial_count += 1

                # If partial or insufficient, identify as gap
                if match_type in ["partial", "insufficient"]:
                    severity = "critical" if req_type == "mandatory" else "moderate"
                    gaps.append({
                        "skill_id": req.get("skill_id"),
                        "skill_name": skill_name,
                        "category": category,
                        "required_level": required_level,
                        "current_level": learner_level,
                        "gap_severity": severity,
                        "requirement_type": req_type,
                        "gap_delta": required_level - learner_level
                    })

                matches.append({
                    "skill_id": req.get("skill_id"),
                    "skill_name": skill_name,
                    "category": category,
                    "match_type": match_type,
                    "learner_level": learner_level,
                    "required_level": required_level,
                    "requirement_type": req_type,
                    "importance_weight": weight,
                    "score_delta": score_delta,
                    "confidence": confidence,
                    "evidence_snippet": evidence
                })
            else:
                # Skill is completely missing
                missing_count += 1
                severity = "critical" if req_type == "mandatory" else ("moderate" if req_type == "preferred" else "minor")
                
                gaps.append({
                    "skill_id": req.get("skill_id"),
                    "skill_name": skill_name,
                    "category": category,
                    "required_level": required_level,
                    "current_level": 0,
                    "gap_severity": severity,
                    "requirement_type": req_type,
                    "gap_delta": required_level
                })

                matches.append({
                    "skill_id": req.get("skill_id"),
                    "skill_name": skill_name,
                    "category": category,
                    "match_type": "missing",
                    "learner_level": 0,
                    "required_level": required_level,
                    "requirement_type": req_type,
                    "importance_weight": weight,
                    "score_delta": float(-required_level),
                    "confidence": 1.0,
                    "evidence_snippet": "No demonstrated evidence found in learner profile."
                })

        # Calculate Readiness Score
        if total_weighted_required > 0.0:
            readiness_score = (total_weighted_demonstrated / total_weighted_required) * 100.0
        else:
            readiness_score = 100.0

        readiness_score = round(max(0.0, min(100.0, readiness_score)), 1)

        # Sort gaps: critical first, then moderate, then minor
        severity_order = {"critical": 0, "moderate": 1, "minor": 2}
        gaps.sort(key=lambda g: (severity_order.get(g["gap_severity"], 3), -g["gap_delta"]))

        return {
            "total_required_skills": len(job_requirements),
            "matched_count": matched_count,
            "partial_count": partial_count,
            "missing_count": missing_count,
            "readiness_score": readiness_score,
            "matches": matches,
            "gaps": gaps,
            "calculation_trace": {
                "total_weighted_demonstrated": round(total_weighted_demonstrated, 2),
                "total_weighted_required": round(total_weighted_required, 2),
                "formula": "(Sum of weighted demonstrated capped levels / Sum of weighted required levels) * 100"
            }
        }

skill_matcher = SkillMatcher()
