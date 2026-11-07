import sys
from io import BytesIO
from pathlib import Path
import pypdf
import docx

backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

def create_sample_pdf_bytes(text: str = "Candidate Resume Content") -> BytesIO:
    """Generate a valid PDF file in memory."""
    writer = pypdf.PdfWriter()
    page = writer.add_blank_page(width=300, height=300)
    # We can also add an annotation or text or just a valid PDF page
    buf = BytesIO()
    writer.write(buf)
    buf.seek(0)
    return buf

def create_sample_docx_bytes(content: str = "Arjun Sharma\nEmail: arjun@example.com\nPhone: 9876543210") -> BytesIO:
    """Generate a valid DOCX file in memory."""
    doc = docx.Document()
    for line in content.split("\n"):
        doc.add_paragraph(line)
    buf = BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf

def get_auth_headers(client, email: str = "resume_test@applypilot.ai") -> dict:
    """Helper to register and return authorization headers."""
    reg = client.post("/api/auth/register", json={
        "email": email,
        "password": "Password123",
        "full_name": "Resume Tester"
    })
    token = reg.get_json()["token"]
    return {"Authorization": f"Bearer {token}"}

def test_upload_docx_resume(client):
    """Test uploading a valid DOCX resume and extracting text."""
    headers = get_auth_headers(client, "docx_user@applypilot.ai")
    docx_file = create_sample_docx_bytes("Arjun Sharma\nEmail: arjun@example.com\nSkills: Python, React, Flask")

    data = {
        "resume": (docx_file, "resume.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    }
    res = client.post("/api/resumes/upload", data=data, content_type="multipart/form-data", headers=headers)
    assert res.status_code == 201
    payload = res.get_json()
    assert payload["resume"]["filename"] == "resume.docx"
    assert payload["resume"]["is_primary"] is True
    assert "Python" in payload["resume"]["parsed_text"]
    assert "arjun@example.com" in payload["meta"]["detected_emails"]

def test_upload_pdf_resume(client):
    """Test uploading a valid PDF resume."""
    headers = get_auth_headers(client, "pdf_user@applypilot.ai")
    pdf_file = create_sample_pdf_bytes()

    data = {
        "resume": (pdf_file, "sample_cv.pdf", "application/pdf")
    }
    res = client.post("/api/resumes/upload", data=data, content_type="multipart/form-data", headers=headers)
    assert res.status_code == 201
    payload = res.get_json()
    assert payload["resume"]["filename"] == "sample_cv.pdf"
    assert payload["resume"]["file_type"] == "pdf"
    assert payload["resume"]["is_primary"] is True

def test_upload_invalid_file_type(client):
    """Test that non-PDF and non-DOCX files are rejected."""
    headers = get_auth_headers(client, "invalid_ext_user@applypilot.ai")
    fake_exe = BytesIO(b"MZ executable header")
    data = {
        "resume": (fake_exe, "virus.exe", "application/octet-stream")
    }
    res = client.post("/api/resumes/upload", data=data, content_type="multipart/form-data", headers=headers)
    assert res.status_code == 400
    assert "Only PDF" in res.get_json()["error"]

def test_upload_without_file(client):
    """Test request without a file."""
    headers = get_auth_headers(client, "nofile_user@applypilot.ai")
    res = client.post("/api/resumes/upload", data={}, content_type="multipart/form-data", headers=headers)
    assert res.status_code == 400

def test_list_and_primary_toggle(client):
    """Test uploading multiple resumes and setting primary resume."""
    headers = get_auth_headers(client, "multi_resume@applypilot.ai")

    # Upload resume 1
    f1 = create_sample_docx_bytes("Resume 1")
    r1 = client.post("/api/resumes/upload", data={"resume": (f1, "cv1.docx")}, content_type="multipart/form-data", headers=headers).get_json()["resume"]
    assert r1["is_primary"] is True

    # Upload resume 2
    f2 = create_sample_docx_bytes("Resume 2")
    r2 = client.post("/api/resumes/upload", data={"resume": (f2, "cv2.docx")}, content_type="multipart/form-data", headers=headers).get_json()["resume"]
    assert r2["is_primary"] is False

    # List
    list_res = client.get("/api/resumes", headers=headers)
    assert list_res.status_code == 200
    resumes = list_res.get_json()["resumes"]
    assert len(resumes) == 2

    # Set resume 2 as primary
    toggle_res = client.put(f"/api/resumes/{r2['id']}/primary", headers=headers)
    assert toggle_res.status_code == 200
    assert toggle_res.get_json()["resume"]["is_primary"] is True

    # Check that resume 1 is no longer primary
    r1_check = client.get(f"/api/resumes/{r1['id']}", headers=headers).get_json()["resume"]
    assert r1_check["is_primary"] is False

def test_delete_resume(client):
    """Test deleting resume cleans up record and physical file."""
    headers = get_auth_headers(client, "delete_resume_user@applypilot.ai")
    f = create_sample_docx_bytes("Resume to be deleted")
    uploaded = client.post("/api/resumes/upload", data={"resume": (f, "delete_me.docx")}, content_type="multipart/form-data", headers=headers).get_json()["resume"]

    del_res = client.delete(f"/api/resumes/{uploaded['id']}", headers=headers)
    assert del_res.status_code == 200

    # Ensure get returns 404
    get_res = client.get(f"/api/resumes/{uploaded['id']}", headers=headers)
    assert get_res.status_code == 404

def test_resume_isolation(client):
    """User B cannot view, modify primary, or delete User A's resume."""
    headers_a = get_auth_headers(client, "user_a_cv@applypilot.ai")
    headers_b = get_auth_headers(client, "user_b_cv@applypilot.ai")

    f = create_sample_docx_bytes("Secret Resume of User A")
    res_a = client.post("/api/resumes/upload", data={"resume": (f, "secret_a.docx")}, content_type="multipart/form-data", headers=headers_a).get_json()["resume"]

    # User B tries to view
    assert client.get(f"/api/resumes/{res_a['id']}", headers=headers_b).status_code == 404

    # User B tries to set primary
    assert client.put(f"/api/resumes/{res_a['id']}/primary", headers=headers_b).status_code == 404

    # User B tries to delete
    assert client.delete(f"/api/resumes/{res_a['id']}", headers=headers_b).status_code == 404
