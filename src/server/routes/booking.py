# from fastapi import APIRouter, HTTPException, Depends
# from pydantic import BaseModel, EmailStr
# from sqlalchemy.orm import Session
# from datetime import datetime, timedelta

# from ..database import get_db
# from ..services.booking_service import (
#     create_booking_record,
#     create_google_event_for_host,
#     get_profile_by_slug
# )
# from ..services.user_service import get_user_by_id

# # PRIMARY router
# router = APIRouter(prefix="/bookings", tags=["bookings"])


# class CreateBookingPayload(BaseModel):
#     profile_slug: str
#     guest_name: str
#     guest_email: EmailStr
#     start_iso: str


# @router.post("/create")
# def create_booking(payload: CreateBookingPayload, db: Session = Depends(get_db)):
#     profile = get_profile_by_slug(db, payload.profile_slug)
#     if not profile:
#         raise HTTPException(404, "Profile not found")

#     host_user = get_user_by_id(db, profile.user_id)
#     if not host_user:
#         raise HTTPException(404, "Host user not found")

#     try:
#         start_dt = datetime.fromisoformat(payload.start_iso)
#     except:
#         raise HTTPException(400, "Invalid start time")

#     end_dt = start_dt + timedelta(minutes=profile.duration_minutes)

#     attendees = [{"email": payload.guest_email}]

#     try:
#         event = create_google_event_for_host(
#             db,
#             host_user,
#             profile.title,
#             f"Booking via {profile.slug} by {payload.guest_name}",
#             start_dt,
#             end_dt,
#             attendees=attendees,
#         )
#         google_event_id = event.get("id")
#     except:
#         google_event_id = None

#     booking = create_booking_record(
#         db,
#         profile,
#         payload.guest_name,
#         payload.guest_email,
#         start_dt,
#         end_dt,
#         google_event_id,
#     )

#     return {"status": "ok", "booking_id": booking.id, "google_event_id": google_event_id}


# @router.get("/public/{slug}")
# def get_public_profile(slug: str, db: Session = Depends(get_db)):
#     profile = get_profile_by_slug(db, slug)
#     if not profile:
#         raise HTTPException(404, "Profile not found")

#     from ..models.user import User
#     host = db.query(User).filter(User.id == profile.user_id).first()

#     return {
#         "profile": {
#             "slug": profile.slug,
#             "title": profile.title,
#             "duration_minutes": profile.duration_minutes,
#             "user_id": profile.user_id,
#             "host_name": host.name if host else None,
#             "host_sub": host.google_sub if host else None
#         }
#     }


# # --- ALIAS ROUTER (Keeps OLD frontend working) ---
# alias_router = APIRouter(prefix="/booking", tags=["booking"])


# @alias_router.post("/create")
# def alias_create(payload: CreateBookingPayload, db: Session = Depends(get_db)):
#     return create_booking(payload, db)


# @alias_router.get("/public/{slug}")
# def alias_public(slug: str, db: Session = Depends(get_db)):
#     return get_public_profile(slug, db)












# # slotly-server/src/server/routes/booking_profile.py
# from fastapi import APIRouter, Depends, HTTPException, Header, Request
# from pydantic import BaseModel
# from typing import Optional, List
# from sqlalchemy.orm import Session

# from ..database import get_db
# from ..services import booking_profile_service as profile_svc
# from ..models.booking import BookingProfile  # model you provided

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






# from fastapi import APIRouter, HTTPException, Depends
# from pydantic import BaseModel, EmailStr
# from sqlalchemy.orm import Session
# from datetime import datetime, timedelta

# from ..database import get_db
# from ..services.booking_service import (
#     create_booking_record,
#     create_google_event_for_host,
#     get_profile_by_slug
# )
# from ..services.user_service import get_user_by_id

# router = APIRouter(prefix="/bookings", tags=["bookings"])

# class CreateBookingPayload(BaseModel):
#     profile_slug: str
#     guest_name: str
#     guest_email: EmailStr
#     start_iso: str

# @router.post("/create")
# def create_booking(payload: CreateBookingPayload, db: Session = Depends(get_db)):
#     profile = get_profile_by_slug(db, payload.profile_slug)
#     if not profile:
#         raise HTTPException(404, "Profile not found")

#     host_user = get_user_by_id(db, profile.user_id)
#     if not host_user:
#         raise HTTPException(404, "Host user not found")

#     try:
#         start_dt = datetime.fromisoformat(payload.start_iso)
#     except:
#         raise HTTPException(400, "Invalid start time")

#     end_dt = start_dt + timedelta(minutes=profile.duration_minutes)

#     attendees = [{"email": payload.guest_email}]

#     try:
#         event = create_google_event_for_host(
#             db,
#             host_user,
#             profile.title,
#             f"Booking via {profile.slug} by {payload.guest_name}",
#             start_dt,
#             end_dt,
#             attendees=attendees,
#         )
#         google_event_id = event.get("id")
#     except:
#         google_event_id = None

#     booking = create_booking_record(
#         db,
#         profile,
#         payload.guest_name,
#         payload.guest_email,
#         start_dt,
#         end_dt,
#         google_event_id,
#     )

#     return {"status": "ok", "booking_id": booking.id, "google_event_id": google_event_id}

# alias_router = APIRouter(prefix="/booking", tags=["booking"])

# @alias_router.post("/create")
# def alias_create(payload: CreateBookingPayload, db: Session = Depends(get_db)):
#     return create_booking(payload, db)

# @alias_router.get("/public/{slug}")
# def alias_public(slug: str, db: Session = Depends(get_db)):
#     profile = get_profile_by_slug(db, slug)
#     if not profile:
#         raise HTTPException(404, "Profile not found")

#     from ..models.user import User
#     host = db.query(User).filter(User.id == profile.user_id).first()

#     return {
#         "profile": {
#             "slug": profile.slug,
#             "title": profile.title,
#             "duration_minutes": profile.duration_minutes,
#             "user_id": profile.user_id,
#             "host_name": host.name if host else None,
#             "host_sub": host.google_sub if host else None
#         }
#     }




# from fastapi import APIRouter, HTTPException, Depends
# from pydantic import BaseModel, EmailStr
# from sqlalchemy.orm import Session
# from datetime import datetime, timedelta

# from ..database import get_db
# from ..services.booking_service import (
#     create_booking_record,
#     create_google_event_for_host,
#     get_profile_by_slug
# )
# from ..services.user_service import get_user_by_id

# from ..models.booking import Booking

# router = APIRouter(prefix="/bookings", tags=["bookings"])


# class CreateBookingPayload(BaseModel):
#     profile_slug: str
#     guest_name: str
#     guest_email: EmailStr
#     start_iso: str
#     title: str | None = None
#     timezone: str | None = None


# @router.post("/create")
# def create_booking(payload: CreateBookingPayload, db: Session = Depends(get_db)):
#     # 1️⃣ Load profile
#     profile = get_profile_by_slug(db, payload.profile_slug)
#     if not profile:
#         raise HTTPException(404, "Profile not found")

#     host_user = get_user_by_id(db, profile.user_id)
#     if not host_user:
#         raise HTTPException(404, "Host user not found")

#     # 2️⃣ Parse start time
#     try:
#         start_dt = datetime.fromisoformat(payload.start_iso)
#     except:
#         raise HTTPException(400, "Invalid start time format")

#     end_dt = start_dt + timedelta(minutes=profile.duration_minutes)

#     # -----------------------------------------------------
#     # 3️⃣ DATABASE LOCKING — Prevent double booking
#     # -----------------------------------------------------
#     conflict = db.query(Booking).filter(
#         Booking.profile_id == profile.id,
#         Booking.start_time < end_dt,
#         Booking.end_time > start_dt
#     ).first()

#     if conflict:
#         raise HTTPException(409, "This time slot is already booked.")

#     # -----------------------------------------------------
#     # 4️⃣ Final title handling
#     # -----------------------------------------------------
#     final_title = payload.title or profile.title

#     # -----------------------------------------------------
#     # 5️⃣ Create Google Calendar event
#     # -----------------------------------------------------
#     attendees = [{"email": payload.guest_email}]
#     google_event_id = None

#     try:
#         event = create_google_event_for_host(
#             db,
#             host_user,
#             final_title,
#             f"Booking via {profile.slug} by {payload.guest_name}",
#             start_dt,
#             end_dt,
#             attendees=attendees,
#         )
#         google_event_id = event.get("id")
#     except Exception as e:
#         print("Google event creation failed:", e)
#         google_event_id = None

#     # -----------------------------------------------------
#     # 6️⃣ Create DB booking record (NO REDIS NEEDED)
#     # -----------------------------------------------------
#     booking = create_booking_record(
#         db,
#         profile,
#         payload.guest_name,
#         payload.guest_email,
#         start_dt,
#         end_dt,
#         google_event_id,
#         title=final_title,
#         timezone=payload.timezone,
#     )

#     return {
#         "status": "ok",
#         "booking_id": booking.id,
#         "google_event_id": google_event_id
#     }


# # -------------------------------------
# # Alias routes for old frontend support
# # -------------------------------------

# alias_router = APIRouter(prefix="/booking", tags=["booking"])


# @alias_router.post("/create")
# def alias_create(payload: CreateBookingPayload, db: Session = Depends(get_db)):
#     return create_booking(payload, db)


# @alias_router.get("/public/{slug}")
# def alias_public(slug: str, db: Session = Depends(get_db)):
#     profile = get_profile_by_slug(db, slug)
#     if not profile:
#         raise HTTPException(404, "Profile not found")

#     from ..models.user import User
#     host = db.query(User).filter(User.id == profile.user_id).first()

#     return {
#         "profile": {
#             "slug": profile.slug,
#             "title": profile.title,
#             "duration_minutes": profile.duration_minutes,
#             "user_id": profile.user_id,
#             "host_name": host.name if host else None,
#             "host_sub": host.google_sub if host else None
#         }
#     }








# from fastapi import APIRouter, HTTPException, Depends
# from pydantic import BaseModel, EmailStr
# from typing import List, Optional
# from sqlalchemy.orm import Session
# from datetime import datetime, timedelta

# from ..database import get_db
# from ..services.booking_service import (
#     create_booking_record,
#     create_google_event_for_host,
#     get_profile_by_slug
# )
# from ..services.user_service import get_user_by_id

# from ..models.booking import Booking

# router = APIRouter(prefix="/bookings", tags=["bookings"])


# # ⭐ UPDATED PAYLOAD — supports multiple attendees
# class CreateBookingPayload(BaseModel):
#     profile_slug: str
#     guest_name: str
#     attendees: List[EmailStr]   # ⬅ MULTIPLE EMAILS
#     start_iso: str
#     title: Optional[str] = None
#     timezone: Optional[str] = None


# @router.post("/create")
# def create_booking(payload: CreateBookingPayload, db: Session = Depends(get_db)):

#     # 1️⃣ Load profile
#     profile = get_profile_by_slug(db, payload.profile_slug)
#     if not profile:
#         raise HTTPException(404, "Profile not found")

#     host_user = get_user_by_id(db, profile.user_id)
#     if not host_user:
#         raise HTTPException(404, "Host user not found")

#     # 2️⃣ Parse start time
#     try:
#         start_dt = datetime.fromisoformat(payload.start_iso)
#     except:
#         raise HTTPException(400, "Invalid start time format")

#     end_dt = start_dt + timedelta(minutes=profile.duration_minutes)

#     # -----------------------------------------------------
#     # 3️⃣ Double-booking prevention — same slot cannot repeat
#     # -----------------------------------------------------
#     conflict = db.query(Booking).filter(
#         Booking.profile_id == profile.id,
#         Booking.start_time < end_dt,
#         Booking.end_time > start_dt
#     ).first()

#     if conflict:
#         raise HTTPException(409, "This time slot is already booked.")

#     # -----------------------------------------------------
#     # 4️⃣ Final title
#     # -----------------------------------------------------
#     final_title = payload.title or profile.title

#     # -----------------------------------------------------
#     # 5️⃣ Build attendees list for Google Calendar
#     # -----------------------------------------------------
#     attendees = [{"email": email} for email in payload.attendees]

#     google_event_id = None

#     # -----------------------------------------------------
#     # 6️⃣ Create Google Calendar event (ONE MEET LINK)
#     # -----------------------------------------------------
#     try:
#         event = create_google_event_for_host(
#             db,
#             host_user,
#             final_title,
#             f"Booking via {profile.slug} by {payload.guest_name}",
#             start_dt,
#             end_dt,
#             attendees=attendees,  # ⭐ ALL ATTENDEES GO HERE
#         )
#         google_event_id = event.get("id")
#     except Exception as e:
#         print("Google event creation failed:", e)
#         google_event_id = None

#     # -----------------------------------------------------
#     # 7️⃣ Create booking record (one booking only)
#     # -----------------------------------------------------
#     booking = create_booking_record(
#         db,
#         profile,
#         payload.guest_name,
#         payload.attendees[0],  # store first email only (DB design)
#         start_dt,
#         end_dt,
#         google_event_id,
#         title=final_title,
#         timezone=payload.timezone,
#     )

#     return {
#         "status": "ok",
#         "booking_id": booking.id,
#         "google_event_id": google_event_id
#     }


# # -------------------------------------
# # Alias route for older frontend (optional)
# # -------------------------------------

# alias_router = APIRouter(prefix="/booking", tags=["booking"])


# @alias_router.post("/create")
# def alias_create(payload: CreateBookingPayload, db: Session = Depends(get_db)):
#     return create_booking(payload, db)












from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from ..database import get_db
from ..services.booking_service import (
    create_booking_record,
    create_google_event_for_host,
    get_profile_by_slug
)
from ..services.user_service import get_user_by_id

from ..models.booking import Booking

router = APIRouter(prefix="/bookings", tags=["bookings"])


# ⭐ UPDATED PAYLOAD — supports meeting mode + location + attendees
class CreateBookingPayload(BaseModel):
    profile_slug: str
    guest_name: str
    attendees: List[EmailStr]                     # multiple attendees
    start_iso: str
    title: Optional[str] = None
    timezone: Optional[str] = None

    meeting_mode: str = "google_meet"            # ⭐ new field
    location: Optional[str] = None               # ⭐ for in-person meetings


@router.post("/create")
def create_booking(payload: CreateBookingPayload, db: Session = Depends(get_db)):

    # 1️⃣ Load profile
    profile = get_profile_by_slug(db, payload.profile_slug)
    if not profile:
        raise HTTPException(404, "Profile not found")

    host_user = get_user_by_id(db, profile.user_id)
    if not host_user:
        raise HTTPException(404, "Host user not found")

    # 2️⃣ Parse start time
    try:
        start_dt = datetime.fromisoformat(payload.start_iso)
    except:
        raise HTTPException(400, "Invalid start time format")

    end_dt = start_dt + timedelta(minutes=profile.duration_minutes)

    # -----------------------------------------------------
    # 3️⃣ Double-booking prevention
    # -----------------------------------------------------
    conflict = db.query(Booking).filter(
        Booking.profile_id == profile.id,
        Booking.start_time < end_dt,
        Booking.end_time > start_dt
    ).first()

    if conflict:
        raise HTTPException(409, "This time slot is already booked.")

    # -----------------------------------------------------
    # 4️⃣ Title
    # -----------------------------------------------------
    final_title = payload.title or profile.title

    # -----------------------------------------------------
    # 5️⃣ Prepare attendees for Google Calendar
    # -----------------------------------------------------
    attendees = [{"email": email} for email in payload.attendees]

    google_event_id = None

    # -----------------------------------------------------
    # 6️⃣ Google Calendar event handling
    # -----------------------------------------------------
    if payload.meeting_mode == "google_meet":
        # ⭐ If Google Meet → create meet link for all attendees
        try:
            event = create_google_event_for_host(
                db,
                host_user,
                final_title,
                f"Booking via {profile.slug} by {payload.guest_name}",
                start_dt,
                end_dt,
                attendees=attendees,
            )
            google_event_id = event.get("id")
        except Exception as e:
            print("Google event creation failed:", e)
            google_event_id = None

    else:
        # ⭐ In-person meeting — NO Google Meet created
        google_event_id = None

    # -----------------------------------------------------
    # 7️⃣ Create database record
    # -----------------------------------------------------
    booking = create_booking_record(
        db,
        profile,
        payload.guest_name,
        payload.attendees,         # store multiple attendees
        start_dt,
        end_dt,
        google_event_id,
        title=final_title,
        timezone=payload.timezone
    )

    return {
        "status": "ok",
        "booking_id": booking.id,
        "google_event_id": google_event_id,
        "meeting_mode": payload.meeting_mode
    }
