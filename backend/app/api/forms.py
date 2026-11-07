from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db import get_db
from app.models.user import User
from app.models.profile import Profile, ProfileFact
from app.security.auth import get_current_user
from app.services.matching.rules import ScannedField, MatchProposal, rule_based_match

router = APIRouter(prefix="/api/v1/forms", tags=["forms"])

class MatchRequest(BaseModel):
    fields: List[ScannedField]

from pydantic import BaseModel
class MatchRequest(BaseModel):
    fields: List[ScannedField]

@router.post("/match", response_model=List[MatchProposal])
def match_fields(
    request: MatchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    facts = db.query(ProfileFact).filter(ProfileFact.profile_id == profile.id).all()
    profile_dict = {fact.key: fact.value for fact in facts}

    # Apply rule-based matching
    proposals = rule_based_match(request.fields, profile_dict)
    
    return proposals
