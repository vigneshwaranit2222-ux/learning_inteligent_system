# REST API Documentation: AI-Powered Learning-to-Career Intelligence System

All API endpoints are namespaced under `/api/v1/` and follow RESTful principles with OpenAPI v3.1 compliance. Interactive Swagger UI is accessible at `http://localhost:8000/docs`.

---

## 1. Authentication (`/api/v1/auth`)

### 1.1 Register
- **Endpoint**: `POST /api/v1/auth/register`
- **Access**: Public
- **Request Body**:
```json
{
  "email": "learner@example.com",
  "password": "Password123!",
  "full_name": "Jane Doe",
  "role": "learner",
  "headline": "Junior Developer",
  "target_role": "Backend Engineer"
}
```
- **Response**: `201 Created`
```json
{
  "access_token": "eyJhbGciOi...",
  "refresh_token": "eyJhbGciOi...",
  "token_type": "bearer",
  "role": "learner",
  "user_id": "97e68b1a-...",
  "learner_id": "18f92a10-...",
  "full_name": "Jane Doe"
}
```

### 1.2 Login
- **Endpoint**: `POST /api/v1/auth/login`
- **Access**: Public
- **Request Body**:
```json
{
  "email": "learner@intelligence.system",
  "password": "LearnerPass123!"
}
```
- **Response**: `200 OK` (Token payload)

### 1.3 Refresh Token
- **Endpoint**: `POST /api/v1/auth/refresh`
- **Access**: Public
- **Request Body**: `{"refresh_token": "eyJhbG..."}`

---

## 2. Learner Profile & Skills (`/api/v1/learners`)

### 2.1 Get Learner Profile
- **Endpoint**: `GET /api/v1/learners/profile`
- **Header**: `Authorization: Bearer <access_token>`
- **Response**: `200 OK`

### 2.2 Update Profile
- **Endpoint**: `PUT /api/v1/learners/profile`
- **Request Body**:
```json
{
  "headline": "AI & Cloud Engineer",
  "target_role": "Senior AI Backend Engineer",
  "years_of_experience": 3.0,
  "github_url": "https://github.com/janedoe"
}
```

### 2.3 Get Verified Demonstrated Skills
- **Endpoint**: `GET /api/v1/learners/skills`
- **Response**: Array of `LearnerSkillResponse` with `proficiency_level` (1-4), `confidence_score`, and verbatim `evidence_list`.

### 2.4 Get Live Dashboard Statistics
- **Endpoint**: `GET /api/v1/learners/dashboard`
- **Response**:
```json
{
  "total_skills_identified": 12,
  "matched_job_skills": 8,
  "skill_gaps": 2,
  "career_readiness_score": 78.5,
  "completed_courses": 3,
  "assessments_completed": 2,
  "active_recommendations": 4,
  "practical_projects": 1,
  "target_job_title": "Senior AI Backend Engineer"
}
```

---

## 3. Resume Ingestion (`/api/v1/resumes`)

### 3.1 Upload Resume
- **Endpoint**: `POST /api/v1/resumes/upload`
- **Content-Type**: `multipart/form-data`
- **Form Field**: `file` (`.pdf`, `.docx`, `.txt`, max 10MB)
- **Features**: Deduplication via SHA-256 hash, section segmentation, hybrid NLP entity extraction, and automatic proficiency evaluation.

---

## 4. Courses & Curriculum (`/api/v1/courses`)

### 4.1 List Courses
- **Endpoint**: `GET /api/v1/courses/`
- **Query Params**: `query` (string), `difficulty` (`beginner|intermediate|advanced`), `skip`, `limit`

### 4.2 Submit Course Completion
- **Endpoint**: `POST /api/v1/courses/complete`
- **Request Body**:
```json
{
  "course_id": "3b29c...",
  "completion_date": "2026-11-10",
  "certificate_url": "https://certificates.io/123",
  "grade": "Passed with Distinction"
}
```

---

## 5. Assessments (`/api/v1/assessments`)

### 5.1 List Assessments
- **Endpoint**: `GET /api/v1/assessments/`

### 5.2 Submit Assessment Answers
- **Endpoint**: `POST /api/v1/assessments/{assessment_id}/submit`
- **Request Body**:
```json
{
  "assessment_id": "...",
  "answers": {
    "question-uuid-1": "It enables concurrent I/O operations without blocking the event loop"
  }
}
```
- **Response**: Returns `score_percentage`, `passed`, and updates learner skill proficiency if score $\ge$ passing threshold.

---

## 6. Job Market Alignment & Matching (`/api/v1/matching`)

### 6.1 Match Learner Against Job
- **Endpoint**: `POST /api/v1/matching/match/{job_id}`
- **Response**:
```json
{
  "job_id": "...",
  "job_title": "Senior AI Backend Engineer",
  "company_name": "Nexus Intelligence Labs",
  "total_required_skills": 8,
  "matched_count": 5,
  "partial_count": 2,
  "missing_count": 1,
  "readiness_score": 74.2,
  "matches": [...],
  "gaps": [...]
}
```

---

## 7. Recommendations (`/api/v1/recommendations`)

### 7.1 Generate Recommendations
- **Endpoint**: `POST /api/v1/recommendations/generate/{job_id}`
- **Response**: List of prioritized recommendations with curated external resources, target levels, and explainable rationale.

### 7.2 Update Recommendation Status
- **Endpoint**: `PATCH /api/v1/recommendations/{recommendation_id}/status`
- **Request Body**: `{"status": "in_progress|completed|dismissed"}`

---

## 8. Career Reports (`/api/v1/reports`)

### 8.1 Generate Career Report
- **Endpoint**: `POST /api/v1/reports/generate/{job_id}`
- **Response**: Generates audit report record, calculation trace, and dynamic PDF on disk.

### 8.2 Download PDF Report
- **Endpoint**: `GET /api/v1/reports/{report_id}/pdf`
- **Response**: `application/pdf` binary stream.
