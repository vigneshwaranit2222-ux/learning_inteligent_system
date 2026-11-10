import pytest
from ai_engine.normalization.canonical_skills import normalize_skill_name
from ai_engine.extraction.extractor import extractor

def test_canonical_normalization():
    res = normalize_skill_name("py")
    assert res is not None
    canonical, cat, conf = res
    assert canonical == "Python"
    assert cat == "Programming"

    res_k8s = normalize_skill_name("k8s")
    assert res_k8s is not None
    assert res_k8s[0] == "Kubernetes"
    assert res_k8s[1] == "DevOps"

def test_alias_resolution():
    res = normalize_skill_name("Postgres")
    assert res is not None
    assert res[0] == "PostgreSQL"

    res_ts = normalize_skill_name("ts")
    assert res_ts is not None
    assert res_ts[0] == "TypeScript"

def test_skill_extraction_with_snippets():
    text = "Implemented high throughput microservices using FastAPI, Python, and Docker."
    skills = extractor.extract_skills_from_text(text)
    names = [s["canonical_name"] for s in skills]
    assert "FastAPI" in names
    assert "Python" in names
    assert "Docker" in names
    
    # Verify evidence snippets
    fastapi_item = next(s for s in skills if s["canonical_name"] == "FastAPI")
    assert "FastAPI" in fastapi_item["evidence_snippet"]
    assert fastapi_item["confidence"] >= 0.9
