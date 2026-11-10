from typing import Dict, List, Optional, Tuple
from rapidfuzz import fuzz, process

CANONICAL_SKILL_CATALOG: Dict[str, Dict[str, any]] = {
    # Programming Languages
    "Python": {"category": "Programming", "aliases": ["python3", "python 3", "py", "python programming"]},
    "JavaScript": {"category": "Programming", "aliases": ["js", "es6", "ecmascript", "javascript programming"]},
    "TypeScript": {"category": "Programming", "aliases": ["ts", "typescript lang"]},
    "Java": {"category": "Programming", "aliases": ["java 17", "java 21", "core java", "j2ee"]},
    "C++": {"category": "Programming", "aliases": ["cpp", "c plus plus", "c/c++"]},
    "C#": {"category": "Programming", "aliases": ["csharp", "c sharp", ".net c#"]},
    "Go": {"category": "Programming", "aliases": ["golang", "go lang"]},
    "Rust": {"category": "Programming", "aliases": ["rust lang", "rust-lang"]},
    "SQL": {"category": "Programming", "aliases": ["structured query language", "ansi sql"]},
    
    # Backend Development
    "FastAPI": {"category": "Backend Development", "aliases": ["fast api", "fastapi framework"]},
    "Django": {"category": "Backend Development", "aliases": ["django framework", "django rest framework", "drf"]},
    "Flask": {"category": "Backend Development", "aliases": ["flask web", "flask python"]},
    "Node.js": {"category": "Backend Development", "aliases": ["nodejs", "node js", "node"]},
    "Express.js": {"category": "Backend Development", "aliases": ["express", "expressjs"]},
    "NestJS": {"category": "Backend Development", "aliases": ["nest.js", "nest js"]},
    "Spring Boot": {"category": "Backend Development", "aliases": ["springboot", "spring", "spring framework"]},
    "REST API": {"category": "Backend Development", "aliases": ["restful api", "restful services", "rest apis", "rest web services"]},
    "GraphQL": {"category": "Backend Development", "aliases": ["graphql api", "gql"]},
    
    # Frontend Development
    "React": {"category": "Frontend Development", "aliases": ["reactjs", "react.js", "react 18"]},
    "Next.js": {"category": "Frontend Development", "aliases": ["nextjs", "next js"]},
    "Vue.js": {"category": "Frontend Development", "aliases": ["vue", "vuejs", "vue 3"]},
    "Angular": {"category": "Frontend Development", "aliases": ["angularjs", "angular 2+"]},
    "Tailwind CSS": {"category": "Frontend Development", "aliases": ["tailwind", "tailwindcss"]},
    "HTML5": {"category": "Frontend Development", "aliases": ["html", "semantic html"]},
    "CSS3": {"category": "Frontend Development", "aliases": ["css", "modern css", "flexbox", "css grid"]},
    "Redux": {"category": "Frontend Development", "aliases": ["redux toolkit", "rtk"]},

    # Databases & Storage
    "PostgreSQL": {"category": "Databases", "aliases": ["postgres", "postgre sql", "psql"]},
    "MySQL": {"category": "Databases", "aliases": ["my sql", "mariadb"]},
    "MongoDB": {"category": "Databases", "aliases": ["mongo", "mongodb atlas"]},
    "Redis": {"category": "Databases", "aliases": ["redis cache", "redis key-value"]},
    "Elasticsearch": {"category": "Databases", "aliases": ["elastic search", "elk stack", "opensearch"]},
    "SQLite": {"category": "Databases", "aliases": ["sqlite3"]},

    # Cloud & DevOps
    "Docker": {"category": "DevOps", "aliases": ["docker container", "dockerfiles", "containerization"]},
    "Kubernetes": {"category": "DevOps", "aliases": ["k8s", "k8", "kube"]},
    "AWS": {"category": "Cloud", "aliases": ["amazon web services", "aws cloud", "ec2", "s3", "lambda"]},
    "Google Cloud Platform": {"category": "Cloud", "aliases": ["gcp", "google cloud"]},
    "Azure": {"category": "Cloud", "aliases": ["microsoft azure", "azure cloud"]},
    "CI/CD": {"category": "DevOps", "aliases": ["continuous integration", "continuous delivery", "github actions", "gitlab ci", "jenkins"]},
    "Terraform": {"category": "DevOps", "aliases": ["iac", "infrastructure as code", "hashicorp terraform"]},
    "Linux": {"category": "DevOps", "aliases": ["ubuntu", "bash", "shell scripting", "unix"]},
    "Git": {"category": "DevOps", "aliases": ["github", "gitlab", "version control"]},

    # AI & Machine Learning
    "Machine Learning": {"category": "AI/ML", "aliases": ["ml", "applied machine learning", "statistical learning"]},
    "Deep Learning": {"category": "AI/ML", "aliases": ["dl", "neural networks", "deep neural networks"]},
    "PyTorch": {"category": "AI/ML", "aliases": ["torch", "pytorch lightning"]},
    "TensorFlow": {"category": "AI/ML", "aliases": ["tf", "keras", "tensorflow 2"]},
    "Scikit-Learn": {"category": "AI/ML", "aliases": ["sklearn", "scikit learn"]},
    "Pandas": {"category": "AI/ML", "aliases": ["pandas dataframe", "pandas lib"]},
    "NumPy": {"category": "AI/ML", "aliases": ["numpy array"]},
    "Natural Language Processing": {"category": "AI/ML", "aliases": ["nlp", "text mining", "computational linguistics"]},
    "spaCy": {"category": "AI/ML", "aliases": ["spacy nlp"]},
    "Computer Vision": {"category": "AI/ML", "aliases": ["cv", "opencv", "image processing"]},

    # Generative AI & LLMs
    "Large Language Models": {"category": "Generative AI", "aliases": ["llm", "llms", "large language model"]},
    "Retrieval-Augmented Generation": {"category": "Generative AI", "aliases": ["rag", "rag architecture", "rag systems"]},
    "LangChain": {"category": "Generative AI", "aliases": ["lang chain", "langchain framework"]},
    "LlamaIndex": {"category": "Generative AI", "aliases": ["llama index", "gpt index"]},
    "Prompt Engineering": {"category": "Generative AI", "aliases": ["prompt design", "few-shot prompting"]},
    "Vector Databases": {"category": "Generative AI", "aliases": ["vector db", "chromadb", "qdrant", "pinecone", "weaviate", "pgvector"]},
    "Hugging Face": {"category": "Generative AI", "aliases": ["huggingface", "transformers", "hf hub"]},
    "Fine-Tuning": {"category": "Generative AI", "aliases": ["lora", "qlora", "peft", "model fine-tuning"]},

    # Soft Skills & Professional
    "Problem Solving": {"category": "Soft Skills", "aliases": ["analytical thinking", "troubleshooting", "algorithmic thinking"]},
    "System Design": {"category": "Professional Skills", "aliases": ["software architecture", "distributed systems design", "high level design", "low level design"]},
    "Agile Methodology": {"category": "Professional Skills", "aliases": ["scrum", "kanban", "sprint planning"]},
    "Communication": {"category": "Soft Skills", "aliases": ["technical communication", "collaboration", "cross-functional communication"]},
    "Team Leadership": {"category": "Soft Skills", "aliases": ["mentoring", "technical leadership", "team management"]}
}

# Build Fast Inverted Alias Lookup Map
ALIAS_TO_CANONICAL: Dict[str, str] = {}
for canonical, meta in CANONICAL_SKILL_CATALOG.items():
    ALIAS_TO_CANONICAL[canonical.lower()] = canonical
    for alias in meta["aliases"]:
        ALIAS_TO_CANONICAL[alias.lower()] = canonical

def normalize_skill_name(input_skill: str, threshold: float = 85.0) -> Optional[Tuple[str, str, float]]:
    """
    Normalizes any raw input skill string to its canonical name and category.
    Returns: (canonical_name, category, confidence_score) or None if no match.
    """
    clean_input = input_skill.strip().lower()
    if not clean_input:
        return None

    # 1. Exact match in canonical / alias lookup
    if clean_input in ALIAS_TO_CANONICAL:
        canonical = ALIAS_TO_CANONICAL[clean_input]
        return (canonical, CANONICAL_SKILL_CATALOG[canonical]["category"], 1.0)

    # 2. RapidFuzz Fuzzy matching against aliases and canonicals
    choices = list(ALIAS_TO_CANONICAL.keys())
    best_match = process.extractOne(
        clean_input,
        choices,
        scorer=fuzz.token_set_ratio,
        score_cutoff=threshold
    )

    if best_match:
        matched_str, score, _ = best_match
        canonical = ALIAS_TO_CANONICAL[matched_str]
        confidence = round(score / 100.0, 3)
        return (canonical, CANONICAL_SKILL_CATALOG[canonical]["category"], confidence)

    return None
