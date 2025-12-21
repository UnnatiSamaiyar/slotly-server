from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from ..database import get_db
from ..services.booking_service import (
    create_booking_record,
    create_google_event_for_host,
    get_profile_by_slug,
)
from ..services.user_service import get_user_by_id

from ..models.booking import Booking
from ..services.booking_service import extract_meet_link


router = APIRouter(prefix="/bookings", tags=["bookings"])


# ⭐ UPDATED PAYLOAD — supports meeting mode + location + attendees
class CreateBookingPayload(BaseModel):
    profile_slug: str
    guest_name: str
    attendees: List[EmailStr]  # multiple attendees
    start_iso: str
    title: Optional[str] = None
    timezone: Optional[str] = None

    meeting_mode: str = "google_meet"  # ⭐ new field
    location: Optional[str] = None  # ⭐ for in-person meetings


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
                meeting_mode=payload.meeting_mode,
                location=payload.location,
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
    meet_link = (
        extract_meet_link(event) if payload.meeting_mode == "google_meet" else None
    )

    booking = create_booking_record(
        db,
        profile,
        payload.guest_name,
        payload.attendees,  # store multiple attendees
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
        "meet_link": meet_link,  # ✅ new
        "attendees": payload.attendees,
    }
