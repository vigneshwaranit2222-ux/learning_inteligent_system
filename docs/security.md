# Security Architecture & Safeguards

## 1. Authentication & Password Security
- **Argon2id**: All passwords are encrypted with `argon2-cffi` utilizing memory-hard parameters ($m=64\text{MB}$, $t=2$ passes, $p=1$ thread), effectively neutralizing GPU and ASIC brute-force attack vectors.
- **JWT (JSON Web Tokens)**:
  - Access Token: Short-lived (60 minutes default), signed via HMAC-SHA256 with strong environment secrets.
  - Refresh Token: Long-lived (7 days), stored securely and required for rotation.
  - Revocation & Expiration: Strict type validation (`access` vs `refresh`), payload expiration check, and user active status verification on every authenticated call.

## 2. Role-Based Access Control (RBAC)
- Role definitions:
  - `admin`: Global system configuration, user activation/deactivation, skill master taxonomy management, system analytics, and audit inspection.
  - `learner`: Self-profile management, resume upload, course completion submissions, assessment exams, and career report generation.
  - `mentor`: Feedback provision, assessment reviews, and student verification.
- Enforced at route level through FastAPI dependency injection guards (`require_roles(["admin"])`).

## 3. Data Protection & File Validation
- **SHA-256 Content-Addressed Vault**: Files uploaded are hashed immediately using SHA-256. Duplicate uploads are detected to protect storage capacity and avoid redundant NLP parsing.
- **File Validation**:
  - File extensions strictly limited to `.pdf`, `.docx`, `.doc`, `.txt`, `.md`.
  - Content length enforced at 10MB limit.
  - Stored under randomized UUID filenames (`{uuid}_{filename}`) to eliminate directory traversal risks (`../`).

## 4. SQL Injection & Database Isolation
- **SQLAlchemy 2.0 ORM**: 100% of database interactions execute via parameterized queries and typed expressions, preventing SQL injection vulnerabilities.
- **Audit Logging**: Every sensitive mutation (user creation, profile edit, resume upload, assessment submission, status toggle) writes an immutable record to the `audit_logs` table containing the user ID, entity ID, action, client IP address, and request correlation ID (`X-Correlation-ID`).
