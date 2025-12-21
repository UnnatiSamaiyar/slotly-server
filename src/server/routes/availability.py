from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, time

from ..database import get_db
from ..models.event_type import EventType
from ..models.booking_profile import BookingProfile
from ..models.booking import Booking

router = APIRouter(prefix="/bookings", tags=["availability"])

TIME_SLOTS = [time(h, 0) for h in range(9, 18)]  # 9AM–5PM


@router.get("/availability/{slug}")
def get_availability(slug: str, date: str, db: Session = Depends(get_db)):
    event_type = db.query(EventType).filter(EventType.slug == slug).first()
    if not event_type:
        raise HTTPException(404, "Event type not found")

    # ✅ Find matching booking_profile (may not exist yet)
    profile = db.query(BookingProfile).filter(BookingProfile.slug == slug).first()

    try:
        date_obj = datetime.strptime(date, "%Y-%m-%d").date()
    except:
        raise HTTPException(400, "Invalid date format")

    duration = timedelta(minutes=event_type.duration)
    slots = []

    for slot_time in TIME_SLOTS:
        start_dt = datetime.combine(date_obj, slot_time)
        end_dt = start_dt + duration

        booking_exists = None
        if profile:
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

    return {"date": date, "slots": slots}
