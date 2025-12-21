# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session

# from ..database import get_db
# from ..services.booking_service import (
#     get_profile_by_slug,
#     create_google_event_for_host,
#     create_booking_record
# )
# from pydantic import BaseModel


# from ..models.booking_profile import BookingProfile
# from ..models.user import User

# from ..models.user import User
# from datetime import datetime, timedelta


# router = APIRouter(prefix="/public", tags=["public-booking"])

# class PublicBookingPayload(BaseModel):
#     profile_slug: str
#     guest_name: str
#     attendees: list[str]
#     start_iso: str
#     title: str | None = None
#     timezone: str | None = None
#     meeting_mode: str = "google_meet"
#     location: str | None = None


# @router.get("/debug/all-profiles")
# def debug_all_profiles(db: Session = Depends(get_db)):
#     profiles = db.query(BookingProfile).all()
#     return {
#         "count": len(profiles),
#         "slugs": [p.slug for p in profiles],
#         "titles": [p.title for p in profiles]
#     }


# @router.get("/profile/{slug}")
# def load_public_profile(slug: str, db: Session = Depends(get_db)):
#     profile = get_profile_by_slug(db, slug)
#     if not profile:
#         raise HTTPException(404, "Profile not found")

#     host = db.query(User).filter(User.id == profile.user_id).first()

#     return {
#         "profile": {
#             "slug": profile.slug,
#             "title": profile.title,
#             "duration_minutes": profile.duration_minutes,
#             "host_name": host.name if host else None
#         },
#         "slots": [] 
#     }


# @router.post("/book")
# def public_create_booking(payload: PublicBookingPayload, db: Session = Depends(get_db)):

#     profile = get_profile_by_slug(db, payload.profile_slug)
#     if not profile:
#         raise HTTPException(404, "Profile not found")

#     host = db.query(User).filter(User.id == profile.user_id).first()

#     start_dt = datetime.fromisoformat(payload.start_iso)
#     end_dt = start_dt + timedelta(minutes=profile.duration_minutes)

#     # Build attendees for Google API
#     attendees = [{"email": email} for email in payload.attendees]

#     event = create_google_event_for_host(
#         db,
#         host,
#         payload.title or profile.title,
#         f"Public booking by {payload.guest_name}",
#         start_dt,
#         end_dt,
#         attendees=attendees,
#         meeting_mode=payload.meeting_mode,
#         location=payload.location
#     )

#     booking = create_booking_record(
#         db,
#         profile,
#         payload.guest_name,
#         payload.attendees,
#         start_dt,
#         end_dt,
#         google_event_id=event.get("id"),
#         title=payload.title,
#         timezone=payload.timezone,
#         meeting_mode=payload.meeting_mode,
#         location=payload.location
#     )

#     return {"status": "success", "booking_id": booking.id}










from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from pydantic import BaseModel

from ..database import get_db
from ..models.user import User
from ..models.event_type import EventType
from ..models.booking_profile import BookingProfile


from ..services.booking_service import (
    create_google_event_for_host,
    create_booking_record
)

router = APIRouter(prefix="/public", tags=["public-booking"])


class PublicBookingPayload(BaseModel):
    profile_slug: str
    guest_name: str
    attendees: list[str]
    start_iso: str
    title: str | None = None
    timezone: str | None = None
    meeting_mode: str = "google_meet"
    location: str | None = None


@router.get("/profile/{slug}")
def load_public_profile(slug: str, db: Session = Depends(get_db)):
    event_type = db.query(EventType).filter(EventType.slug == slug).first()
    if not event_type:
        raise HTTPException(404, "Profile not found")

    host = db.query(User).filter(User.id == event_type.user_id).first()

    return {
        "profile": {
            "slug": event_type.slug,
            "title": event_type.title,
            "duration_minutes": event_type.duration,
            "host_name": host.name if host else None,
            "location": event_type.location,
        }
    }


@router.post("/book")
def public_create_booking(payload: PublicBookingPayload, db: Session = Depends(get_db)):
    event_type = db.query(EventType).filter(EventType.slug == payload.profile_slug).first()
    if not event_type:
        raise HTTPException(404, "Profile not found")

    host = db.query(User).filter(User.id == event_type.user_id).first()
    if not host:
        raise HTTPException(404, "Host not found")

    # ✅ 1) Ensure BookingProfile exists (FK safe)
    profile = db.query(BookingProfile).filter(BookingProfile.slug == event_type.slug).first()
    if not profile:
        profile = BookingProfile(
            slug=event_type.slug,
            user_id=event_type.user_id,
            duration_minutes=event_type.duration,
            title=event_type.title,
            active=True
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)

    start_dt = datetime.fromisoformat(payload.start_iso)
    end_dt = start_dt + timedelta(minutes=event_type.duration)

    attendees = [{"email": email} for email in payload.attendees]

    event = create_google_event_for_host(
        db,
        host,
        payload.title or event_type.title,
        f"Public booking by {payload.guest_name}",
        start_dt,
        end_dt,
        attendees=attendees,
        meeting_mode=payload.meeting_mode,
        location=payload.location or event_type.location,
    )

    # ✅ 2) Create booking with BookingProfile (NOT EventType)
    booking = create_booking_record(
        db,
        profile,                      # ✅ BookingProfile object
        payload.guest_name,
        payload.attendees,            # list
        start_dt,
        end_dt,
        google_event_id=(event.get("id") if event else None),
        title=payload.title or event_type.title,
        timezone=payload.timezone,
        meeting_mode=payload.meeting_mode,
        location=payload.location or event_type.location,
    )

    return {"status": "success", "booking_id": booking.id}

