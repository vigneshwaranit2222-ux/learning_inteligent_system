# Implementation Decisions & Mathematical Formulas

## 1. Mathematical Formulas

### 1.1 Career Readiness Score
$$\text{Readiness Score} = \left(\frac{\sum_{i=1}^N w_i \cdot \min(D_i, R_i)}{\sum_{i=1}^N w_i \cdot R_i}\right) \times 100$$
Where:
- $N$ is the total number of required skills for the target job.
- $R_i \in \{1, 2, 3, 4\}$ is the required proficiency level for skill $i$.
- $D_i \in \{0, 1, 2, 3, 4\}$ is the learner's demonstrated proficiency level for skill $i$ ($0$ if unobserved).
- $w_i$ is the requirement weight:
  - $w_i = 1.5$ for Mandatory skills ($M$).
  - $w_i = 1.0$ for Preferred skills ($P$).
  - $w_i = 0.5$ for Optional skills ($O$).

Note: $D_i$ is explicitly capped at $R_i$ ($\min(D_i, R_i)$) to prevent high proficiency in an optional skill from artificially compensating for missing mandatory skills.

### 1.2 Multi-Evidence Proficiency Evaluation
For each canonical skill possessed by a learner:
$$P = \text{round}\left(\min\left(4, \sum_{k} w_k \cdot E_k\right)\right)$$
Where the evidence sources $E_k$ and weights $w_k$ are:
1. **Work Experience ($w_{exp} = 0.40$)**:
   - $\ge 4$ years: $4.0$
   - $2 - 4$ years: $3.0$
   - $1 - 2$ years: $2.0$
   - $< 1$ year: $1.0$
2. **Practical Projects ($w_{proj} = 0.30$)**:
   - Production/Verified complex project: $4.0$
   - Intermediate project with tests/repo: $3.0$
   - Basic portfolio exercise: $2.0$
   - Single demo or snippet: $1.0$
3. **Assessment Results ($w_{ass} = 0.20$)**:
   - Score $\ge 90\%$: $4.0$
   - Score $75\% - 89\%$: $3.0$
   - Score $60\% - 74\%$: $2.0$
   - Score $< 60\%$: $1.0$
4. **Course Completions ($w_{course} = 0.10$)**:
   - Advanced capstone course: $3.0$
   - Intermediate course: $2.0$
   - Intro/Survey course: $1.0$

**Hard Safety Guardrail**:
- If $E_{ass} = 0$ and $E_{proj} = 0$ (resume text mention only), $P$ is capped at $\min(P, 2)$ (Intermediate). Advanced and Expert can never be assigned purely on unverified resume claims.

## 2. Technology Choices & Justifications

### 2.1 Database & ORM
- **Engine**: PostgreSQL with asyncpg. Provides relational integrity, transactions, and JSONB indexing for skill evidence.
- **ORM**: SQLAlchemy 2.0 with async engine. Ensures full asynchronous query pipelining without blocking event loops.
- **SQLite Async Fallback**: Implemented via `aiosqlite` for automated unit/integration tests and zero-dependency local verification when external PostgreSQL service is starting or isolated.

### 2.2 Skill Normalization & Extraction
- **Rule & Canonical Lookup + RapidFuzz**: 100% deterministic, ultra-fast ($< 5\text{ms}$), completely explainable.
- **spaCy NLP**: Tokenization, lemmatization, and noun chunks identify compound terms (e.g. "Continuous Integration/Continuous Delivery").
- **LLM Contextual Fallback**: Standardized OpenAI / Ollama REST API compatibility. If LLM is active, output is strictly validated against canonical categories using Pydantic; if local LLM is inactive or offline, the deterministic NLP + RapidFuzz pipeline executes seamlessly with full fidelity.

### 2.3 Vector Database Choice
- **Primary Choice**: PostgreSQL `pgvector` / In-Memory Cosine Similarity Engine with Qdrant client adapter.
- **Rationale**: Keeps the architecture streamlined, eliminates distributed network failure points during standard deployments, and ensures atomic consistency between vector embeddings and relational entities.

### 2.4 Document Processing
- **PyMuPDF (`fitz`)**: Proven 10x speed advantage over pdfminer and reliable extraction of multi-column resume layouts.
- **python-docx**: Robust XML-based Word document parsing.
- **SHA-256 Hashing**: Prevents redundant processing jobs, saves compute, and enforces idempotency.
