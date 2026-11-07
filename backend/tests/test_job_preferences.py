import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

def get_auth_headers(client, email: str = "prefs_test@applypilot.ai") -> dict:
    """Helper to register and return authorization headers."""
    reg = client.post("/api/auth/register", json={
        "email": email,
        "password": "Password123",
        "full_name": "Preference User"
    })
    token = reg.get_json()["token"]
    return {"Authorization": f"Bearer {token}"}

def test_get_default_preferences(client):
    """Test retrieving automatically initialized default preferences."""
    headers = get_auth_headers(client, "default_pref@applypilot.ai")
    res = client.get("/api/preferences", headers=headers)
    assert res.status_code == 200
    prefs = res.get_json()["preferences"]
    assert "Software Engineer" in prefs["desired_titles"]
    assert "Remote" in prefs["desired_locations"]
    assert prefs["fresh_graduate_friendly"] is True
    assert prefs["experience_level"] == "entry"

def test_update_preferences(client):
    """Test updating all preference filters."""
    headers = get_auth_headers(client, "update_pref@applypilot.ai")
    
    update_data = {
        "desired_titles": "AI Engineer, Python Developer, Machine Learning Intern",
        "desired_locations": "Bengaluru, Hyderabad, Remote",
        "remote_preference": "remote",
        "min_salary": 600000,
        "employment_types": "full-time, internship",
        "experience_level": "entry",
        "fresh_graduate_friendly": True,
        "skills_filter": "Python, PyTorch, FastAPI, React",
        "companies_whitelist": "Google, Microsoft, Amazon",
        "companies_blacklist": "Revature, Infosys"
    }
    
    res = client.put("/api/preferences", json=update_data, headers=headers)
    assert res.status_code == 200
    updated = res.get_json()["preferences"]
    assert updated["desired_titles"] == update_data["desired_titles"]
    assert updated["remote_preference"] == "remote"
    assert updated["min_salary"] == 600000
    assert updated["companies_whitelist"] == "Google, Microsoft, Amazon"
    assert updated["companies_blacklist"] == "Revature, Infosys"

def test_update_preferences_with_arrays(client):
    """Test updating preferences using array inputs for titles and locations."""
    headers = get_auth_headers(client, "array_pref@applypilot.ai")

    update_data = {
        "desired_titles": ["Frontend Engineer", "React Developer"],
        "desired_locations": ["Pune", "Mumbai"],
        "remote_preference": "hybrid",
        "min_salary": -500 # Should be clamped to 0
    }

    res = client.put("/api/preferences", json=update_data, headers=headers)
    assert res.status_code == 200
    updated = res.get_json()["preferences"]
    assert updated["desired_titles"] == "Frontend Engineer, React Developer"
    assert updated["desired_locations"] == "Pune, Mumbai"
    assert updated["remote_preference"] == "hybrid"
    assert updated["min_salary"] == 0

def test_preferences_user_isolation(client):
    """Ensure User A and User B maintain isolated preferences."""
    headers_a = get_auth_headers(client, "pref_user_a@applypilot.ai")
    headers_b = get_auth_headers(client, "pref_user_b@applypilot.ai")

    # User A updates preferences
    client.put("/api/preferences", json={"desired_titles": "Data Scientist"}, headers=headers_a)

    # User B checks preferences
    prefs_b = client.get("/api/preferences", headers=headers_b).get_json()["preferences"]
    assert "Data Scientist" != prefs_b["desired_titles"]
    assert "Software Engineer" in prefs_b["desired_titles"]
