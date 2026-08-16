from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import desc
 
from app.db import get_db
from app.models.db_models import Profile
 
router = APIRouter(prefix="/profile", tags=["profile"])
 
 
class SurveyIn(BaseModel):
    user_id: str
    northstar: str
    final_idea: str | None = None
    timeframe: str
    stage: str
    priorities: list[str]
    skills: str
    dealbreakers: str | None = None
    location_pref: str | None = None
    target_types: list[str]
 
 
@router.post("")
def create_profile(payload: SurveyIn, db: Session = Depends(get_db)):
    """Creates a new profile snapshot and marks it current.
    Previous profile rows stay in the table - that history is what
    lets the chatbot later explain how a user's goals have changed.
    """
    db.query(Profile).filter(
        Profile.user_id == payload.user_id, Profile.is_current == True  # noqa: E712
    ).update({"is_current": False})
 
    new_profile = Profile(
        user_id=payload.user_id,
        northstar=payload.northstar,
        final_idea=payload.final_idea,
        timeframe=payload.timeframe,
        stage=payload.stage,
        priorities=payload.priorities,
        skills=payload.skills,
        dealbreakers=payload.dealbreakers,
        location_pref=payload.location_pref,
        target_types=payload.target_types,
        is_current=True,
    )
    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)
    return {"status": "created", "profile_id": str(new_profile.id)}
 
 
@router.get("/{user_id}")
def get_current_profile(user_id: str, db: Session = Depends(get_db)):
    profile = (
        db.query(Profile)
        .filter(Profile.user_id == user_id, Profile.is_current == True)  # noqa: E712
        .first()
    )
    if not profile:
        raise HTTPException(status_code=404, detail="No current profile for this user")
    return {
        "id": str(profile.id),
        "northstar": profile.northstar,
        "final_idea": profile.final_idea,
        "timeframe": profile.timeframe,
        "stage": profile.stage,
        "priorities": profile.priorities,
        "skills": profile.skills,
        "dealbreakers": profile.dealbreakers,
        "location_pref": profile.location_pref,
        "target_types": profile.target_types,
    }
 
 
@router.get("/{user_id}/history")
def get_profile_history(user_id: str, db: Session = Depends(get_db)):
    profiles = (
        db.query(Profile)
        .filter(Profile.user_id == user_id)
        .order_by(desc(Profile.created_at))
        .all()
    )
    return [
        {
            "id": str(p.id),
            "northstar": p.northstar,
            "is_current": p.is_current,
            "created_at": p.created_at.isoformat(),
        }
        for p in profiles
    ]
 
