# Deployment Guide: AI-Powered Learning-to-Career Intelligence System

This guide covers deployment procedures for local development and containerized multi-service production environments using Docker and Docker Compose.

---

## 1. Quick Start with Docker Compose (Recommended for Production)

### Prerequisites
- Docker Engine 24.0+
- Docker Compose v2.20+

### Steps
1. Clone the repository and configure environment:
   ```bash
   cp .env.example .env
   ```
2. Build and launch all services:
   ```bash
   docker compose up -d --build
   ```
3. Verify running containers:
   ```bash
   docker compose ps
   ```
   Services running:
   - `career_intel_db` (PostgreSQL 16) on port `5432`
   - `career_intel_redis` (Redis 7) on port `6379`
   - `career_intel_backend` (FastAPI) on port `8000`
   - `career_intel_frontend` (React + Nginx) on port `80`

4. Access the application:
   - Web Application: `http://localhost`
   - Backend Swagger API Docs: `http://localhost:8000/docs`

---

## 2. Local Development Setup (Windows / Linux / macOS)

### Backend Setup
1. Create and activate a Python virtual environment:
   ```bash
   python -m venv .venv
   # Windows PowerShell:
   .venv\Scripts\Activate.ps1
   # Linux/macOS:
   source .venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r backend/requirements.txt
   python -m spacy download en_core_web_sm
   ```
3. Initialize the database and seed master taxonomy:
   ```bash
   python scripts/seed_database.py
   ```
4. Start the backend development server:
   ```bash
   cd backend
   uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   ```

### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   npm install
   ```
2. Start the Vite development server:
   ```bash
   npm run dev
   ```
3. Open `http://localhost:5173` in your browser.

---

## 3. Automated Testing & Verification Commands

### Execute Pytest Backend Suite
```bash
python -m pytest
```

### Run Direct Full-Pipeline Verification Script
```bash
python scripts/test_direct_endpoints.py
```

### Run Ground-Truth Evaluation Benchmark
```bash
python scripts/run_evaluation.py
```
Outputs formal evaluation metrics to `docs/evaluation_report.md`.

---

## 4. Default Seeded Credentials

| Role | Email Address | Password |
| :--- | :--- | :--- |
| **Administrator** | `admin@intelligence.system` | `AdminPass123!` |
| **Demo Learner** | `learner@intelligence.system` | `LearnerPass123!` |
