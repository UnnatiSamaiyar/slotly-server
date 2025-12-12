
# # slotly-server/src/server/routes/booking_profile.py
# from fastapi import APIRouter, Depends, HTTPException, Header, Request
# from pydantic import BaseModel
# from typing import Optional, List
# from sqlalchemy.orm import Session

# from ..database import get_db
# from ..services import booking_profile_service as profile_svc
# from ..models.booking_profile import BookingProfile
#  # model you provided

# router = APIRouter(prefix="/booking", tags=["booking_profiles"])

# # --- Schemas ---
# class CreateProfileIn(BaseModel):
#     title: str
#     slug: Optional[str] = None
#     duration_minutes: int = 30
#     description: Optional[str] = None

# class UpdateProfileIn(BaseModel):
#     title: Optional[str] = None
#     duration_minutes: Optional[int] = None
#     description: Optional[str] = None
#     active: Optional[bool] = None

# class ProfileOut(BaseModel):
#     id: int
#     slug: str
#     title: str
#     duration_minutes: int
#     user_id: Optional[int] = None
#     description: Optional[str] = None
#     created_at: Optional[str] = None

#     class Config:
#         orm_mode = True

# # Helper to get user id from header for now.
# # In your real auth, replace this with current_user dependency
# def _get_user_id_from_header(x_user_id: Optional[str] = Header(None)):
#     if not x_user_id:
#         raise HTTPException(status_code=401, detail="Missing X-User-Id header for development mode")
#     try:
#         return int(x_user_id)
#     except:
#         raise HTTPException(status_code=400, detail="Invalid X-User-Id header")

# # GET all profiles for current user
# @router.get("/profiles/me", response_model=List[ProfileOut])
# def profiles_for_me(db: Session = Depends(get_db), x_user_id: int = Depends(_get_user_id_from_header)):
#     profiles = profile_svc.list_profiles_for_user(db, x_user_id)
#     return profiles

# # POST create profile
# @router.post("/profiles", response_model=ProfileOut)
# def create_profile(payload: CreateProfileIn, db: Session = Depends(get_db), x_user_id: int = Depends(_get_user_id_from_header)):
#     create_payload = profile_svc.CreateProfilePayload(
#         title=payload.title,
#         slug=payload.slug,
#         duration_minutes=payload.duration_minutes,
#         user_id=x_user_id,
#         description=payload.description,
#     )
#     try:
#         profile = profile_svc.create_profile(db, create_payload)
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))
#     return profile

# # GET profile by slug (public)
# @router.get("/profile/{slug}", response_model=ProfileOut)
# def get_profile(slug: str, db: Session = Depends(get_db)):
#     profile = profile_svc.get_profile_by_slug(db, slug)
#     if not profile:
#         raise HTTPException(status_code=404, detail="Profile not found")
#     return profile

# # PUT update profile (owner only)
# @router.put("/profiles/{slug}", response_model=ProfileOut)
# def update_profile(slug: str, payload: UpdateProfileIn, db: Session = Depends(get_db), x_user_id: int = Depends(_get_user_id_from_header)):
#     profile = profile_svc.get_profile_by_slug(db, slug)
#     if not profile:
#         raise HTTPException(status_code=404, detail="Profile not found")
#     if profile.user_id != x_user_id:
#         raise HTTPException(status_code=403, detail="Not allowed")
#     patch = payload.dict(exclude_unset=True)
#     updated = profile_svc.update_profile(db, slug, patch)
#     if not updated:
#         raise HTTPException(status_code=500, detail="Update failed")
#     return updated

# # DELETE profile (owner only)
# @router.delete("/profiles/{slug}")
# def delete_profile(slug: str, db: Session = Depends(get_db), x_user_id: int = Depends(_get_user_id_from_header)):
#     profile = profile_svc.get_profile_by_slug(db, slug)
#     if not profile:
#         raise HTTPException(status_code=404, detail="Profile not found")
#     if profile.user_id != x_user_id:
#         raise HTTPException(status_code=403, detail="Not allowed")
#     ok = profile_svc.delete_profile(db, slug)
#     if not ok:
#         raise HTTPException(status_code=500, detail="Delete failed")
#     return {"status": "ok"}














# slotly-server/src/server/routes/booking_profile.py

from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session

from ..database import get_db
from ..services import booking_profile_service as profile_svc

router = APIRouter(prefix="/booking", tags=["booking_profiles"])

# -------------------------
# SCHEMAS
# -------------------------

class CreateProfileIn(BaseModel):
    title: str
    slug: Optional[str] = None
    duration_minutes: int = 30
    description: Optional[str] = None


class UpdateProfileIn(BaseModel):
    title: Optional[str] = None
    duration_minutes: Optional[int] = None
    description: Optional[str] = None
    active: Optional[bool] = None


class ProfileOut(BaseModel):
    id: int
    slug: str
    title: str
    duration_minutes: int
    user_id: Optional[int] = None
    description: Optional[str] = None
    created_at: Optional[str] = None
    active: Optional[bool] = True     # ✅ REQUIRED for frontend

    class Config:
        orm_mode = True


# -------------------------
# DEV AUTH (Header-Based)
# -------------------------

def _get_user_id_from_header(x_user_id: Optional[str] = Header(None)):
    if not x_user_id:
        raise HTTPException(401, "Missing X-User-Id header for development mode")
    try:
        return int(x_user_id)
    except:
        raise HTTPException(400, "Invalid X-User-Id header")


# -------------------------
# ROUTES
# -------------------------

@router.get("/profiles/me", response_model=List[ProfileOut])
def profiles_for_me(
    db: Session = Depends(get_db),
    x_user_id: int = Depends(_get_user_id_from_header)
):
    return profile_svc.list_profiles_for_user(db, x_user_id)


@router.post("/profiles", response_model=ProfileOut)
def create_profile(
    payload: CreateProfileIn,
    db: Session = Depends(get_db),
    x_user_id: int = Depends(_get_user_id_from_header)
):
    create_payload = profile_svc.CreateProfilePayload(
        title=payload.title,
        slug=payload.slug,
        duration_minutes=payload.duration_minutes,
        user_id=x_user_id,
        description=payload.description,
    )
    return profile_svc.create_profile(db, create_payload)


@router.get("/profile/{slug}", response_model=ProfileOut)
def get_profile(slug: str, db: Session = Depends(get_db)):
    profile = profile_svc.get_profile_by_slug(db, slug)
    if not profile:
        raise HTTPException(404, "Profile not found")
    return profile


@router.put("/profiles/{slug}", response_model=ProfileOut)
def update_profile(
    slug: str,
    payload: UpdateProfileIn,
    db: Session = Depends(get_db),
    x_user_id: int = Depends(_get_user_id_from_header)
):
    profile = profile_svc.get_profile_by_slug(db, slug)
    if not profile:
        raise HTTPException(404, "Profile not found")
    if profile.user_id != x_user_id:
        raise HTTPException(403, "Not allowed")

    patch = payload.dict(exclude_unset=True)
    updated = profile_svc.update_profile(db, slug, patch)
    if not updated:
        raise HTTPException(500, "Update failed")

    return updated


@router.delete("/profiles/{slug}")
def delete_profile(
    slug: str,
    db: Session = Depends(get_db),
    x_user_id: int = Depends(_get_user_id_from_header)
):
    profile = profile_svc.get_profile_by_slug(db, slug)
    if not profile:
        raise HTTPException(404, "Profile not found")
    if profile.user_id != x_user_id:
        raise HTTPException(403, "Not allowed")

    ok = profile_svc.delete_profile(db, slug)
    if not ok:
        raise HTTPException(500, "Delete failed")

    return {"status": "ok"}
