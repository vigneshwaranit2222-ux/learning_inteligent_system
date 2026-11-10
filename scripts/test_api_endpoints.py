import sys
import os

sys.path.insert(0, os.path.abspath("backend"))
sys.path.insert(0, os.path.abspath("."))

from fastapi.testclient import TestClient
from app.main import app

def main():
    print("Testing with client = TestClient(app)...")
    client = TestClient(app)
    
    print("Testing /health...")
    res = client.get("/health")
    print("Health response:", res.status_code, res.json())
    assert res.status_code == 200

    print("Testing /api/v1/auth/login...")
    res = client.post("/api/v1/auth/login", json={"email": "admin@intelligence.system", "password": "AdminPass123!"})
    print("Login status code:", res.status_code)
    assert res.status_code == 200
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    print("Testing /api/v1/skills/...")
    res = client.get("/api/v1/skills/", headers=headers)
    skills = res.json()
    print("Skills count:", len(skills))
    assert res.status_code == 200

    print("Testing /api/v1/jobs/...")
    res = client.get("/api/v1/jobs/", headers=headers)
    jobs = res.json()
    print("Jobs count:", len(jobs))
    assert res.status_code == 200

    print("Testing /api/v1/courses/...")
    res = client.get("/api/v1/courses/", headers=headers)
    courses = res.json()
    print("Courses count:", len(courses))
    assert res.status_code == 200

    print("All API endpoint checks passed successfully!")

if __name__ == "__main__":
    main()
