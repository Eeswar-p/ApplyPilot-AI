# ApplyPilot AI — Phase 4: Job Preferences Report

## Executive Summary
Phase 4 (Job Preferences) has been implemented, tested, and integrated. Candidates can configure their target job titles, preferred geographical locations, workplace modes (remote, hybrid, onsite, any), experience levels, minimum salary thresholds in INR, opportunity types (full-time, internship), and dedicated fresh graduate filters. Crucially, companies can be selectively prioritized via a whitelist or automatically excluded via a blacklist. On the frontend, we created `src/pages/JobPreferences.tsx` with interactive role pills, city suggestions, salary presets, and a fresh graduate feature spotlight.

---

## 1. Modules Implemented

### REST API Endpoints (`backend/app/routes/preferences.py`)
- **`GET /api/preferences`**:
  - Authenticated endpoint returning candidate's configured job search preferences.
  - Automatically seeds recommended default preferences if non-existent.
- **`PUT /api/preferences`**:
  - Updates preference filters:
    - `desired_titles`: Target titles with string or list normalization.
    - `desired_locations`: Preferred job cities with normalization.
    - `remote_preference`: Validates choice between `remote`, `hybrid`, `onsite`, and `any`.
    - `min_salary`: Minimum baseline annual compensation (clamped to >= 0).
    - `employment_types`: Filters for full-time, internship, etc.
    - `experience_level`: Level target (`entry`, `mid`, `senior`, `any`).
    - `fresh_graduate_friendly`: Boolean flag activating college graduate optimizations.
    - `skills_filter`: Comma-separated keywords required in job descriptions.
    - `companies_whitelist`: Priority target companies.
    - `companies_blacklist`: Excluded companies to be skipped during discovery.
  - Returns updated `JobPreference` object with strict user isolation.

### Frontend Integration (`apps/dashboard/src/pages/JobPreferences.tsx`)
- **Fresh Graduate Friendly Spotlight**: Highlighted card with a toggle switch that directs the automation engine to focus on roles with 0–2 years experience and filter out unrealistic requirements.
- **Target Role Selector**: Comma-separated tag editor with quick-add chips (e.g. Software Engineer, React Developer, Full Stack, Python, AI/ML).
- **Location Selector**: Geographical filter with Indian tech hub suggestions (Bengaluru, Hyderabad, Pune, Mumbai, Delhi NCR, Remote).
- **Workplace Mode Grid**: Visual cards for Remote Only, Hybrid, Onsite, and Any Mode.
- **Salary / Compensation Configuration**: Numeric input with INR presets (₹3 LPA, ₹5 LPA, ₹8 LPA, ₹12 LPA).
- **Company Whitelist & Blacklist**: Dedicated sections for preferred and excluded employers.
- **App Routing**: Integrated under `/preferences` with automatic protection in `DashboardLayout.tsx`.

---

## 2. Verification & Test Results

### Automated Backend Test Suite
Command:
```bash
pytest backend/tests -v
```
Test Results:
- `test_get_default_preferences`: **PASSED** (verifies default creation upon account setup)
- `test_update_preferences`: **PASSED** (verifies updating all preference fields)
- `test_update_preferences_with_arrays`: **PASSED** (verifies array input normalization and negative salary clamp)
- `test_preferences_user_isolation`: **PASSED** (verifies User A and User B preferences remain completely separated)
- All 20 previous tests for Foundation, Auth, Profile, and Resumes: **PASSED**
- **Total: 24 passed in 14.75s (100% pass rate)**

### Frontend Production Build
Command:
```bash
npm run build
```
- TypeScript check: **0 errors**
- Vite production bundle: **Built successfully in 3.03s**
