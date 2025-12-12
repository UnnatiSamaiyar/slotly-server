from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..services.user_service import get_user_by_sub
from ..models.user import User

router = APIRouter(prefix="/user", tags=["user"])

@router.get("/me")
def get_me(user_sub: str, db: Session = Depends(get_db)):
    """
    Returns full user profile + booking profile
    """
    user: User = get_user_by_sub(db, user_sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Fetch Primary Booking Profile (if exists)
    primary_profile = user.booking_profiles[0] if user.booking_profiles else None

    return {
        "sub": user.google_sub,
        "name": user.name,
        "email": user.email,
        "picture": user.picture,
        "avatar_url": user.picture,
        "username": user.email.split("@")[0],

        # Include full booking profile info
        "profile_title": primary_profile.title if primary_profile else None,
        "host_name": primary_profile.host_name if primary_profile else None,
        "timezone": primary_profile.timezone if primary_profile else None,
        "slug": primary_profile.slug if primary_profile else None,

        # Useful flags
        "has_booking_profile": primary_profile is not None
    }
