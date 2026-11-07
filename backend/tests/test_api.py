import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

def test_api_health_check(client):
    """Integration test for /api/health."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ok"
    assert data["database"] == "healthy"

def test_api_auth_and_profile_flow(client):
    """End-to-end integration test of registration, login, and profile retrieval."""
    # 1. Register
    reg_res = client.post(
        "/api/auth/register",
        json={"email": "integration@applypilot.ai", "password": "password123", "full_name": "Integration User"}
    )
    assert reg_res.status_code == 201
    reg_data = reg_res.get_json()
    assert "token" in reg_data

    # 2. Login
    login_res = client.post(
        "/api/auth/login",
        json={"email": "integration@applypilot.ai", "password": "password123"}
    )
    assert login_res.status_code == 200
    token = login_res.get_json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Get profile
    profile_res = client.get("/api/profile", headers=headers)
    assert profile_res.status_code == 200
    profile_data = profile_res.get_json()
    assert profile_data["profile"]["full_name"] == "Integration User"
