import os
from datetime import datetime, timedelta
import requests
from sqlalchemy.orm import Session
from typing import Optional, List

from ..models.booking import Booking
from ..models.booking_profile import BookingProfile
from ..models.user import User
from ..utils.crypto import decrypt_token
import json


GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_CALENDAR_EVENTS_URL = "https://www.googleapis.com/calendar/v3/calendars/primary/events"




def create_booking_record(
    db: Session,
    profile: BookingProfile,
    guest_name: str,
    attendee_emails: List[str],
    start_dt: datetime,
    end_dt: datetime,
    google_event_id: Optional[str] = None,
    title: Optional[str] = None,
    timezone: Optional[str] = None,
    meeting_mode: str = "google_meet",
    location: Optional[str] = None,
    meet_link: Optional[str] = None,          # ✅ new
):
    primary_email = attendee_emails[0] if attendee_emails else None

    b = Booking(
        profile_id=profile.id,
        guest_name=guest_name,
        guest_email=primary_email,
        start_time=start_dt,
        end_time=end_dt,
        google_event_id=google_event_id,
        title=title or profile.title,
        timezone=timezone,
        status="pending",
        meeting_mode=meeting_mode,
        location=location,

        meet_link=meet_link,                                   # ✅ new
        attendees_json=json.dumps(attendee_emails or []),       # ✅ new
    )

    db.add(b)
    db.commit()
    db.refresh(b)
    return b


# --------------------------
# 2️⃣ Exchange refresh token
# --------------------------
def exchange_refresh_for_access(refresh_token: str, client_id: str, client_secret: str) -> dict:
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }
    r = requests.post(GOOGLE_TOKEN_URL, data=data, timeout=15)
    r.raise_for_status()
    return r.json()


# --------------------------
# 3️⃣ Create Google Event
# --------------------------
def create_google_event_for_host(
    db: Session,
    host_user: User,
    summary: str,
    description: str,
    start_dt: datetime,
    end_dt: datetime,
    attendees: list = None,
    meeting_mode: str = "google_meet",
    location: Optional[str] = None
):

    if not host_user.refresh_token_enc:
        raise Exception("No refresh token for host")

    refresh_token = decrypt_token(host_user.refresh_token_enc)

    tokens = exchange_refresh_for_access(
        refresh_token,
        os.getenv("GOOGLE_CLIENT_ID"),
        os.getenv("GOOGLE_CLIENT_SECRET")
    )

    access_token = tokens.get("access_token")
    if not access_token:
        raise Exception("Failed to obtain access token")

    # ------------------------
    # FIX attendee format
    # ------------------------
    fixed_attendees = []
    if attendees:
        for at in attendees:
            if isinstance(at, str):
                fixed_attendees.append({"email": at, "responseStatus": "accepted"})
            else:
                fixed_attendees.append({
                    "email": at.get("email"),
                    "responseStatus": "accepted"
                })

    # ------------------------
    # BUILD EVENT PAYLOAD
    # ------------------------
    tz = "Asia/Kolkata"  # default
    event_tz = tz

    event_payload = {
        "summary": summary,
        "description": description,
        "start": {"dateTime": start_dt.isoformat(), "timeZone": event_tz},
        "end": {"dateTime": end_dt.isoformat(), "timeZone": event_tz},
        "attendees": fixed_attendees,
        "guestsCanModify": False,
        "guestsCanInviteOthers": False,
        "reminders": {"useDefault": True},
    }


    # Location support
    if meeting_mode == "in_person":
        event_payload["location"] = location or "In-person meeting"
    else:
        event_payload["location"] = ""

    # ------------------------
    # GOOGLE MEET SUPPORT
    # ------------------------
    if meeting_mode == "google_meet":
        event_payload["conferenceData"] = {
            "createRequest": {
                "requestId": f"slotly-{int(datetime.utcnow().timestamp())}"
            }
        }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    params = {"conferenceDataVersion": 1}

    try:
        r = requests.post(
            GOOGLE_CALENDAR_EVENTS_URL + "?sendUpdates=all",
            json=event_payload,
            headers=headers,
            params=params,
            timeout=15
        )
        r.raise_for_status()
        return r.json()

    except Exception as e:
        # SUPER DEBUG LOGGING
        print("❌ GOOGLE EVENT CREATION FAILED")
        print("Error Type:", type(e))
        print("Error:", str(e))
        try:
            print("Google Response:", r.text)
        except:
            pass
        return None


# --------------------------
# 4️⃣ Get profile by slug
# --------------------------
# --------------------------
# 4️⃣ Get profile by slug (robust + debug)
# --------------------------
def get_profile_by_slug(db: Session, slug: str) -> BookingProfile:
    """
    Robust lookup for booking profile by slug.
    Tries:
      1) exact match
      2) lower() match
      3) LIKE match (fuzzy)
    Adds debug prints so you can see what is returned in server logs.
    """
    if not slug:
        print("[booking_service] get_profile_by_slug called with empty slug")
        return None

    # 1) exact
    profile = db.query(BookingProfile).filter(BookingProfile.slug == slug).first()
    if profile:
        print(f"[booking_service] found profile by exact slug='{slug}' -> id={profile.id}")
        return profile

    # 2) case-insensitive
    try:
        profile = db.query(BookingProfile).filter(
            BookingProfile.slug.ilike(slug)
        ).first()
        if profile:
            print(f"[booking_service] found profile by ilike slug='{slug}' -> id={profile.id}")
            return profile
    except Exception as e:
        # some SQL backends may not support ilike on column types - ignore quietly
        print("[booking_service] ilike check failed:", e)

    # 3) fuzzy (contains)
    try:
        profile = db.query(BookingProfile).filter(
            BookingProfile.slug.like(f"%{slug}%")
        ).first()
        if profile:
            print(f"[booking_service] found profile by LIKE '%{slug}%' -> id={profile.id}")
            return profile
    except Exception as e:
        print("[booking_service] LIKE check failed:", e)

    # not found - print a helpful debug snapshot
    print(f"[booking_service] profile NOT found for slug='{slug}'. Inspecting first 10 rows:")
    try:
        rows = db.query(BookingProfile.id, BookingProfile.slug, BookingProfile.title).limit(10).all()
        for r in rows:
            print("  row:", r)
    except Exception as e:
        print("[booking_service] failed to dump booking_profiles:", e)

    return None



def extract_meet_link(event: dict | None) -> Optional[str]:
    if not event:
        return None

    # Most common
    if event.get("hangoutLink"):
        return event["hangoutLink"]

    # Sometimes available in conferenceData entryPoints
    conf = event.get("conferenceData") or {}
    for ep in conf.get("entryPoints") or []:
        if ep.get("entryPointType") == "video" and ep.get("uri"):
            return ep["uri"]

    return None
