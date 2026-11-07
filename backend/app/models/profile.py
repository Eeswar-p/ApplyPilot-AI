from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from app.database.db import Base

class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    full_name = Column(String(255), default="")
    phone = Column(String(50), default="")
    address = Column(String(255), default="")
    city = Column(String(100), default="")
    state = Column(String(100), default="")
    country = Column(String(100), default="India")
    postal_code = Column(String(20), default="")
    linkedin_url = Column(String(255), default="")
    github_url = Column(String(255), default="")
    portfolio_url = Column(String(255), default="")
    bio = Column(Text, default="")
    graduation_year = Column(Integer, nullable=True)
    highest_degree = Column(String(100), default="")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="profile")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "full_name": self.full_name or "",
            "phone": self.phone or "",
            "address": self.address or "",
            "city": self.city or "",
            "state": self.state or "",
            "country": self.country or "",
            "postal_code": self.postal_code or "",
            "linkedin_url": self.linkedin_url or "",
            "github_url": self.github_url or "",
            "portfolio_url": self.portfolio_url or "",
            "bio": self.bio or "",
            "graduation_year": self.graduation_year,
            "highest_degree": self.highest_degree or "",
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

class Education(Base):
    __tablename__ = "education"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    institution = Column(String(255), nullable=False)
    degree = Column(String(100), nullable=False)
    field_of_study = Column(String(150), default="")
    start_date = Column(String(50), default="")
    end_date = Column(String(50), default="")
    gpa = Column(String(20), default="")
    is_current = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="education")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "institution": self.institution,
            "degree": self.degree,
            "field_of_study": self.field_of_study or "",
            "start_date": self.start_date or "",
            "end_date": self.end_date or "",
            "gpa": self.gpa or "",
            "is_current": self.is_current,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    skill_name = Column(String(100), nullable=False, index=True)
    category = Column(String(50), default="Technical")
    proficiency_level = Column(String(50), default="Intermediate")
    years_of_experience = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="skills")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "skill_name": self.skill_name,
            "category": self.category or "Technical",
            "proficiency_level": self.proficiency_level or "Intermediate",
            "years_of_experience": self.years_of_experience,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

class Experience(Base):
    __tablename__ = "experience"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    company = Column(String(255), nullable=False)
    job_title = Column(String(150), nullable=False)
    location = Column(String(150), default="")
    start_date = Column(String(50), default="")
    end_date = Column(String(50), default="")
    is_current = Column(Boolean, default=False)
    description = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="experience")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "company": self.company,
            "job_title": self.job_title,
            "location": self.location or "",
            "start_date": self.start_date or "",
            "end_date": self.end_date or "",
            "is_current": self.is_current,
            "description": self.description or "",
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
