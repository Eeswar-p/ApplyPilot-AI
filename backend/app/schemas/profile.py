from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ProfileFactBase(BaseModel):
    category: str
    key: str
    value: str
    is_verified: bool = False
    source: str = "user_input"
    resume_id: Optional[int] = None

class ProfileFactCreate(ProfileFactBase):
    pass

class ProfileFactResponse(ProfileFactBase):
    id: int
    profile_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ProfileResponse(BaseModel):
    id: int
    user_id: int
    facts: List[ProfileFactResponse] = []

    class Config:
        from_attributes = True

class ResumeBase(BaseModel):
    filename: str

class ResumeResponse(ResumeBase):
    id: int
    parsed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True
