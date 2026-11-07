import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

def test_register_success(client):
    """Test successful user registration."""
    res = client.post("/api/auth/register", json={
        "email": "student@applypilot.ai",
        "password": "SecurePassword123!",
        "full_name": "Arjun Sharma"
    })
    assert res.status_code == 201
    data = res.get_json()
    assert "token" in data
    assert data["user"]["email"] == "student@applypilot.ai"
    assert data["profile"]["full_name"] == "Arjun Sharma"

def test_register_duplicate_email(client):
    """Test duplicate registration error."""
    client.post("/api/auth/register", json={
        "email": "duplicate@applypilot.ai",
        "password": "Password123"
    })
    res = client.post("/api/auth/register", json={
        "email": "duplicate@applypilot.ai",
        "password": "AnotherPassword"
    })
    assert res.status_code == 409
    assert "already exists" in res.get_json()["error"]

def test_register_validation_errors(client):
    """Test validation errors for empty email, invalid email, or short password."""
    # Empty email
    res1 = client.post("/api/auth/register", json={"email": "", "password": "password123"})
    assert res1.status_code == 400

    # Invalid email
    res2 = client.post("/api/auth/register", json={"email": "invalid-email-format", "password": "password123"})
    assert res2.status_code == 400

    # Short password
    res3 = client.post("/api/auth/register", json={"email": "shortpw@applypilot.ai", "password": "123"})
    assert res3.status_code == 400

def test_login_flow(client):
    """Test login with correct and incorrect credentials."""
    # Register first
    client.post("/api/auth/register", json={
        "email": "login_user@applypilot.ai",
        "password": "CorrectPassword123"
    })

    # Wrong password
    bad_res = client.post("/api/auth/login", json={
        "email": "login_user@applypilot.ai",
        "password": "WrongPassword"
    })
    assert bad_res.status_code == 401

    # Right password
    good_res = client.post("/api/auth/login", json={
        "email": "login_user@applypilot.ai",
        "password": "CorrectPassword123"
    })
    assert good_res.status_code == 200
    data = good_res.get_json()
    assert "token" in data
    assert data["user"]["email"] == "login_user@applypilot.ai"

def test_auth_me_and_logout(client):
    """Test /api/auth/me and /api/auth/logout with token."""
    reg = client.post("/api/auth/register", json={
        "email": "me_user@applypilot.ai",
        "password": "Password123"
    })
    token = reg.get_json()["token"]

    # Without token
    no_auth = client.get("/api/auth/me")
    assert no_auth.status_code == 401

    # With token
    auth_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert auth_res.status_code == 200
    assert auth_res.get_json()["user"]["email"] == "me_user@applypilot.ai"

    # Logout
    logout_res = client.post("/api/auth/logout", headers={"Authorization": f"Bearer {token}"})
    assert logout_res.status_code == 200

def test_profile_update_and_retrieval(client):
    """Test updating and reading profile personal details."""
    reg = client.post("/api/auth/register", json={
        "email": "profile_tester@applypilot.ai",
        "password": "Password123"
    })
    token = reg.get_json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    update_res = client.put("/api/profile", json={
        "full_name": "Priya Verma",
        "phone": "+91 9876543210",
        "city": "Bengaluru",
        "state": "Karnataka",
        "linkedin_url": "https://linkedin.com/in/priya-verma",
        "github_url": "https://github.com/priya-verma",
        "graduation_year": 2026,
        "highest_degree": "B.Tech Computer Science"
    }, headers=headers)
    assert update_res.status_code == 200

    get_res = client.get("/api/profile", headers=headers)
    assert get_res.status_code == 200
    p = get_res.get_json()["profile"]
    assert p["full_name"] == "Priya Verma"
    assert p["city"] == "Bengaluru"
    assert p["graduation_year"] == 2026

def test_education_crud(client):
    """Test CRUD operations for education."""
    reg = client.post("/api/auth/register", json={
        "email": "edu_tester@applypilot.ai",
        "password": "Password123"
    })
    headers = {"Authorization": f"Bearer {reg.get_json()['token']}"}

    # Add education
    add_res = client.post("/api/profile/education", json={
        "institution": "National Institute of Technology",
        "degree": "Bachelor of Technology",
        "field_of_study": "Computer Science & Engineering",
        "start_date": "2022",
        "end_date": "2026",
        "gpa": "8.9/10",
        "is_current": True
    }, headers=headers)
    assert add_res.status_code == 201
    edu_id = add_res.get_json()["education"]["id"]

    # Update education
    up_res = client.put(f"/api/profile/education/{edu_id}", json={
        "gpa": "9.1/10"
    }, headers=headers)
    assert up_res.status_code == 200
    assert up_res.get_json()["education"]["gpa"] == "9.1/10"

    # Get profile and verify list
    profile_res = client.get("/api/profile", headers=headers)
    edu_list = profile_res.get_json()["education"]
    assert len(edu_list) == 1
    assert edu_list[0]["institution"] == "National Institute of Technology"

    # Delete education
    del_res = client.delete(f"/api/profile/education/{edu_id}", headers=headers)
    assert del_res.status_code == 200

    # Verify deleted
    profile_res2 = client.get("/api/profile", headers=headers)
    assert len(profile_res2.get_json()["education"]) == 0

def test_skills_and_experience_crud(client):
    """Test CRUD operations for skills and work experience."""
    reg = client.post("/api/auth/register", json={
        "email": "skill_exp@applypilot.ai",
        "password": "Password123"
    })
    headers = {"Authorization": f"Bearer {reg.get_json()['token']}"}

    # Add Skill
    skill_res = client.post("/api/profile/skills", json={
        "skill_name": "Python",
        "category": "Programming Languages",
        "proficiency_level": "Advanced",
        "years_of_experience": 2.5
    }, headers=headers)
    assert skill_res.status_code == 201
    skill_id = skill_res.get_json()["skill"]["id"]

    # Add Experience
    exp_res = client.post("/api/profile/experience", json={
        "company": "Infosys",
        "job_title": "Software Development Intern",
        "location": "Bengaluru, India",
        "start_date": "June 2025",
        "end_date": "August 2025",
        "is_current": False,
        "description": "Developed backend microservices and automated API testing."
    }, headers=headers)
    assert exp_res.status_code == 201
    exp_id = exp_res.get_json()["experience"]["id"]

    # Check profile aggregated view
    full_profile = client.get("/api/profile", headers=headers).get_json()
    assert len(full_profile["skills"]) == 1
    assert full_profile["skills"][0]["skill_name"] == "Python"
    assert len(full_profile["experience"]) == 1
    assert full_profile["experience"][0]["company"] == "Infosys"

    # Delete both
    assert client.delete(f"/api/profile/skills/{skill_id}", headers=headers).status_code == 200
    assert client.delete(f"/api/profile/experience/{exp_id}", headers=headers).status_code == 200

def test_user_data_isolation(client):
    """Ensure User A cannot update or delete User B's profile records."""
    user_a = client.post("/api/auth/register", json={"email": "user_a@applypilot.ai", "password": "Password123"}).get_json()
    user_b = client.post("/api/auth/register", json={"email": "user_b@applypilot.ai", "password": "Password123"}).get_json()

    headers_a = {"Authorization": f"Bearer {user_a['token']}"}
    headers_b = {"Authorization": f"Bearer {user_b['token']}"}

    # User A creates a skill
    skill_a = client.post("/api/profile/skills", json={"skill_name": "React", "category": "Frontend"}, headers=headers_a).get_json()["skill"]

    # User B tries to delete User A's skill
    attack_res = client.delete(f"/api/profile/skills/{skill_a['id']}", headers=headers_b)
    assert attack_res.status_code == 404

    # User A's skill should still exist
    check_a = client.get("/api/profile", headers=headers_a).get_json()
    assert len(check_a["skills"]) == 1
