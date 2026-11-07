import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

def get_auth_headers(client, email: str = "discover_tester@applypilot.ai") -> dict:
    """Helper to register and return authorization headers."""
    reg = client.post("/api/auth/register", json={
        "email": email,
        "password": "Password123",
        "full_name": "Discovery Tester"
    })
    token = reg.get_json()["token"]
    return {"Authorization": f"Bearer {token}"}

def test_trigger_job_discovery(client):
    """Test running on-demand job discovery."""
    headers = get_auth_headers(client, "disc_run@applypilot.ai")
    res = client.post("/api/jobs/discover", headers=headers)
    assert res.status_code == 200
    data = res.get_json()
    assert data["message"] == "Job discovery completed successfully"
    assert data["stats"]["new_jobs_stored"] > 0
    assert data["stats"]["new_applications_linked"] > 0

def test_job_discovery_deduplication(client):
    """Test that running discovery repeatedly does not produce duplicate jobs."""
    headers = get_auth_headers(client, "dedup_test@applypilot.ai")
    
    # Run 1
    res1 = client.post("/api/jobs/discover", headers=headers)
    assert res1.status_code == 200
    
    # Run 2 immediately
    res2 = client.post("/api/jobs/discover", headers=headers)
    assert res2.status_code == 200
    stats2 = res2.get_json()["stats"]
    # No new jobs or applications should be duplicated
    assert stats2["new_jobs_stored"] == 0
    assert stats2["new_applications_linked"] == 0

def test_blacklist_filtering(client):
    """Test that blacklisted companies are omitted from user's discovery results."""
    headers = get_auth_headers(client, "blacklist_user@applypilot.ai")

    # Blacklist Swiggy and Amazon
    client.put("/api/preferences", json={"companies_blacklist": "Swiggy, Amazon"}, headers=headers)

    # Run discovery
    client.post("/api/jobs/discover", headers=headers)

    # Fetch user's jobs
    res = client.get("/api/jobs?per_page=50", headers=headers)
    jobs = res.get_json()["jobs"]
    companies = [j["company"].lower() for j in jobs]

    assert not any("swiggy" in c for c in companies)
    assert not any("amazon" in c for c in companies)

def test_whitelist_prioritization(client):
    """Test that whitelisted companies receive Highly Relevant category."""
    headers = get_auth_headers(client, "whitelist_user@applypilot.ai")

    # Whitelist Razorpay
    client.put("/api/preferences", json={"companies_whitelist": "Razorpay"}, headers=headers)

    # Run discovery
    client.post("/api/jobs/discover", headers=headers)

    # Check Razorpay job
    res = client.get("/api/jobs?search=Razorpay", headers=headers)
    jobs = res.get_json()["jobs"]
    assert len(jobs) >= 1
    assert jobs[0]["relevance_category"] == "Highly Relevant"

def test_list_and_search_jobs(client):
    """Test search query, source filtering, and pagination on /api/jobs."""
    headers = get_auth_headers(client, "search_user@applypilot.ai")
    client.post("/api/jobs/discover", headers=headers)

    # Search by keyword
    search_res = client.get("/api/jobs?search=Python", headers=headers)
    assert search_res.status_code == 200
    jobs = search_res.get_json()["jobs"]
    assert len(jobs) > 0
    assert any("python" in (j["title"] + j["description"]).lower() for j in jobs)

    # Filter by source: LinkedIn
    source_res = client.get("/api/jobs?source=linkedin", headers=headers)
    assert source_res.status_code == 200
    linkedin_jobs = source_res.get_json()["jobs"]
    assert all(j["source"] == "linkedin" for j in linkedin_jobs)

    # Pagination
    page_res = client.get("/api/jobs?page=1&per_page=3", headers=headers)
    assert page_res.status_code == 200
    page_data = page_res.get_json()
    assert len(page_data["jobs"]) <= 3
    assert page_data["page"] == 1

def test_get_single_job_details(client):
    """Test retrieving full details of a specific job."""
    headers = get_auth_headers(client, "details_user@applypilot.ai")
    client.post("/api/jobs/discover", headers=headers)

    list_res = client.get("/api/jobs?per_page=1", headers=headers)
    job_id = list_res.get_json()["jobs"][0]["id"]

    detail_res = client.get(f"/api/jobs/{job_id}", headers=headers)
    assert detail_res.status_code == 200
    job_data = detail_res.get_json()["job"]
    assert job_data["id"] == job_id
    assert "description" in job_data
    assert "requirements" in job_data
    assert job_data["application"]["status"] == "Discovered"
