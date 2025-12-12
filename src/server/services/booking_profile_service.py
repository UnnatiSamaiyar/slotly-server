# # slotly-server/src/server/services/booking_profile_service.py
# from sqlalchemy.orm import Session
# from sqlalchemy.exc import IntegrityError
# from typing import List, Optional
# from datetime import datetime

# from ..models.booking import BookingProfile  # path based on your provided model file

# class CreateProfilePayload:
#     def __init__(self, title: str, slug: Optional[str], duration_minutes: int, user_id: int, description: Optional[str] = None):
#         self.title = title
#         self.slug = slug
#         self.duration_minutes = duration_minutes
#         self.user_id = user_id
#         self.description = description

# def list_profiles_for_user(db: Session, user_id: int) -> List[BookingProfile]:
#     return db.query(BookingProfile).filter(BookingProfile.user_id == user_id).order_by(BookingProfile.created_at.desc()).all()

# def get_profile_by_slug(db: Session, slug: str) -> Optional[BookingProfile]:
#     return db.query(BookingProfile).filter(BookingProfile.slug == slug).first()

# def create_profile(db: Session, payload: CreateProfilePayload) -> BookingProfile:
#     # Ensure slug exists
#     slug = (payload.slug or payload.title or "untitled").strip().lower().replace(" ", "-")
#     # Normalize: remove non-url-friendly chars (simple)
#     import re
#     slug = re.sub(r"[^a-z0-9\-]", "", slug)

#     # Ensure unique slug by appending suffix if needed
#     base = slug
#     i = 1
#     while db.query(BookingProfile).filter(BookingProfile.slug == slug).first():
#         slug = f"{base}-{i}"
#         i += 1

#     profile = BookingProfile(
#         title=payload.title,
#         slug=slug,
#         duration_minutes=payload.duration_minutes,
#         user_id=payload.user_id,
#         # created_at is auto-handled by model default
#     )
#     # If your model has description or other fields, set them if available (safe getattr)
#     if hasattr(profile, "description") and payload.description is not None:
#         setattr(profile, "description", payload.description)

#     db.add(profile)
#     try:
#         db.commit()
#     except IntegrityError:
#         db.rollback()
#         raise
#     db.refresh(profile)
#     return profile

# def update_profile(db: Session, slug: str, patch: dict) -> Optional[BookingProfile]:
#     profile = get_profile_by_slug(db, slug)
#     if not profile:
#         return None

#     # Only update allowed fields
#     allowed = {"title", "duration_minutes", "description", "active"}
#     for k, v in patch.items():
#         if k in allowed and hasattr(profile, k):
#             setattr(profile, k, v)

#     # If caller tries to change slug, ignore here (we keep slug immutable). If you want slug change, implement separately.
#     db.add(profile)
#     db.commit()
#     db.refresh(profile)
#     return profile

# def delete_profile(db: Session, slug: str) -> bool:
#     profile = get_profile_by_slug(db, slug)
#     if not profile:
#         return False
#     db.delete(profile)
#     db.commit()
#     return True









# # src/server/services/booking_profile_service.py

# from sqlalchemy.orm import Session
# from sqlalchemy.exc import IntegrityError
# from typing import Optional, List
# from datetime import datetime
# from ..models.booking_profile import BookingProfile

# import re


# def list_profiles_for_user(db: Session, user_id: int) -> List[BookingProfile]:
#     return (
#         db.query(BookingProfile)
#         .filter(BookingProfile.user_id == user_id)
#         .order_by(BookingProfile.created_at.desc())
#         .all()
#     )


# def get_profile_by_slug(db: Session, slug: str) -> Optional[BookingProfile]:
#     return db.query(BookingProfile).filter(BookingProfile.slug == slug).first()


# def create_profile(db: Session, title: str, duration: int, user_id: int, description: str = None):
#     # Generate slug
#     slug = title.lower().strip().replace(" ", "-")
#     slug = re.sub(r"[^a-z0-9\-]", "", slug)

#     # Ensure unique slug
#     base = slug
#     i = 1
#     while get_profile_by_slug(db, slug):
#         slug = f"{base}-{i}"
#         i += 1

#     profile = BookingProfile(
#         title=title,
#         slug=slug,
#         user_id=user_id,
#         duration_minutes=duration,
#         description=description,
#     )

#     db.add(profile)
#     try:
#         db.commit()
#     except IntegrityError:
#         db.rollback()
#         raise

#     db.refresh(profile)
#     return profile


# def update_profile(db: Session, slug: str, patch: dict):
#     profile = get_profile_by_slug(db, slug)
#     if not profile:
#         return None

#     allowed = {"title", "duration_minutes", "description", "active"}
#     for k, v in patch.items():
#         if k in allowed:
#             setattr(profile, k, v)

#     db.commit()
#     db.refresh(profile)
#     return profile


# def delete_profile(db: Session, slug: str):
#     profile = get_profile_by_slug(db, slug)
#     if not profile:
#         return False

#     db.delete(profile)
#     db.commit()
#     return True







# src/server/services/booking_profile_service.py

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
import re

from ..models.booking_profile import BookingProfile


# ----------------------------------------
# Pydantic Payload for create_profile()
# ----------------------------------------
class CreateProfilePayload(BaseModel):
    title: str
    slug: Optional[str] = None
    duration_minutes: int = 30
    user_id: int
    description: Optional[str] = None


# ----------------------------------------
# List all profiles for a user
# ----------------------------------------
def list_profiles_for_user(db: Session, user_id: int) -> List[BookingProfile]:
    return (
        db.query(BookingProfile)
        .filter(BookingProfile.user_id == user_id)
        .order_by(BookingProfile.created_at.desc())
        .all()
    )


# ----------------------------------------
# Get profile by slug
# ----------------------------------------
def get_profile_by_slug(db: Session, slug: str) -> Optional[BookingProfile]:
    return db.query(BookingProfile).filter(BookingProfile.slug == slug).first()


# ----------------------------------------
# Create a booking profile
# ----------------------------------------
def create_profile(db: Session, payload: CreateProfilePayload):
    title = payload.title.strip()
    duration = payload.duration_minutes
    user_id = payload.user_id
    description = payload.description

    # Generate slug
    if payload.slug:
        slug = payload.slug.lower().strip().replace(" ", "-")
    else:
        slug = title.lower().strip().replace(" ", "-")

    slug = re.sub(r"[^a-z0-9\-]", "", slug)

    # Ensure unique slug
    base = slug
    i = 1
    while get_profile_by_slug(db, slug):
        slug = f"{base}-{i}"
        i += 1

    profile = BookingProfile(
        title=title,
        slug=slug,
        user_id=user_id,
        duration_minutes=duration,
        description=description,
        active=True,
    )

    db.add(profile)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise

    db.refresh(profile)
    return profile


# ----------------------------------------
# Update booking profile
# ----------------------------------------
def update_profile(db: Session, slug: str, patch: dict):
    profile = get_profile_by_slug(db, slug)
    if not profile:
        return None

    allowed_fields = {"title", "duration_minutes", "description", "active"}

    for key, value in patch.items():
        if key in allowed_fields:
            setattr(profile, key, value)

    db.commit()
    db.refresh(profile)

    return profile


# ----------------------------------------
# Delete booking profile
# ----------------------------------------
def delete_profile(db: Session, slug: str) -> bool:
    profile = get_profile_by_slug(db, slug)
    if not profile:
        return False

    db.delete(profile)
    db.commit()
    return True 
