import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.models import User, UserProfile, JobPreference, AutomationSetting, Job, Application

def test_health_check(client):
    """Test health check route."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ok"
    assert data["service"] == "ApplyPilot AI Backend"
    assert data["database"] == "healthy"

def test_database_models_creation(db_session):
    """Test creating user and related models."""
    user = User(email="pilot_test@applypilot.ai", password_hash="hashed_pw_test")
    db_session.add(user)
    db_session.commit()

    assert user.id is not None
    assert user.email == "pilot_test@applypilot.ai"

    # Profile
    profile = UserProfile(user_id=user.id, full_name="John Doe", highest_degree="B.Tech")
    db_session.add(profile)

    # Job Preferences
    prefs = JobPreference(user_id=user.id, desired_titles="Software Engineer", fresh_graduate_friendly=True)
    db_session.add(prefs)

    # Automation Setting
    setting = AutomationSetting(user_id=user.id, max_applications_per_session=10)
    db_session.add(setting)

    # Job & Application
    job = Job(
        title="Frontend Engineer",
        company="TechCorp",
        location="Remote",
        external_job_url="https://techcorp.jobs/123",
    )
    db_session.add(job)
    db_session.commit()

    app_record = Application(
        user_id=user.id,
        job_id=job.id,
        status="Discovered",
        relevance_category="Highly Relevant",
    )
    db_session.add(app_record)
    db_session.commit()

    assert profile.id is not None
    assert prefs.id is not None
    assert setting.id is not None
    assert job.id is not None
    assert app_record.id is not None
    assert app_record.user.email == "pilot_test@applypilot.ai"
    assert app_record.job.company == "TechCorp"
