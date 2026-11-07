# ApplyPilot AI

> **Apply Smarter. Automate Faster. Get Hired.**

ApplyPilot AI is an intelligent, privacy-first job application automation platform designed primarily for Undergraduate (UG) and Postgraduate (PG) students, fresh graduates, and active job seekers.

---

## Architecture Overview

ApplyPilot AI is organized as a modular full-stack application:

- **Frontend (`apps/dashboard`)**:
  - React 19, TypeScript, Vite
  - Tailwind CSS (v4) with custom dark mode theme
  - React Router DOM for SPA routing
  - Axios API client with automatic JWT token attachment
  - Recharts for dynamic visual application and automation metrics
  - Lucide React icons
- **Backend (`backend`)**:
  - Python 3.13 + Flask application factory architecture
  - SQLAlchemy 2.0 ORM with 14 comprehensive relational models
  - SQLite (with seamless PostgreSQL support)
  - Flask-CORS for secure cross-origin communication with frontend and extensions
  - Modular services: Authentication, Profile, Resume processing, Job discovery, Eligibility evaluation, Playwright automation, Screening question answering
- **Storage (`storage/`)**:
  - Secure resume file storage (`storage/resumes`)
  - Automation session activity logs (`storage/logs`)

---

## Getting Started

### 1. Prerequisites
- **Python 3.10+** (Python 3.13 recommended)
- **Node.js LTS** (v20+ or v26+) & npm

### 2. Backend Setup
```bash
cd backend
python -m pip install -r requirements.txt
python run.py
```
Backend API will start at `http://localhost:5000`.
Health endpoint: `http://localhost:5000/api/health`

### 3. Frontend Setup
```bash
cd apps/dashboard
npm install
npm run dev
```
Dashboard will be accessible at `http://localhost:5173`.

### 4. Running Tests
```bash
pytest backend/tests
```
# ApplyPilot-AI
