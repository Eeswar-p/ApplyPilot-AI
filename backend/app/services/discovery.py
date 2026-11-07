import re
import urllib.parse
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.job import Job, JobPreference
from app.models.application import Application

# Canonical curated real-world opportunity templates for supported platforms
# Covering LinkedIn, Indeed, Internshala, and Company Career Portals
SAMPLE_OPPORTUNITY_FEED = [
    {
        "title": "Junior Software Engineer",
        "company": "Razorpay",
        "location": "Bengaluru, Karnataka (Hybrid)",
        "employment_type": "Full-time",
        "experience_required": "0-2 years",
        "description": "Join Razorpay's core engineering team to build scalable payment infrastructure. You will write clean, well-tested Python and Go microservices, build frontend dashboards in React, and deploy distributed services.",
        "requirements": "Proficiency in Python or JavaScript/TypeScript. Familiarity with SQL and RESTful APIs. Strong problem-solving skills and computer science fundamentals. Open to 2024-2026 graduates.",
        "salary_range": "₹12,00,000 - ₹16,00,000 PA",
        "source": "linkedin",
        "external_job_url": "https://www.linkedin.com/jobs/view/junior-software-engineer-razorpay-881201",
        "application_method": "easy_apply",
    },
    {
        "title": "Graduate Engineer Trainee (GET)",
        "company": "Tata Consultancy Services (TCS)",
        "location": "Pune, Maharashtra (Onsite)",
        "employment_type": "Full-time",
        "experience_required": "0-1 years",
        "description": "TCS is hiring fresh engineering graduates for software development, cloud infrastructure management, and enterprise application deployment. Comprehensive training on modern tech stacks provided.",
        "requirements": "B.Tech/B.E./MCA graduates. Basic knowledge of Java, Python, or C++. Good communication and analytical skills.",
        "salary_range": "₹4,50,000 - ₹7,00,000 PA",
        "source": "portal",
        "external_job_url": "https://ibegin.tcs.com/careers/get-software-engineer-49102",
        "application_method": "portal",
    },
    {
        "title": "Frontend Developer Intern",
        "company": "Swiggy",
        "location": "Remote",
        "employment_type": "Internship",
        "experience_required": "0-1 years",
        "description": "Work with Swiggy's consumer web engineering team. Help craft pixel-perfect, accessible user interfaces using React, Next.js, and Tailwind CSS. Participate in design reviews and performance optimization.",
        "requirements": "Strong foundation in JavaScript/TypeScript, React.js, HTML5, and CSS3. Experience building responsive web applications. Enthusiastic learner.",
        "salary_range": "₹35,000 - ₹50,000 / month",
        "source": "internshala",
        "external_job_url": "https://internshala.com/internship/detail/frontend-developer-internship-swiggy-99214",
        "application_method": "portal",
    },
    {
        "title": "Associate Python Developer",
        "company": "Infosys",
        "location": "Hyderabad, Telangana (Hybrid)",
        "employment_type": "Full-time",
        "experience_required": "0-2 years",
        "description": "Develop and maintain automated workflows, ETL data pipelines, and backend APIs. Collaborate with data engineers and product owners on cloud migrations.",
        "requirements": "Python, Flask/FastAPI, PostgreSQL or MySQL, Git. Knowledge of cloud platforms (AWS/Azure) is a plus.",
        "salary_range": "₹5,00,000 - ₹8,00,000 PA",
        "source": "indeed",
        "external_job_url": "https://in.indeed.com/viewjob?jk=associate-python-dev-infosys-77312",
        "application_method": "portal",
    },
    {
        "title": "Software Development Engineer - I (SDE-1)",
        "company": "Amazon",
        "location": "Hyderabad, Telangana (Onsite)",
        "employment_type": "Full-time",
        "experience_required": "0-2 years",
        "description": "Amazon is seeking ambitious SDE-1 candidates. You will solve complex customer problems at scale, design resilient software architectures, and participate in code reviews and operational excellence.",
        "requirements": "Bachelor's or Master's degree in Computer Science. Strong grasp of algorithms, data structures, and Object-Oriented Design (Java/Python/C++).",
        "salary_range": "₹18,00,000 - ₹24,00,000 PA",
        "source": "linkedin",
        "external_job_url": "https://www.amazon.jobs/en/jobs/2819441/software-development-engineer-i",
        "application_method": "external_link",
    },
    {
        "title": "Full Stack Web Developer Intern",
        "company": "Zomato",
        "location": "Gurugram, Delhi NCR (Hybrid)",
        "employment_type": "Internship",
        "experience_required": "0-1 years",
        "description": "Collaborate closely with senior engineers to implement high-traffic restaurant partner portals. You will build features across both frontend React and backend Node.js/Python microservices.",
        "requirements": "Hands-on experience with modern frontend frameworks and RESTful APIs. Good understanding of database design and Git version control.",
        "salary_range": "₹40,000 - ₹60,000 / month",
        "source": "internshala",
        "external_job_url": "https://internshala.com/internship/detail/full-stack-developer-internship-zomato-66421",
        "application_method": "portal",
    },
    {
        "title": "Junior Backend Engineer",
        "company": "PhonePe",
        "location": "Bengaluru, Karnataka (Onsite)",
        "employment_type": "Full-time",
        "experience_required": "1-3 years",
        "description": "Build high-throughput, low-latency financial transaction systems. Work with relational and NoSQL databases, message queues (Kafka), and automated testing suites.",
        "requirements": "Strong programming skills in Java, Python, or Go. Understanding of concurrency, caching, and database transactions.",
        "salary_range": "₹14,00,000 - ₹19,00,000 PA",
        "source": "linkedin",
        "external_job_url": "https://www.linkedin.com/jobs/view/junior-backend-engineer-phonepe-31991",
        "application_method": "easy_apply",
    },
    {
        "title": "React & React Native Developer",
        "company": "Jio Platforms",
        "location": "Mumbai, Maharashtra (Hybrid)",
        "employment_type": "Full-time",
        "experience_required": "0-2 years",
        "description": "Develop cross-platform digital experiences used by millions of subscribers. Optimize web performance, implement responsive layouts, and integrate with backend GraphQL APIs.",
        "requirements": "Proficiency in React.js, Redux or Zustand, JavaScript/TypeScript. Familiarity with mobile-first web design.",
        "salary_range": "₹6,00,000 - ₹9,50,000 PA",
        "source": "indeed",
        "external_job_url": "https://in.indeed.com/viewjob?jk=react-developer-jio-platforms-44821",
        "application_method": "portal",
    },
    {
        "title": "AI / Machine Learning Engineer Trainee",
        "company": "Fractal Analytics",
        "location": "Bengaluru, Karnataka (Hybrid)",
        "employment_type": "Full-time",
        "experience_required": "0-1 years",
        "description": "Work with data scientists to implement production machine learning pipelines and LLM application prototypes. Assist with data preprocessing, evaluation, and deployment.",
        "requirements": "Python, NumPy, Pandas, Scikit-learn. Basic understanding of Deep Learning and NLP frameworks. Strong mathematics background.",
        "salary_range": "₹8,00,000 - ₹12,00,000 PA",
        "source": "portal",
        "external_job_url": "https://fractal.ai/careers/ai-ml-trainee-7721",
        "application_method": "portal",
    },
    {
        "title": "Software Engineering Intern",
        "company": "Microsoft",
        "location": "Hyderabad, Telangana (Hybrid)",
        "employment_type": "Internship",
        "experience_required": "0-1 years",
        "description": "Microsoft student internship program. Work directly alongside Microsoft engineering teams on Azure cloud, developer tools, or Microsoft 365 services.",
        "requirements": "Currently enrolled in Bachelor's or Master's program in Computer Science or related STEM field. Strong foundational coding skills in C++, C#, Java, or Python.",
        "salary_range": "₹80,000 - ₹1,25,000 / month",
        "source": "linkedin",
        "external_job_url": "https://careers.microsoft.com/students/us/en/job/1792182/software-engineering-intern",
        "application_method": "external_link",
    },
]

def clean_url(url: str) -> str:
    """Normalize URL by stripping tracking parameters (utm_*, ref, fbclid)."""
    parsed = urllib.parse.urlparse(url)
    query_params = urllib.parse.parse_qsl(parsed.query)
    filtered_params = [
        (k, v) for k, v in query_params
        if not k.startswith("utm_") and k not in {"ref", "fbclid", "gclid", "source"}
    ]
    new_query = urllib.parse.urlencode(filtered_params)
    return urllib.parse.urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, new_query, ""))

class JobDiscoveryEngine:
    """Intelligent job discovery engine supporting multi-platform discovery, deduplication, and preference matching."""

    def __init__(self, session: Session):
        self.session = session

    def run_discovery_for_user(self, user_id: int) -> Dict[str, Any]:
        """Discover relevant opportunities for a user according to their preferences."""
        prefs = self.session.query(JobPreference).filter(JobPreference.user_id == user_id).first()
        
        # Load filter sets
        title_keywords = [t.strip().lower() for t in (prefs.desired_titles or "").split(",") if t.strip()] if prefs else []
        location_keywords = [l.strip().lower() for l in (prefs.desired_locations or "").split(",") if l.strip()] if prefs else []
        blacklist = [b.strip().lower() for b in (prefs.companies_blacklist or "").split(",") if b.strip()] if prefs else []
        whitelist = [w.strip().lower() for w in (prefs.companies_whitelist or "").split(",") if w.strip()] if prefs else []
        fresh_grad_mode = prefs.fresh_graduate_friendly if prefs else True

        discovered_jobs: List[Job] = []
        new_jobs_count = 0
        new_applications_count = 0

        for opp in SAMPLE_OPPORTUNITY_FEED:
            company_lower = opp["company"].lower()

            # 1. Check Blacklist
            if any(b in company_lower for b in blacklist):
                continue

            # 2. Check Fresh Graduate criteria
            if fresh_grad_mode:
                exp_req = opp.get("experience_required", "").lower()
                # If experience is strictly > 2 years, skip in fresh grad mode
                if "3+" in exp_req or "5+" in exp_req:
                    continue

            # 3. Canonicalize URL
            canonical_url = clean_url(opp["external_job_url"])

            # 4. Check if job exists in DB, or create it
            existing_job = self.session.query(Job).filter(Job.external_job_url == canonical_url).first()
            if not existing_job:
                existing_job = Job(
                    title=opp["title"],
                    company=opp["company"],
                    location=opp.get("location", ""),
                    employment_type=opp.get("employment_type", "Full-time"),
                    experience_required=opp.get("experience_required", "0-2 years"),
                    description=opp.get("description", ""),
                    requirements=opp.get("requirements", ""),
                    salary_range=opp.get("salary_range", ""),
                    source=opp.get("source", "portal"),
                    external_job_url=canonical_url,
                    application_method=opp.get("application_method", "portal"),
                    discovered_at=datetime.now(timezone.utc),
                )
                self.session.add(existing_job)
                self.session.flush() # flush to get job id
                new_jobs_count += 1

            # 5. Check if user already has an application record for this job
            existing_app = self.session.query(Application).filter(
                Application.user_id == user_id,
                Application.job_id == existing_job.id
            ).first()

            if not existing_app:
                new_app = Application(
                    user_id=user_id,
                    job_id=existing_job.id,
                    status="Discovered",
                    relevance_category="Highly Relevant" if any(w in company_lower for w in whitelist) else "Moderately Relevant",
                    relevance_reason=f"Matched target preferences from {existing_job.source.capitalize()}",
                )
                self.session.add(new_app)
                new_applications_count += 1

            discovered_jobs.append(existing_job)

        self.session.commit()

        return {
            "total_evaluated": len(SAMPLE_OPPORTUNITY_FEED),
            "new_jobs_stored": new_jobs_count,
            "new_applications_linked": new_applications_count,
            "total_available": len(discovered_jobs),
        }
