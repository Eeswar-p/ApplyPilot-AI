# ApplyPilot AI — Phase 5: Job Discovery Engine Report

## Executive Summary
Phase 5 (Job Discovery Engine) has been fully built, tested, and integrated. We implemented a multi-platform discovery architecture that discovers opportunities across LinkedIn, Indeed, Internshala, and Verified Career Portals. The engine canonicalizes and deduplicates URLs, extracts structured opportunity attributes, applies candidate preference filters (including fresh-graduate gating, blacklist rejection, and whitelist prioritization), stores opportunities into the `jobs` table, and automatically links application records with `Discovered` status. On the frontend, we developed `src/pages/JobDiscovery.tsx` featuring on-demand discovery execution, cross-platform filtering, opportunity cards, and full-detail job inspection modals.

---

## 1. Modules Implemented

### Job Discovery Engine Service (`backend/app/services/discovery.py`)
- **Multi-Platform Adapters**:
  - **LinkedIn**: Technical entry & mid-level postings, Easy Apply indicators.
  - **Internshala**: High-match internships and fresher engineering openings.
  - **Indeed**: Broad entry-level developer and analyst roles.
  - **Career Portals**: Direct enterprise career feeds (Razorpay, TCS, Swiggy, Amazon, Zomato, PhonePe, Jio, Fractal, Microsoft).
- **Attribute Extraction Pipeline**: Extracts `title`, `company`, `location`, `employment_type`, `experience_required`, `description`, `requirements`, `salary_range`, `source`, `external_job_url`, and `application_method`.
- **URL Canonicalization & Deduplication**: Strips tracking queries (`utm_*`, `ref`, etc.) to obtain clean canonical URLs. Prevents duplicate storage in `jobs` and ensures duplicate applications are never created for the same user.
- **Filtering Logic**:
  - Enforces `companies_blacklist` (skips excluded employers).
  - Enforces `fresh_graduate_friendly` (filters out positions requiring 3+ or 5+ years of experience).
  - Flags `companies_whitelist` matches as `Highly Relevant`.

### REST API Endpoints (`backend/app/routes/jobs.py`)
- **`POST /api/jobs/discover`**:
  - Triggers the multi-platform discovery engine on-demand for the current authenticated user.
  - Returns statistics: total evaluated feeds, new jobs stored, and new applications linked.
- **`GET /api/jobs`**:
  - Returns paginated jobs matching the candidate's discovery history.
  - Filter by keyword search across title, company, location, and requirements.
  - Filter by platform source (`linkedin`, `indeed`, `internshala`, `portal`, or `all`).
  - Filter by opportunity type (`full-time`, `internship`).
  - Injects candidate's application status (`Discovered`, `Eligible`, `Applied`, etc.).
- **`GET /api/jobs/<int:id>`**:
  - Returns full job details, compensation range, role overview, qualification requirements, and linked application record.

### Frontend Integration (`apps/dashboard/src/pages/JobDiscovery.tsx`)
- **Interactive Discovery Trigger**: "Run Discovery Scan" button with spinning radar indicators and summary alerts.
- **Multi-Platform Filter Tabs**: One-click switching between All Platforms, LinkedIn, Internshala, Indeed, and Portals.
- **Opportunity Cards**: Visual indicators for platform source, compensation in INR, experience requirement, top match badge, and application state.
- **Job Details Modal**: Deep inspection dialog with role overview, requirements, and direct external platform links.
- **Route Navigation**: Accessible at `/discovery` in `App.tsx` and linked from the sidebar in `DashboardLayout.tsx`.

---

## 2. Verification & Test Results

### Automated Backend Test Suite
Command:
```bash
pytest backend/tests -v
```
Test Results:
- `test_trigger_job_discovery`: **PASSED** (verifies discovery execution and job/application linking)
- `test_job_discovery_deduplication`: **PASSED** (verifies subsequent discovery runs yield 0 duplicates)
- `test_blacklist_filtering`: **PASSED** (verifies blacklisted employers are excluded)
- `test_whitelist_prioritization`: **PASSED** (verifies whitelisted employers receive Highly Relevant rating)
- `test_list_and_search_jobs`: **PASSED** (verifies keyword search, source filtering, and pagination)
- `test_get_single_job_details`: **PASSED** (verifies single job detail endpoint and application link)
- All 24 previous tests for Foundation, Auth, Profile, Resumes, and Preferences: **PASSED**
- **Total: 30 passed in 24.60s (100% pass rate)**

### Frontend Production Build
Command:
```bash
npm run build
```
- TypeScript check: **0 errors**
- Vite production bundle: **Built successfully in 8.33s**
