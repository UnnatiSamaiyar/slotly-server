# routes_availability.py
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, time

from ..database import get_db
from ..services.user_service import get_user_by_sub
from ..models.booking_profile import BookingProfile
from ..models.event_type import EventType
from ..models.booking import Booking

router = APIRouter(prefix="/bookings", tags=["availability"])

TIME_SLOTS = [time(h, 0) for h in range(9, 18)]  # 9AM–5PM

@router.get("/availability")
def get_availability(user_sub: str, date: str, db: Session = Depends(get_db)):
    user = get_user_by_sub(db, user_sub)
    if not user:
        raise HTTPException(404, "User not found")

    profile = user.booking_profiles[0] if user.booking_profiles else None
    if not profile:
        raise HTTPException(404, "Booking profile not found")

    # event_type by same slug (your DB pattern)
    event_type = db.query(EventType).filter(EventType.slug == profile.slug).first()
    if not event_type:
        raise HTTPException(404, "Event type not found")

    try:
        date_obj = datetime.strptime(date, "%Y-%m-%d").date()
    except:
        raise HTTPException(400, "Invalid date format")

    duration = timedelta(minutes=event_type.duration)
    slots = []

    for slot_time in TIME_SLOTS:
        start_dt = datetime.combine(date_obj, slot_time)
        end_dt = start_dt + duration

        booking_exists = db.query(Booking).filter(
            Booking.profile_id == profile.id,
            Booking.start_time < end_dt,
            Booking.end_time > start_dt
        ).first()

        slots.append({
            "time": slot_time.strftime("%H:%M"),
            "iso": start_dt.isoformat(),
            "available": booking_exists is None
        })

    return {"date": date, "profile_slug": profile.slug, "slots": slots}

@router.get("/availability/{slug}")
def get_availability_by_slug(slug: str, date: str, db: Session = Depends(get_db)):
    profile = db.query(BookingProfile).filter(BookingProfile.slug == slug).first()
    if not profile:
        raise HTTPException(404, "Booking profile not found")

    event_type = db.query(EventType).filter(EventType.slug == slug).first()
    if not event_type:
        raise HTTPException(404, "Event type not found")

    try:
        date_obj = datetime.strptime(date, "%Y-%m-%d").date()
    except:
        raise HTTPException(400, "Invalid date format")

    duration = timedelta(minutes=event_type.duration)
    slots = []

    for slot_time in TIME_SLOTS:
        start_dt = datetime.combine(date_obj, slot_time)
        end_dt = start_dt + duration

        booking_exists = db.query(Booking).filter(
            Booking.profile_id == profile.id,
            Booking.start_time < end_dt,
            Booking.end_time > start_dt
        ).first()

        slots.append({
            "time": slot_time.strftime("%H:%M"),
            "iso": start_dt.isoformat(),
            "available": booking_exists is None
        })

    return {"date": date, "profile_slug": profile.slug, "slots": slots}
