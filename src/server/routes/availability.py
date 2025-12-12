from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, time

from ..database import get_db
from ..services.booking_service import get_profile_by_slug
from ..models.booking import Booking

router = APIRouter(prefix="/bookings", tags=["availability"])

# Default daily slots (customizable later)
TIME_SLOTS = [time(h, 0) for h in range(9, 18)]  # 9AM–5PM


@router.get("/availability/{slug}")
def get_availability(slug: str, date: str, db: Session = Depends(get_db)):
    profile = get_profile_by_slug(db, slug)
    if not profile:
        raise HTTPException(404, "Profile not found")

    try:
        date_obj = datetime.strptime(date, "%Y-%m-%d").date()
    except:
        raise HTTPException(400, "Invalid date")

    available_slots = []
    duration = timedelta(minutes=profile.duration_minutes)

    for slot_time in TIME_SLOTS:
        start_dt = datetime.combine(date_obj, slot_time)
        end_dt = start_dt + duration

        # Overlap check
        booking_exists = db.query(Booking).filter(
            Booking.profile_id == profile.id,
            Booking.start_time < end_dt,
            Booking.end_time > start_dt
        ).first()

        available_slots.append({
            "time": slot_time.strftime("%H:%M"),
            "available": booking_exists is None
        })

    return {"date": date, "slots": available_slots}
