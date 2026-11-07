import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

def get_auth_headers_with_profile(client, email: str = "elig_test@applypilot.ai") -> dict:
    """Helper to register, set up verified profile/skills/education, and return headers."""
    reg = client.post("/api/auth/register", json={
        "email": email,
        "password": "Password123",
        "full_name": "Rohan Gupta"
    })
    token = reg.get_json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Add Education
    client.post("/api/profile/education", json={
        "institution": "IIT Delhi",
        "degree": "B.Tech Computer Science",
        "field_of_study": "Computer Science",
        "start_date": "2022",
        "end_date": "2026",
        "gpa": "9.2/10",
        "is_current": True
    }, headers=headers)

    # Add Skills
    for skill in ["Python", "React", "TypeScript", "SQL", "Git", "REST"]:
        client.post("/api/profile/skills", json={
            "skill_name": skill,
            "category": "Technical",
            "proficiency_level": "Advanced",
            "years_of_experience": 2.0
        }, headers=headers)

    # Update preferences
    client.put("/api/preferences", json={
        "desired_titles": "Software Engineer, Frontend Developer",
        "desired_locations": "Bengaluru, Remote",
        "fresh_graduate_friendly": True
    }, headers=headers)

    return headers

def test_evaluate_single_high_match_job(client):
    """Test evaluating a high-matching job for a qualified candidate."""
    headers = get_auth_headers_with_profile(client, "high_match@applypilot.ai")
    
    # Run discovery to populate jobs and applications
    client.post("/api/jobs/discover", headers=headers)

    # Find Razorpay or Swiggy job (requires Python/React, Remote/Bengaluru)
    res = client.get("/api/jobs?search=Razorpay", headers=headers)
    jobs = res.get_json()["jobs"]
    assert len(jobs) >= 1
    job_id = jobs[0]["id"]

    # Evaluate eligibility
    eval_res = client.post("/api/eligibility/evaluate", json={"job_id": job_id}, headers=headers)
    assert eval_res.status_code == 200
    evaluation = eval_res.get_json()["evaluation"]

    assert evaluation["match_score"] >= 70
    assert evaluation["relevance_category"] in ["Highly Relevant", "Moderately Relevant"]
    assert evaluation["status"] == "Eligible"
    assert "Python" in evaluation["matched_skills"] or "React" in evaluation["matched_skills"]
    assert "relevance_reason" in evaluation
    assert evaluation["score_breakdown"]["skills"] > 0

def test_evaluate_all_discovered_jobs(client):
    """Test batch evaluating all discovered jobs for a user."""
    headers = get_auth_headers_with_profile(client, "batch_elig@applypilot.ai")
    client.post("/api/jobs/discover", headers=headers)

    batch_res = client.post("/api/eligibility/evaluate", json={}, headers=headers)
    assert batch_res.status_code == 200
    summary = batch_res.get_json()["summary"]

    assert summary["total_evaluated"] > 0
    assert summary["eligible_count"] > 0
    assert len(summary["evaluations"]) == summary["total_evaluated"]

    # Verify that jobs list reflects new statuses
    jobs_res = client.get("/api/jobs", headers=headers)
    for j in jobs_res.get_json()["jobs"]:
        assert j["application_status"] in ["Eligible", "Skipped"]

def test_get_job_eligibility_breakdown(client):
    """Test GET /api/eligibility/:job_id endpoint."""
    headers = get_auth_headers_with_profile(client, "breakdown_user@applypilot.ai")
    client.post("/api/jobs/discover", headers=headers)

    job_id = client.get("/api/jobs?per_page=1", headers=headers).get_json()["jobs"][0]["id"]

    res = client.get(f"/api/eligibility/{job_id}", headers=headers)
    assert res.status_code == 200
    data = res.get_json()["evaluation"]
    assert data["job_id"] == job_id
    assert "score_breakdown" in data
    assert "education" in data["score_breakdown"]
    assert "skills" in data["score_breakdown"]

def test_evaluate_nonexistent_job(client):
    """Evaluating a nonexistent job ID returns 404."""
    headers = get_auth_headers_with_profile(client, "nonexistent@applypilot.ai")
    res = client.post("/api/eligibility/evaluate", json={"job_id": 999999}, headers=headers)
    assert res.status_code == 404
