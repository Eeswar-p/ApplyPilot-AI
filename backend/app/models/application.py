from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database.db import Base

class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id", ondelete="SET NULL"), nullable=True)
    
    # Statuses: 'Discovered', 'Eligible', 'Pending Approval', 'Applying', 'Applied', 'Failed', 'Skipped', 'Interview', 'Rejected', 'Offer Received'
    status = Column(String(50), default="Discovered", nullable=False, index=True)
    match_score = Column(Integer, default=0) # 0 to 100
    relevance_category = Column(String(50), default="Moderately Relevant") # 'Highly Relevant', 'Moderately Relevant', 'Not Relevant'
    relevance_reason = Column(Text, default="")
    automation_result = Column(Text, default="")
    failure_reason = Column(Text, default="")
    
    applied_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Unique constraint: user cannot have duplicate application record for same job
    __table_args__ = (
        UniqueConstraint('user_id', 'job_id', name='uq_user_job_application'),
    )

    user = relationship("User", back_populates="applications")
    job = relationship("Job", back_populates="applications")
    resume = relationship("Resume", back_populates="applications")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "job_id": self.job_id,
            "resume_id": self.resume_id,
            "status": self.status,
            "match_score": self.match_score,
            "relevance_category": self.relevance_category,
            "relevance_reason": self.relevance_reason or "",
            "automation_result": self.automation_result or "",
            "failure_reason": self.failure_reason or "",
            "applied_at": self.applied_at.isoformat() if self.applied_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "job": self.job.to_dict() if self.job else None,
            "resume": self.resume.to_dict() if self.resume else None,
        }
