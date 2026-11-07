from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db import get_db
from app.models.user import User
from app.models.profile import Profile, ProfileFact
from app.schemas.profile import ProfileResponse, ProfileFactCreate, ProfileFactResponse
from app.security.auth import get_current_user

router = APIRouter(prefix="/api/v1/profile", tags=["profile"])

@router.get("", response_model=ProfileResponse)
def get_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile

@router.post("/facts", response_model=ProfileFactResponse)
def add_profile_fact(
    fact: ProfileFactCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    new_fact = ProfileFact(
        profile_id=profile.id,
        category=fact.category,
        key=fact.key,
        value=fact.value,
        is_verified=fact.is_verified,
        source=fact.source,
        resume_id=fact.resume_id
    )
    db.add(new_fact)
    db.commit()
    db.refresh(new_fact)
    return new_fact

@router.delete("/facts/{fact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_profile_fact(
    fact_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    fact = db.query(ProfileFact).filter(ProfileFact.id == fact_id, ProfileFact.profile_id == profile.id).first()
    if not fact:
        raise HTTPException(status_code=404, detail="Fact not found")

    db.delete(fact)
    db.commit()
    return None
