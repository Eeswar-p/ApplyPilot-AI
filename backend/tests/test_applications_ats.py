import pytest
from app.models.user import User
from app.models.job import Job
from app.models.application import Application
from app.utils.security import generate_token

@pytest.fixture
def auth_headers(client, db_session):
    user = User(email="applicant@applypilot.test")
    user.set_password("SecureApplicantPass123!")
    db_session.add(user)
    db_session.commit()
    token = generate_token(user.id, user.email)
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }, user

@pytest.fixture
def sample_jobs_and_applications(db_session, auth_headers):
    headers, user = auth_headers

    job1 = Job(
        title="Frontend Developer",
        company="TechCorp",
        location="Bangalore",
        source="linkedin",
        job_url="https://linkedin.com/jobs/view/1001",
        description="React and TypeScript role"
    )
    job2 = Job(
        title="Python Backend Engineer",
        company="CloudScale",
        location="Remote",
        source="indeed",
        job_url="https://indeed.com/viewjob?jk=2002",
        description="Flask and SQL automation"
    )
    db_session.add_all([job1, job2])
    db_session.commit()

    app1 = Application(
        user_id=user.id,
        job_id=job1.id,
        status="Discovered",
        match_score=85,
        relevance_category="Highly Relevant"
    )
    app2 = Application(
        user_id=user.id,
        job_id=job2.id,
        status="Pending Approval",
        match_score=92,
        relevance_category="Highly Relevant"
    )
    db_session.add_all([app1, app2])
    db_session.commit()

    return user, [job1, job2], [app1, app2]

def test_get_applications_list(client, auth_headers, sample_jobs_and_applications):
    headers, user = auth_headers
    resp = client.get("/api/applications", headers=headers)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["total"] == 2
    assert len(data["applications"]) == 2

def test_filter_applications_by_status(client, auth_headers, sample_jobs_and_applications):
    headers, user = auth_headers
    resp = client.get("/api/applications?status=Pending Approval", headers=headers)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["total"] == 1
    assert data["applications"][0]["status"] == "Pending Approval"
    assert data["applications"][0]["job"]["company"] == "CloudScale"

def test_update_application_status(client, auth_headers, sample_jobs_and_applications):
    headers, user = auth_headers
    _, _, apps = sample_jobs_and_applications
    app_id = apps[0].id

    # Update to Interview
    resp = client.put(f"/api/applications/{app_id}/status", headers=headers, json={
        "status": "Interview"
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["application"]["status"] == "Interview"

    # Invalid status rejection
    invalid_resp = client.put(f"/api/applications/{app_id}/status", headers=headers, json={
        "status": "NonExistentStatus"
    })
    assert invalid_resp.status_code == 400

def test_approve_application(client, auth_headers, sample_jobs_and_applications):
    headers, user = auth_headers
    _, _, apps = sample_jobs_and_applications
    pending_app = apps[1] # "Pending Approval"

    resp = client.post(f"/api/applications/{pending_app.id}/approve", headers=headers)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["application"]["status"] == "Applied"
    assert data["application"]["applied_at"] is not None

def test_application_stats_calculation(client, auth_headers, sample_jobs_and_applications):
    headers, user = auth_headers
    resp = client.get("/api/applications/stats", headers=headers)
    assert resp.status_code == 200
    stats = resp.get_json()
    assert stats["total_discovered"] == 2
    assert stats["pending_approval"] == 1
    assert "by_platform" in stats
    assert len(stats["recent_activity"]) == 2
