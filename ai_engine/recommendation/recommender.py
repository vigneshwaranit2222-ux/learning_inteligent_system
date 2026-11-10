from typing import Dict, List, Any, Optional

# Curated High-Quality Real-World Learning Resources Catalog
CURATED_RESOURCES: Dict[str, List[Dict[str, Any]]] = {
    "FastAPI": [
        {
            "title": "FastAPI Production Foundations & Async APIs",
            "type": "course",
            "provider": "Official FastAPI Tutorial",
            "url": "https://fastapi.tiangolo.com/tutorial/",
            "estimated_hours": 12,
            "target_level": 2,
            "outcome": "Master asynchronous REST API development, Pydantic v2 data models, and dependency injection."
        },
        {
            "title": "Microservices with FastAPI and Docker",
            "type": "project",
            "provider": "TestDriven.io",
            "url": "https://testdriven.io/courses/tdd-fastapi/",
            "estimated_hours": 20,
            "target_level": 3,
            "outcome": "Architect containerized FastAPI services with PostgreSQL, Celery, and automated pytest suites."
        }
    ],
    "Docker": [
        {
            "title": "Docker Hands-On for Backend Developers",
            "type": "tutorial",
            "provider": "Docker Docs",
            "url": "https://docs.docker.com/get-started/",
            "estimated_hours": 8,
            "target_level": 2,
            "outcome": "Build multi-stage Dockerfiles, manage volumes, network bridge configuration, and multi-container Compose setups."
        }
    ],
    "PostgreSQL": [
        {
            "title": "PostgreSQL Performance Optimization & Indexing",
            "type": "course",
            "provider": "PostgreSQL Official Docs",
            "url": "https://www.postgresql.org/docs/current/indexes.html",
            "estimated_hours": 15,
            "target_level": 3,
            "outcome": "Design B-Tree/GIN indexes, analyze EXPLAIN ANALYZE execution plans, and tune connection pools."
        }
    ],
    "React": [
        {
            "title": "Full-Stack Modern React with TypeScript",
            "type": "course",
            "provider": "React.dev",
            "url": "https://react.dev/learn",
            "estimated_hours": 25,
            "target_level": 2,
            "outcome": "Master React 18 hooks, custom state management, performance optimization, and TypeScript integration."
        }
    ],
    "Python": [
        {
            "title": "Python 3.11+ Advanced Concurrency & Type Systems",
            "type": "documentation",
            "provider": "Python Software Foundation",
            "url": "https://docs.python.org/3/library/asyncio.html",
            "estimated_hours": 14,
            "target_level": 3,
            "outcome": "Build resilient asynchronous applications using asyncio tasks, coroutines, and strict typing."
        }
    ],
    "Kubernetes": [
        {
            "title": "Kubernetes Core Concepts & Cloud Deployments",
            "type": "tutorial",
            "provider": "Kubernetes.io",
            "url": "https://kubernetes.io/docs/tutorials/",
            "estimated_hours": 18,
            "target_level": 2,
            "outcome": "Deploy scalable microservices using Deployments, Services, ConfigMaps, and Ingress controllers."
        }
    ],
    "Large Language Models": [
        {
            "title": "Building Applications with LLMs and LangChain",
            "type": "course",
            "provider": "DeepLearning.AI",
            "url": "https://www.deeplearning.ai/short-courses/langchain-for-llm-application-development/",
            "estimated_hours": 10,
            "target_level": 2,
            "outcome": "Integrate local and cloud LLMs, manage token contexts, and implement structured output parsing."
        }
    ],
    "Retrieval-Augmented Generation": [
        {
            "title": "Advanced RAG Pipelines with Vector Databases",
            "type": "project",
            "provider": "Qdrant / Hugging Face",
            "url": "https://qdrant.tech/articles/what-is-rag-in-ai/",
            "estimated_hours": 16,
            "target_level": 3,
            "outcome": "Construct semantic search pipelines with dense embeddings, rerankers, and chunking strategies."
        }
    ]
}

class RecommendationEngine:
    def generate_recommendations_for_gaps(
        self,
        gaps: List[Dict[str, Any]],
        available_courses: Optional[List[Dict[str, Any]]] = None
    ) -> List[Dict[str, Any]]:
        recommendations = []
        available_courses = available_courses or []

        for gap in gaps:
            skill_name = gap["skill_name"]
            req_level = gap["required_level"]
            curr_level = gap["current_level"]
            severity = gap["gap_severity"]

            priority = "high" if severity == "critical" else ("medium" if severity == "moderate" else "low")
            
            # Check internal course catalog first
            matched_internal_courses = [
                c for c in available_courses
                if skill_name.lower() in c.get("title", "").lower() or skill_name.lower() in c.get("description", "").lower()
            ]

            if matched_internal_courses:
                for c in matched_internal_courses[:1]:
                    recommendations.append({
                        "skill_name": skill_name,
                        "current_level": curr_level,
                        "target_level": req_level,
                        "priority": priority,
                        "resource_title": c["title"],
                        "resource_type": "course",
                        "provider": c.get("provider", "Internal Academy"),
                        "url": c.get("url") or f"/courses/{c.get('id')}",
                        "estimated_hours": c.get("estimated_hours", 10),
                        "reason": f"Required Level {req_level} exceeded current Level {curr_level} in {gap.get('requirement_type', 'mandatory')} skill.",
                        "expected_outcome": f"Elevate {skill_name} proficiency from {curr_level} to {req_level} by completing syllabus modules and practical assessment."
                    })

            # Check curated catalog
            curated_list = CURATED_RESOURCES.get(skill_name, [])
            if curated_list:
                for res in curated_list:
                    recommendations.append({
                        "skill_name": skill_name,
                        "current_level": curr_level,
                        "target_level": max(req_level, res.get("target_level", req_level)),
                        "priority": priority,
                        "resource_title": res["title"],
                        "resource_type": res["type"],
                        "provider": res["provider"],
                        "url": res["url"],
                        "estimated_hours": res["estimated_hours"],
                        "reason": f"Target job requires {gap.get('requirement_type', 'mandatory')} proficiency at Level {req_level}. Currently evaluated at Level {curr_level}.",
                        "expected_outcome": res["outcome"]
                    })
            else:
                # Default structured action item if skill has no curated entry yet
                recommendations.append({
                    "skill_name": skill_name,
                    "current_level": curr_level,
                    "target_level": req_level,
                    "priority": priority,
                    "resource_title": f"Mastering {skill_name}: Core Foundations & Practice",
                    "resource_type": "project",
                    "provider": "Self-Directed Capstone",
                    "url": "https://github.com/explore",
                    "estimated_hours": 15,
                    "reason": f"Demonstrated evidence is missing or below target Level {req_level}.",
                    "expected_outcome": f"Build a practical verified project demonstrating {skill_name} competencies to satisfy employer requirements."
                })

        return recommendations

recommendation_engine = RecommendationEngine()
