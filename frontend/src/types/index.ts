export interface User {
  id: string;
  email: string;
  full_name: string;
  role: 'admin' | 'learner' | 'mentor';
  is_active: boolean;
}

export interface LearnerProfile {
  id: string;
  user_id: string;
  headline?: string;
  bio?: string;
  location?: string;
  target_role?: string;
  years_of_experience: number;
  education_level?: string;
  github_url?: string;
  linkedin_url?: string;
}

export interface SkillCategory {
  id: string;
  name: string;
  slug: string;
  description?: string;
}

export interface Skill {
  id: string;
  category_id: string;
  name: string;
  slug: string;
  popularity_score: number;
  category?: SkillCategory;
}

export interface SkillEvidence {
  id: string;
  source_type: 'resume' | 'course' | 'assessment' | 'project';
  text_snippet: string;
  confidence: number;
  created_at: string;
}

export interface LearnerSkill {
  id: string;
  skill_id: string;
  skill: Skill;
  proficiency_level: number; // 1: Beginner, 2: Intermediate, 3: Advanced, 4: Expert
  confidence_score: number;
  years_experience: number;
  evidence_summary?: string;
  evidence_list: SkillEvidence[];
}

export interface CourseModule {
  id: string;
  title: string;
  order_index: number;
  description?: string;
}

export interface LearningOutcome {
  id: string;
  skill_id: string;
  target_proficiency: number;
  outcome_statement: string;
}

export interface Course {
  id: string;
  title: string;
  provider: string;
  code?: string;
  description?: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  estimated_hours: number;
  url?: string;
  modules: CourseModule[];
  learning_outcomes: LearningOutcome[];
}

export interface AssessmentQuestion {
  id: string;
  question_text: string;
  question_type: string;
  options: string[];
}

export interface Assessment {
  id: string;
  course_id?: string;
  skill_id?: string;
  title: string;
  description?: string;
  passing_score: number;
  time_limit_minutes: number;
  questions: AssessmentQuestion[];
}

export interface JobRequirement {
  id: string;
  skill_id: string;
  skill: Skill;
  required_level: number;
  requirement_type: 'mandatory' | 'preferred' | 'optional';
  importance_weight: number;
}

export interface JobDescription {
  id: string;
  role_id: string;
  title: string;
  company_name: string;
  location?: string;
  employment_type: string;
  experience_required?: string;
  raw_text: string;
  requirements: JobRequirement[];
}

export interface SkillMatchItem {
  skill_id: string;
  skill_name: string;
  category: string;
  match_type: 'matched' | 'partial' | 'missing' | 'insufficient' | 'exceeds';
  learner_level: number;
  required_level: number;
  requirement_type: string;
  importance_weight: number;
  score_delta: number;
  confidence: number;
  evidence_snippet?: string;
}

export interface SkillGapItem {
  skill_id: string;
  skill_name: string;
  category: string;
  required_level: number;
  current_level: number;
  gap_severity: 'critical' | 'moderate' | 'minor';
  requirement_type: string;
}

export interface MatchingResult {
  job_id: string;
  job_title: string;
  company_name: string;
  learner_id: string;
  total_required_skills: number;
  matched_count: number;
  partial_count: number;
  missing_count: number;
  readiness_score: number;
  matches: SkillMatchItem[];
  gaps: SkillGapItem[];
}

export interface LearningResource {
  id: string;
  title: string;
  resource_type: string;
  provider: string;
  url: string;
  estimated_hours: number;
  target_level: number;
}

export interface Recommendation {
  id: string;
  learner_id: string;
  skill: Skill;
  resource?: LearningResource;
  priority: 'high' | 'medium' | 'low';
  reason: string;
  expected_outcome: string;
  status: 'active' | 'in_progress' | 'completed' | 'dismissed';
}

export interface CareerReport {
  id: string;
  job_id: string;
  job_title: string;
  company_name: string;
  overall_readiness_score: number;
  breakdown: any;
  executive_summary: string;
  pdf_path?: string;
  generated_at: string;
}

export interface DashboardStats {
  total_skills_identified: number;
  matched_job_skills: number;
  skill_gaps: number;
  career_readiness_score: number;
  completed_courses: number;
  assessments_completed: number;
  active_recommendations: number;
  practical_projects: number;
  target_job_title?: string;
}
