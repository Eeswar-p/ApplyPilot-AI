from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database.db import Base

class AutomationSetting(Base):
    __tablename__ = "automation_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    max_applications_per_session = Column(Integer, default=15, nullable=False)
    application_delay_seconds = Column(Integer, default=5, nullable=False)
    require_approval = Column(Boolean, default=False, nullable=False)
    auto_submit = Column(Boolean, default=True, nullable=False)
    target_platforms = Column(String(255), default="linkedin,indeed,internshala")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="automation_settings")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "max_applications_per_session": self.max_applications_per_session,
            "application_delay_seconds": self.application_delay_seconds,
            "require_approval": self.require_approval,
            "auto_submit": self.auto_submit,
            "target_platforms": self.target_platforms or "",
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

class AutomationSession(Base):
    __tablename__ = "automation_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(50), default="idle", nullable=False) # 'idle', 'running', 'paused', 'completed', 'stopped', 'failed'
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    ended_at = Column(DateTime, nullable=True)
    total_discovered = Column(Integer, default=0, nullable=False)
    total_processed = Column(Integer, default=0, nullable=False)
    total_successful = Column(Integer, default=0, nullable=False)
    total_failed = Column(Integer, default=0, nullable=False)
    current_job_title = Column(String(255), default="")
    current_job_company = Column(String(255), default="")
    error_message = Column(Text, default="")

    user = relationship("User", back_populates="automation_sessions")
    logs = relationship("AutomationLog", back_populates="session", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "status": self.status,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "total_discovered": self.total_discovered,
            "total_processed": self.total_processed,
            "total_successful": self.total_successful,
            "total_failed": self.total_failed,
            "current_job_title": self.current_job_title or "",
            "current_job_company": self.current_job_company or "",
            "error_message": self.error_message or "",
        }

class AutomationLog(Base):
    __tablename__ = "automation_logs"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("automation_sessions.id", ondelete="CASCADE"), nullable=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    log_level = Column(String(20), default="INFO", nullable=False) # INFO, WARNING, ERROR, SUCCESS
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    session = relationship("AutomationSession", back_populates="logs")
    user = relationship("User", back_populates="automation_logs")

    def to_dict(self):
        return {
            "id": self.id,
            "session_id": self.session_id,
            "user_id": self.user_id,
            "log_level": self.log_level,
            "message": self.message,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }
