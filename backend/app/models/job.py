from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database.db import Base

class JobPreference(Base):
    __tablename__ = "job_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    desired_titles = Column(Text, default="Software Engineer, Full Stack Developer, Frontend Developer, Backend Developer")
    desired_locations = Column(Text, default="Remote, Bangalore, Hyderabad, Pune, Mumbai, Delhi NCR")
    remote_preference = Column(String(50), default="any") # 'remote', 'hybrid', 'onsite', 'any'
    min_salary = Column(Integer, default=0)
    employment_types = Column(String(100), default="full-time, internship")
    experience_level = Column(String(50), default="entry") # 'entry', 'mid', 'any'
    fresh_graduate_friendly = Column(Boolean, default=True)
    skills_filter = Column(Text, default="")
    companies_whitelist = Column(Text, default="")
    companies_blacklist = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="job_preferences")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "desired_titles": self.desired_titles or "",
            "desired_locations": self.desired_locations or "",
            "remote_preference": self.remote_preference or "any",
            "min_salary": self.min_salary or 0,
            "employment_types": self.employment_types or "any",
            "experience_level": self.experience_level or "entry",
            "fresh_graduate_friendly": self.fresh_graduate_friendly,
            "skills_filter": self.skills_filter or "",
            "companies_whitelist": self.companies_whitelist or "",
            "companies_blacklist": self.companies_blacklist or "",
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), index=True, nullable=False)
    company = Column(String(255), index=True, nullable=False)
    location = Column(String(255), default="")
    employment_type = Column(String(100), default="Full-time")
    experience_required = Column(String(100), default="0-2 years")
    description = Column(Text, default="")
    requirements = Column(Text, default="")
    salary_range = Column(String(100), default="")
    source = Column(String(100), default="portal", index=True) # 'linkedin', 'indeed', 'internshala', 'portal'
    external_job_url = Column(String(1024), unique=True, index=True, nullable=False)
    application_method = Column(String(50), default="portal") # 'easy_apply', 'external_link'
    discovered_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    applications = relationship("Application", back_populates="job", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "company": self.company,
            "location": self.location or "",
            "employment_type": self.employment_type or "Full-time",
            "experience_required": self.experience_required or "",
            "description": self.description or "",
            "requirements": self.requirements or "",
            "salary_range": self.salary_range or "",
            "source": self.source or "portal",
            "external_job_url": self.external_job_url,
            "application_method": self.application_method or "portal",
            "discovered_at": self.discovered_at.isoformat() if self.discovered_at else None,
        }
