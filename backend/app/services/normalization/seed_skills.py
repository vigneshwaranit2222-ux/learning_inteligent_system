import re
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.skill import SkillCategory, Skill, SkillAlias
from app.models.job import JobRole, JobDescription, JobRequirement
from app.models.course import Course, CourseModule, LearningOutcome, Assessment, AssessmentQuestion
from app.models.recommendation import LearningResource
from ai_engine.normalization.canonical_skills import CANONICAL_SKILL_CATALOG
from ai_engine.recommendation.recommender import CURATED_RESOURCES

def slugify(text: str) -> str:
    text = text.lower()
    text = text.replace("c++", "cpp").replace("c#", "csharp").replace(".net", "dotnet").replace(".js", "-js")
    return re.sub(r'[\W_]+', '-', text).strip('-')

def seed_master_data(db: Session):
    """
    Seeds canonical categories, skills, aliases, resources, courses, assessments, and jobs.
    Idempotent: skips existing entries.
    """
    # 1. Categories & Skills
    categories_map = {}
    for canonical_name, meta in CANONICAL_SKILL_CATALOG.items():
        cat_name = meta["category"]
        if cat_name not in categories_map:
            cat = db.scalar(select(SkillCategory).where(SkillCategory.name == cat_name))
            if not cat:
                cat = SkillCategory(
                    name=cat_name,
                    slug=slugify(cat_name),
                    description=f"Industry competencies in {cat_name}"
                )
                db.add(cat)
                db.flush()
            categories_map[cat_name] = cat

        # Skill
        skill = db.scalar(select(Skill).where(Skill.name == canonical_name))
        if not skill:
            skill = Skill(
                category_id=categories_map[cat_name].id,
                name=canonical_name,
                slug=slugify(canonical_name),
                description=f"Proficiency in {canonical_name}",
                popularity_score=1.0,
                is_verified=True
            )
            db.add(skill)
            db.flush()

            # Aliases
            for alias in meta["aliases"]:
                existing_alias = db.scalar(select(SkillAlias).where(SkillAlias.alias == alias))
                if not existing_alias:
                    sa = SkillAlias(
                        skill_id=skill.id,
                        alias=alias,
                        normalized_alias=alias.lower().strip()
                    )
                    db.add(sa)

    db.commit()

    # 2. Learning Resources
    for skill_name, resources in CURATED_RESOURCES.items():
        skill = db.scalar(select(Skill).where(Skill.name == skill_name))
        if skill:
            for r in resources:
                existing_res = db.scalar(select(LearningResource).where(LearningResource.title == r["title"]))
                if not existing_res:
                    lr = LearningResource(
                        skill_id=skill.id,
                        title=r["title"],
                        resource_type=r["type"],
                        provider=r["provider"],
                        url=r["url"],
                        estimated_hours=r["estimated_hours"],
                        target_level=r.get("target_level", 2)
                    )
                    db.add(lr)
    db.commit()

    # 3. Sample Courses & Assessments
    sample_courses = [
        {
            "title": "Mastering FastAPI and Modern Async Python",
            "provider": "Enterprise Academy",
            "code": "PY-301",
            "description": "Comprehensive course covering asynchronous REST APIs, Pydantic v2 schemas, SQLAlchemy 2.0 ORM, and dependency injection.",
            "difficulty": "intermediate",
            "estimated_hours": 20,
            "url": "https://fastapi.tiangolo.com",
            "skills": [("FastAPI", 3), ("Python", 3), ("REST API", 3)],
            "assessment": {
                "title": "FastAPI & Async Python Competency Exam",
                "passing_score": 75.0,
                "skill": "FastAPI",
                "questions": [
                    {
                        "text": "What is the primary benefit of declaring route handlers with 'async def' in FastAPI?",
                        "type": "mcq",
                        "options": [
                            "It enables concurrent I/O operations without blocking the event loop",
                            "It guarantees automatic database table indexing",
                            "It compiles Python bytecode to native assembly",
                            "It disables CORS origin checks"
                        ],
                        "correct": "It enables concurrent I/O operations without blocking the event loop",
                        "explanation": "Asynchronous def allows ASGI servers (like Uvicorn) to interleave concurrent I/O tasks efficiently on a single thread."
                    },
                    {
                        "text": "How does Pydantic v2 achieve high serialization and validation performance?",
                        "type": "mcq",
                        "options": [
                            "By utilizing a high-speed Rust-based core (pydantic-core)",
                            "By bypassing type validation completely",
                            "By caching responses in browser cookies",
                            "By executing in the GPU"
                        ],
                        "correct": "By utilizing a high-speed Rust-based core (pydantic-core)",
                        "explanation": "Pydantic v2 rewrote its internal validation logic in Rust via pydantic-core, yielding massive speedups."
                    }
                ]
            }
        },
        {
            "title": "Docker and Kubernetes Cloud Architecture",
            "provider": "Cloud Native Foundation",
            "code": "OPS-201",
            "description": "Learn to containerize microservices, write optimized Dockerfiles, and orchestrate pods with Kubernetes.",
            "difficulty": "intermediate",
            "estimated_hours": 25,
            "url": "https://kubernetes.io",
            "skills": [("Docker", 2), ("Kubernetes", 2), ("DevOps", 2)],
            "assessment": {
                "title": "Container Orchestration & Docker Exam",
                "passing_score": 70.0,
                "skill": "Docker",
                "questions": [
                    {
                        "text": "What is the main benefit of multi-stage Docker builds?",
                        "type": "mcq",
                        "options": [
                            "Minimizing final image size by discarding build tools and intermediate artifacts",
                            "Allowing multiple containers to run in one process",
                            "Running Docker on systems without Linux kernels",
                            "Automatically encrypting environment variables"
                        ],
                        "correct": "Minimizing final image size by discarding build tools and intermediate artifacts",
                        "explanation": "Multi-stage builds permit keeping compilation SDKs in build stages while copying only production binaries to the final image."
                    }
                ]
            }
        },
        {
            "title": "Building Production RAG Systems with LLMs",
            "provider": "AI Systems Institute",
            "code": "AI-401",
            "description": "Deep dive into vector embeddings, semantic search, dense retrieval, and local LLM orchestration.",
            "difficulty": "advanced",
            "estimated_hours": 30,
            "url": "https://qdrant.tech",
            "skills": [("Large Language Models", 3), ("Retrieval-Augmented Generation", 3), ("Python", 3)]
        }
    ]

    for c_data in sample_courses:
        existing_course = db.scalar(select(Course).where(Course.title == c_data["title"]))
        if not existing_course:
            course = Course(
                title=c_data["title"],
                provider=c_data["provider"],
                code=c_data["code"],
                description=c_data["description"],
                difficulty=c_data["difficulty"],
                estimated_hours=c_data["estimated_hours"],
                url=c_data["url"]
            )
            db.add(course)
            db.flush()

            # Modules
            m1 = CourseModule(course_id=course.id, title="Module 1: Foundations & Architecture", order_index=1)
            m2 = CourseModule(course_id=course.id, title="Module 2: Practical Implementation & Capstone", order_index=2)
            db.add_all([m1, m2])

            # Outcomes
            for sk_name, req_lvl in c_data.get("skills", []):
                sk = db.scalar(select(Skill).where(Skill.name == sk_name))
                if sk:
                    out = LearningOutcome(
                        course_id=course.id,
                        skill_id=sk.id,
                        target_proficiency=req_lvl,
                        outcome_statement=f"Students will achieve Level {req_lvl} competence in {sk_name}."
                    )
                    db.add(out)

            # Assessment
            if "assessment" in c_data:
                ass_info = c_data["assessment"]
                ass_skill = db.scalar(select(Skill).where(Skill.name == ass_info["skill"]))
                assessment = Assessment(
                    course_id=course.id,
                    skill_id=ass_skill.id if ass_skill else None,
                    title=ass_info["title"],
                    description="Official multiple-choice proficiency verification assessment.",
                    passing_score=ass_info["passing_score"],
                    time_limit_minutes=30
                )
                db.add(assessment)
                db.flush()

                for q in ass_info.get("questions", []):
                    question = AssessmentQuestion(
                        assessment_id=assessment.id,
                        question_text=q["text"],
                        question_type=q["type"],
                        options=q["options"],
                        correct_answer=q["correct"],
                        explanation=q.get("explanation")
                    )
                    db.add(question)

    db.commit()

    # 4. Sample Job Roles & Descriptions
    sample_jobs = [
        {
            "role_title": "Senior AI Backend Engineer",
            "industry": "Information Technology",
            "title": "Senior AI Backend Engineer",
            "company_name": "Nexus Intelligence Labs",
            "location": "San Francisco, CA (Hybrid)",
            "employment_type": "Full-time",
            "experience_required": "4-6 years",
            "raw_text": """
We are seeking an experienced Senior AI Backend Engineer to scale our autonomous agent and learning intelligence infrastructure.
Requirements:
- Strong mastery of Python (4+ years) and FastAPI framework.
- Hands-on experience developing and deploying Large Language Models (LLMs) and RAG architectures.
- Deep expertise in PostgreSQL database modeling, query optimization, and vector search.
- Solid containerization experience with Docker and Kubernetes.
- Experience with REST APIs, Git, and automated CI/CD pipelines.
            """,
            "requirements": [
                ("Python", 4, "mandatory", 1.5),
                ("FastAPI", 3, "mandatory", 1.5),
                ("PostgreSQL", 3, "mandatory", 1.5),
                ("Docker", 2, "mandatory", 1.5),
                ("Large Language Models", 3, "preferred", 1.0),
                ("Retrieval-Augmented Generation", 3, "preferred", 1.0),
                ("Kubernetes", 2, "preferred", 1.0),
                ("Git", 2, "optional", 0.5)
            ]
        },
        {
            "role_title": "Full-Stack Software Engineer",
            "industry": "Software & Web Development",
            "title": "Full-Stack Software Engineer (React / Python)",
            "company_name": "CloudScale Systems",
            "location": "Remote",
            "employment_type": "Full-time",
            "experience_required": "2-4 years",
            "raw_text": """
CloudScale is looking for a versatile Full-Stack Engineer proficient in React and Python backends.
Requirements:
- Demonstrated experience in modern React (React 18, TypeScript, Tailwind CSS).
- Backend proficiency with Python (FastAPI or Django) and REST APIs.
- Relational database experience with PostgreSQL or MySQL.
- Containerization with Docker and standard Git version control.
            """,
            "requirements": [
                ("React", 3, "mandatory", 1.5),
                ("TypeScript", 2, "mandatory", 1.5),
                ("Python", 2, "mandatory", 1.5),
                ("FastAPI", 2, "preferred", 1.0),
                ("PostgreSQL", 2, "mandatory", 1.5),
                ("Tailwind CSS", 2, "preferred", 1.0),
                ("Docker", 2, "optional", 0.5)
            ]
        }
    ]

    for j_data in sample_jobs:
        role = db.scalar(select(JobRole).where(JobRole.title == j_data["role_title"]))
        if not role:
            role = JobRole(title=j_data["role_title"], industry=j_data["industry"])
            db.add(role)
            db.flush()

        job_desc = db.scalar(select(JobDescription).where(JobDescription.title == j_data["title"]))
        if not job_desc:
            import hashlib
            file_hash = hashlib.sha256(j_data["raw_text"].strip().encode("utf-8")).hexdigest()
            job_desc = JobDescription(
                role_id=role.id,
                title=j_data["title"],
                company_name=j_data["company_name"],
                location=j_data["location"],
                employment_type=j_data["employment_type"],
                experience_required=j_data["experience_required"],
                raw_text=j_data["raw_text"].strip(),
                file_hash=file_hash,
                is_active=True
            )
            db.add(job_desc)
            db.flush()

            for sk_name, req_lvl, req_type, weight in j_data["requirements"]:
                sk = db.scalar(select(Skill).where(Skill.name == sk_name))
                if sk:
                    jr = JobRequirement(
                        job_id=job_desc.id,
                        skill_id=sk.id,
                        required_level=req_lvl,
                        requirement_type=req_type,
                        importance_weight=weight
                    )
                    db.add(jr)

    db.commit()
    print("Master data seeded successfully!")
