from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
 
from app.db import get_db
from app.models.db_models import Profile, Listing, MatchScore
from app.services.matching import rank_listings
 
router = APIRouter(prefix="/listings", tags=["listings"])
 
 
def _profile_to_dict(p: Profile) -> dict:
    return {
        "northstar": p.northstar,
        "final_idea": p.final_idea or "",
        "skills": p.skills or "",
        "dealbreakers": p.dealbreakers or "",
        "priorities": p.priorities or [],
        "target_types": p.target_types or [],
    }
 
 
def _listing_to_dict(l: Listing) -> dict:
    return {
        "id": str(l.id),
        "type": l.type,
        "title": l.title,
        "org": l.org,
        "tags": l.tags or [],
        "location": l.location,
        "deadline": l.deadline.isoformat() if l.deadline else None,
    }
 
 
@router.get("/matches/{user_id}")
def get_matches(user_id: str, db: Session = Depends(get_db)):
    """Returns the current top-ranked listings for a user, scored live
    against whatever's currently in the listings table.
    """
    profile = (
        db.query(Profile)
        .filter(Profile.user_id == user_id, Profile.is_current == True)  # noqa: E712
        .first()
    )
    if not profile:
        raise HTTPException(status_code=404, detail="No current profile for this user")
 
    listings = db.query(Listing).all()
    if not listings:
        return {"matches": [], "note": "No listings in the database yet - run a scan first."}
 
    ranked = rank_listings(
        [_listing_to_dict(l) for l in listings],
        _profile_to_dict(profile),
        top_n=10,
    )
    return {"matches": ranked, "profile_id": str(profile.id)}
 
 
@router.post("/scan/{user_id}")
def trigger_scan(user_id: str, db: Session = Depends(get_db)):
    """Manually triggers an immediate scan + re-scoring for one user,
    on top of the scheduled background job that runs for everyone.
    """
    from app.services.scheduler import run_scan_for_user
    result = run_scan_for_user(db, user_id)
    return result
 
