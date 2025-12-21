from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from ..database import get_db
from ..services.user_service import get_user_by_sub
from ..services.booking_service import (
    create_booking_record,
    create_google_event_for_host,
    extract_meet_link,
)
from ..models.booking import Booking

router = APIRouter(prefix="/bookings", tags=["bookings"])


class CreateBookingPayload(BaseModel):
    guest_name: str
    attendees: List[EmailStr]
    start_iso: str
    title: Optional[str] = None
    timezone: Optional[str] = None
    meeting_mode: str = "google_meet"
    location: Optional[str] = None


@router.post("/create")
def create_booking(user_sub: str, payload: CreateBookingPayload, db: Session = Depends(get_db)):
    user = get_user_by_sub(db, user_sub)
    if not user:
        raise HTTPException(404, "User not found")

    profile = user.booking_profiles[0] if user.booking_profiles else None
    if not profile:
        raise HTTPException(404, "Profile not found")

    host_user = user  # ✅ host is the same logged-in user

    try:
        start_dt = datetime.fromisoformat(payload.start_iso.replace("Z", "+00:00"))
    except:
        raise HTTPException(400, "Invalid start time format")

    end_dt = start_dt + timedelta(minutes=profile.duration_minutes)

    conflict = (
        db.query(Booking)
        .filter(
            Booking.profile_id == profile.id,
            Booking.start_time < end_dt,
            Booking.end_time > start_dt,
        )
        .first()
    )
    if conflict:
        raise HTTPException(409, "This time slot is already booked.")

    final_title = payload.title or profile.title
    attendees = [{"email": email} for email in payload.attendees]

    event = None
    google_event_id = None

    if payload.meeting_mode == "google_meet":
        try:
            event = create_google_event_for_host(
                db,
                host_user,
                final_title,
                f"Booking by {payload.guest_name}",
                start_dt,
                end_dt,
                attendees=attendees,
                meeting_mode=payload.meeting_mode,
                location=payload.location,
            )
            google_event_id = event.get("id")
        except Exception as e:
            print("Google event creation failed:", e)
            event = None
            google_event_id = None

    meet_link = extract_meet_link(event) if event else None

    booking = create_booking_record(
        db,
        profile,
        payload.guest_name,
        payload.attendees,
        start_dt,
        end_dt,
        google_event_id,
        title=final_title,
        timezone=payload.timezone,
        meeting_mode=payload.meeting_mode,
        location=payload.location,
        meet_link=meet_link,
    )

    return {
        "status": "ok",
        "booking_id": booking.id,
        "google_event_id": google_event_id,
        "meeting_mode": payload.meeting_mode,
        "meet_link": meet_link,
        "attendees": payload.attendees,
    }
