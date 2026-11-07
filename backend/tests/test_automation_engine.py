import pytest
from app.models.user import User
from app.models.profile import UserProfile, Skill, Education
from app.models.screening import SavedAnswer
from app.models.automation import AutomationSetting
from app.utils.security import generate_token
from app.question_handler.matcher import ScreeningQuestionHandler
from app.automation.filler import FormFiller
from app.automation.form_scanner import FormFieldDescriptor

@pytest.fixture
def auth_headers(client, db_session):
    user = User(email="automator@applypilot.test")
    user.set_password("PilotAutoSecure123!")
    db_session.add(user)
    db_session.commit()
    token = generate_token(user.id, user.email)
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }, user

def test_automation_settings_get_and_put(client, auth_headers):
    headers, user = auth_headers

    # GET default settings
    resp = client.get("/api/automation/settings", headers=headers)
    assert resp.status_code == 200
    data = resp.get_json()
    assert "settings" in data
    assert data["settings"]["max_applications_per_session"] == 15

    # PUT updated settings
    update_resp = client.put("/api/automation/settings", headers=headers, json={
        "max_applications_per_session": 25,
        "application_delay_seconds": 8,
        "require_approval": True,
        "target_platforms": "linkedin,indeed"
    })
    assert update_resp.status_code == 200
    updated = update_resp.get_json()["settings"]
    assert updated["max_applications_per_session"] == 25
    assert updated["application_delay_seconds"] == 8
    assert updated["require_approval"] is True

def test_automation_status_and_logs(client, auth_headers):
    headers, user = auth_headers
    resp = client.get("/api/automation/status", headers=headers)
    assert resp.status_code == 200
    data = resp.get_json()
    assert "is_running" in data
    assert data["is_running"] is False

    logs_resp = client.get("/api/automation/logs", headers=headers)
    assert logs_resp.status_code == 200
    logs = logs_resp.get_json()["logs"]
    assert isinstance(logs, list)

def test_automation_pause_resume_stop_endpoints(client, auth_headers):
    headers, user = auth_headers

    pause_resp = client.post("/api/automation/pause", headers=headers)
    assert pause_resp.status_code == 200

    resume_resp = client.post("/api/automation/resume", headers=headers)
    assert resume_resp.status_code == 200

    stop_resp = client.post("/api/automation/stop", headers=headers)
    assert stop_resp.status_code == 200

def test_screening_question_handler_factual_answers(db_session):
    user = User(email="candidate@test.com")
    db_session.add(user)
    db_session.commit()

    profile = UserProfile(
        user_id=user.id,
        full_name="Eshwar Rao",
        phone="+91 9876543210",
        current_location="Hyderabad, India",
        highest_degree="Bachelor of Technology in Computer Science",
        graduation_year=2025
    )
    skill1 = Skill(user_id=user.id, skill_name="Python", proficiency="Advanced", years_of_experience=2.0)
    skill2 = Skill(user_id=user.id, skill_name="React", proficiency="Intermediate", years_of_experience=1.5)
    saved_answer = SavedAnswer(
        user_id=user.id,
        question_pattern="notice period",
        answer_text="Immediate / Under 15 days"
    )
    db_session.add_all([profile, skill1, skill2, saved_answer])
    db_session.commit()

    handler = ScreeningQuestionHandler(db_session, user.id)

    # 1. Custom saved answer test
    ans, conf, src = handler.answer_question("What is your current notice period?")
    assert "Immediate" in ans
    assert conf == 1.0

    # 2. Degree test
    ans, conf, src = handler.answer_question("Highest qualification attained?")
    assert ans == "Bachelor of Technology in Computer Science"
    assert conf >= 0.90

    # 3. Work Authorization test
    ans, conf, src = handler.answer_question("Are you legally authorized to work in India?")
    assert ans == "Yes"

    # 4. Specific skill experience test
    ans, conf, src = handler.answer_question("How many years of Python experience do you have?")
    assert ans == "2"

def test_form_filler_field_mapping(db_session):
    user = User(email="testpilot@example.com")
    profile = UserProfile(
        user_id=user.id,
        full_name="Alex Mercer",
        phone="+1 555-0199",
        current_location="Seattle, WA",
        linkedin_url="https://linkedin.com/in/alexmercer"
    )
    db_session.add_all([user, profile])
    db_session.commit()

    handler = ScreeningQuestionHandler(db_session, user.id)
    filler = FormFiller(
        page=None,
        user=user,
        profile=profile,
        primary_resume=None,
        question_handler=handler
    )

    f_email = FormFieldDescriptor("1", "email", "text", "Your Email Address")
    assert filler._get_candidate_value_for_field(f_email) == "testpilot@example.com"

    f_name = FormFieldDescriptor("2", "fullName", "text", "Full Name")
    assert filler._get_candidate_value_for_field(f_name) == "Alex Mercer"

    f_phone = FormFieldDescriptor("3", "phone", "tel", "Mobile Phone")
    assert filler._get_candidate_value_for_field(f_phone) == "+1 555-0199"

    f_linkedin = FormFieldDescriptor("4", "linkedin", "text", "LinkedIn Profile URL")
    assert filler._get_candidate_value_for_field(f_linkedin) == "https://linkedin.com/in/alexmercer"
