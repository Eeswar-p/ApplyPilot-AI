from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database.db import Base

class ScreeningQuestion(Base):
    __tablename__ = "screening_questions"

    id = Column(Integer, primary_key=True, index=True)
    question_text = Column(String(512), unique=True, index=True, nullable=False)
    category = Column(String(100), default="general") # experience, authorization, education, relocation, salary
    question_type = Column(String(50), default="text") # text, boolean, select, number
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "question_text": self.question_text,
            "category": self.category,
            "question_type": self.question_type,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

class SavedAnswer(Base):
    __tablename__ = "saved_answers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    question_pattern = Column(String(512), index=True, nullable=False)
    answer_text = Column(Text, nullable=False)
    is_verified = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="saved_answers")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "question_pattern": self.question_pattern,
            "answer_text": self.answer_text,
            "is_verified": self.is_verified,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
