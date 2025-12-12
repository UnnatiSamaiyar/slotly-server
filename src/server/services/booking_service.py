# import os
# from datetime import datetime, timedelta
# import requests
# from sqlalchemy.orm import Session
# from ..models.booking import Booking, BookingProfile
# from ..models.user import User
# from ..utils.crypto import decrypt_token  # your existing fernet functions
# from ..database import SessionLocal
# from typing import Optional

# GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
# GOOGLE_CALENDAR_EVENTS_URL = "https://www.googleapis.com/calendar/v3/calendars/primary/events"

# def create_booking_record(db: Session, profile: BookingProfile, guest_name: str, guest_email: str, start_dt: datetime, end_dt: datetime, google_event_id: Optional[str]=None):
#     b = Booking(
#         profile_id=profile.id,
#         guest_name=guest_name,
#         guest_email=guest_email,
#         start_time=start_dt,
#         end_time=end_dt,
#         google_event_id=google_event_id
#     )
#     db.add(b)
#     db.commit()
#     db.refresh(b)
#     return b

# def exchange_refresh_for_access(refresh_token: str, client_id: str, client_secret: str) -> dict:
#     data = {
#         "client_id": client_id,
#         "client_secret": client_secret,
#         "refresh_token": refresh_token,
#         "grant_type": "refresh_token"
#     }
#     r = requests.post(GOOGLE_TOKEN_URL, data=data, timeout=15)
#     r.raise_for_status()
#     return r.json()

# def create_google_event_for_host(db: Session, host_user: User, summary: str, description: str, start_dt: datetime, end_dt: datetime, attendees: list = None):
#     """
#     Uses stored encrypted refresh token to get access token and create an event in host's primary calendar.
#     Returns created event object (dict) or raises.
#     """
#     if not host_user.refresh_token_enc:
#         raise Exception("No refresh token for host")

#     # decrypt stored refresh token (your encrypt/decrypt util)
#     refresh_token = decrypt_token(host_user.refresh_token_enc)

#     tokens = exchange_refresh_for_access(refresh_token, os.getenv("GOOGLE_CLIENT_ID"), os.getenv("GOOGLE_CLIENT_SECRET"))
#     access_token = tokens.get("access_token")
#     if not access_token:
#         raise Exception("Failed to obtain access token")

#     event_payload = {
#         "summary": summary,
#         "description": description,
#         "start": {"dateTime": start_dt.isoformat()},
#         "end": {"dateTime": end_dt.isoformat()},
#         "attendees": attendees or [],
#         "conferenceData": {"createRequest": {"requestId": f"slotly-{int(datetime.utcnow().timestamp())}"}}
#     }

#     headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
#     params = {"conferenceDataVersion": 1}
#     r = requests.post(GOOGLE_CALENDAR_EVENTS_URL + "?sendUpdates=all", json=event_payload, headers=headers, params=params, timeout=15)
#     r.raise_for_status()
#     return r.json()

# def get_profile_by_slug(db: Session, slug: str) -> BookingProfile:
#     return db.query(BookingProfile).filter(BookingProfile.slug == slug).first()

















# import os
# from datetime import datetime, timedelta
# import requests
# from sqlalchemy.orm import Session
# from ..models.booking import Booking
# from ..models.booking_profile import BookingProfile

# from ..models.user import User
# from ..utils.crypto import decrypt_token
# from typing import Optional

# GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
# GOOGLE_CALENDAR_EVENTS_URL = "https://www.googleapis.com/calendar/v3/calendars/primary/events"


# def create_booking_record(
#     db: Session,
#     profile: BookingProfile,
#     guest_name: str,
#     guest_email: str,
#     start_dt: datetime,
#     end_dt: datetime,
#     google_event_id: Optional[str] = None,
#     title: Optional[str] = None,
#     timezone: Optional[str] = None
# ):
#     """
#     Create and persist a booking record.

#     This function is backward-compatible: title and timezone are optional.
#     If title is not provided, it falls back to profile.title.
#     Status is set to 'pending' by default.
#     """
#     b = Booking(
#         profile_id=profile.id,
#         guest_name=guest_name,
#         guest_email=guest_email,
#         start_time=start_dt,
#         end_time=end_dt,
#         google_event_id=google_event_id,
#         title=title or profile.title,
#         timezone=timezone,
#         status="pending"
#     )
#     db.add(b)
#     db.commit()
#     db.refresh(b)
#     return b


# def exchange_refresh_for_access(refresh_token: str, client_id: str, client_secret: str) -> dict:
#     data = {
#         "client_id": client_id,
#         "client_secret": client_secret,
#         "refresh_token": refresh_token,
#         "grant_type": "refresh_token"
#     }
#     r = requests.post(GOOGLE_TOKEN_URL, data=data, timeout=15)
#     r.raise_for_status()
#     return r.json()


# def create_google_event_for_host(
#     db: Session,
#     host_user: User,
#     summary: str,
#     description: str,
#     start_dt: datetime,
#     end_dt: datetime,
#     attendees: list = None
# ):
#     """
#     Creates Google Calendar event in host's calendar using refresh token.
#     Auto-accepts attendees to avoid the "Yes? Maybe?" confirmation popup.
#     Returns the created event JSON.
#     """

#     if not host_user.refresh_token_enc:
#         raise Exception("No refresh token for host")

#     refresh_token = decrypt_token(host_user.refresh_token_enc)

#     tokens = exchange_refresh_for_access(
#         refresh_token,
#         os.getenv("GOOGLE_CLIENT_ID"),
#         os.getenv("GOOGLE_CLIENT_SECRET")
#     )

#     access_token = tokens.get("access_token")
#     if not access_token:
#         raise Exception("Failed to obtain access token")

#     # --- AUTO ACCEPT ATTENDEE FIX ✔ ---
#     fixed_attendees = []
#     if attendees:
#         for at in attendees:
#             fixed_attendees.append({
#                 "email": at.get("email"),
#                 "responseStatus": "accepted"     # <- KEY FIX
#             })

#     event_payload = {
#         "summary": summary,
#         "description": description,
#         "start": {"dateTime": start_dt.isoformat()},
#         "end": {"dateTime": end_dt.isoformat()},
#         "attendees": fixed_attendees,
#         "conferenceData": {
#             "createRequest": {
#                 "requestId": f"slotly-{int(datetime.utcnow().timestamp())}"
#             }
#         }
#     }

#     headers = {
#         "Authorization": f"Bearer {access_token}",
#         "Content-Type": "application/json"
#     }

#     params = {"conferenceDataVersion": 1}

#     # Use sendUpdates=all so guests receive notifications and responses propagate
#     r = requests.post(
#         GOOGLE_CALENDAR_EVENTS_URL + "?sendUpdates=all",
#         json=event_payload,
#         headers=headers,
#         params=params,
#         timeout=15
#     )
#     r.raise_for_status()
#     return r.json()


# def get_profile_by_slug(db: Session, slug: str) -> BookingProfile:
#     return db.query(BookingProfile).filter(BookingProfile.slug == slug).first()











# import os
# from datetime import datetime, timedelta
# import requests
# from sqlalchemy.orm import Session
# from ..models.booking import Booking
# from ..models.booking_profile import BookingProfile

# from ..models.user import User
# from ..utils.crypto import decrypt_token
# from typing import Optional, List

# GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
# GOOGLE_CALENDAR_EVENTS_URL = "https://www.googleapis.com/calendar/v3/calendars/primary/events"


# def create_booking_record(
#     db: Session,
#     profile: BookingProfile,
#     guest_name: str,
#     attendee_emails: List[str],            # ⭐ NOW SUPPORTS MULTIPLE EMAILS
#     start_dt: datetime,
#     end_dt: datetime,
#     google_event_id: Optional[str] = None,
#     title: Optional[str] = None,
#     timezone: Optional[str] = None
# ):
#     """
#     Create and persist a booking record.
#     Only the first attendee is stored in guest_email for backward compatibility.
#     """

#     primary_email = attendee_emails[0] if attendee_emails else None

#     b = Booking(
#         profile_id=profile.id,
#         guest_name=guest_name,
#         guest_email=primary_email,         # ⭐ STORE FIRST ATTENDEE ONLY
#         start_time=start_dt,
#         end_time=end_dt,
#         google_event_id=google_event_id,
#         title=title or profile.title,
#         timezone=timezone,
#         status="pending"
#     )
#     db.add(b)
#     db.commit()
#     db.refresh(b)
#     return b


# def exchange_refresh_for_access(refresh_token: str, client_id: str, client_secret: str) -> dict:
#     data = {
#         "client_id": client_id,
#         "client_secret": client_secret,
#         "refresh_token": refresh_token,
#         "grant_type": "refresh_token"
#     }
#     r = requests.post(GOOGLE_TOKEN_URL, data=data, timeout=15)
#     r.raise_for_status()
#     return r.json()


# def create_google_event_for_host(
#     db: Session,
#     host_user: User,
#     summary: str,
#     description: str,
#     start_dt: datetime,
#     end_dt: datetime,
#     attendees: list = None
# ):
#     """
#     Creates Google Calendar event in host's calendar with multi-attendee support.
#     FIXED VERSION — ensures Google never rewrites the title.
#     """

#     if not host_user.refresh_token_enc:
#         raise Exception("No refresh token for host")

#     refresh_token = decrypt_token(host_user.refresh_token_enc)

#     tokens = exchange_refresh_for_access(
#         refresh_token,
#         os.getenv("GOOGLE_CLIENT_ID"),
#         os.getenv("GOOGLE_CLIENT_SECRET")
#     )

#     access_token = tokens.get("access_token")
#     if not access_token:
#         raise Exception("Failed to obtain access token")

#     # MULTIPLE ATTENDEE SUPPORT
#     fixed_attendees = []
#     if attendees:
#         for at in attendees:
#             fixed_attendees.append({
#                 "email": at.get("email"),
#                 "responseStatus": "accepted"
#             })

#     # ⭐⭐ FINAL GOOGLE TITLE FIX ⭐⭐
#     event_payload = {
#         "summary": summary,                     # ← FORCES CORRECT TITLE ALWAYS
#         "location": "",                         # ← PREVENTS GOOGLE AUTO TITLE
#         "description": description,

#         "start": {
#             "dateTime": start_dt.isoformat(),
#             "timeZone": "UTC"                   # ← FIX: prevents auto adjustment
#         },

#         "end": {
#             "dateTime": end_dt.isoformat(),
#             "timeZone": "UTC"
#         },

#         "attendees": fixed_attendees,

#         "guestsCanModify": False,               # ← prevents Google overwriting
#         "guestsCanInviteOthers": False,
#         "reminders": {"useDefault": True},

#         "conferenceData": {
#             "createRequest": {
#                 "requestId": f"slotly-{int(datetime.utcnow().timestamp())}"
#             }
#         }
#     }

#     headers = {
#         "Authorization": f"Bearer {access_token}",
#         "Content-Type": "application/json",
#     }

#     params = {"conferenceDataVersion": 1}

#     r = requests.post(
#         GOOGLE_CALENDAR_EVENTS_URL + "?sendUpdates=all",
#         json=event_payload,
#         headers=headers,
#         params=params,
#         timeout=15
#     )

#     r.raise_for_status()
#     return r.json()


# def get_profile_by_slug(db: Session, slug: str) -> BookingProfile:
#     return db.query(BookingProfile).filter(BookingProfile.slug == slug).first()









import os
from datetime import datetime, timedelta
import requests
from sqlalchemy.orm import Session
from typing import Optional, List

from ..models.booking import Booking
from ..models.booking_profile import BookingProfile
from ..models.user import User
from ..utils.crypto import decrypt_token


GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_CALENDAR_EVENTS_URL = "https://www.googleapis.com/calendar/v3/calendars/primary/events"


# --------------------------
# 1️⃣ Create booking record
# --------------------------
# def create_booking_record(
#     db: Session,
#     profile: BookingProfile,
#     guest_name: str,
#     attendee_emails: List[str],
#     start_dt: datetime,
#     end_dt: datetime,
#     google_event_id: Optional[str] = None,
#     title: Optional[str] = None,
#     timezone: Optional[str] = None,
#     meeting_mode: str = "google_meet",
#     location: Optional[str] = None
# ):
#     primary_email = attendee_emails[0] if attendee_emails else None

#     b = Booking(
#         profile_id=profile.id,
#         guest_name=guest_name,
#         guest_email=primary_email,
#         start_time=start_dt,
#         end_time=end_dt,
#         google_event_id=google_event_id,
#         title=title or profile.title,
#         timezone=timezone,
#         status="pending",
#         meeting_mode=meeting_mode,
#         location=location
#     )

#     db.add(b)
#     db.commit()
#     db.refresh(b)
#     return b


def create_booking_record(
    db: Session,
    profile: BookingProfile,
    guest_name: str,
    attendee_emails: List[str],     # ✔ FULL LIST
    start_dt: datetime,
    end_dt: datetime,
    google_event_id: Optional[str] = None,
    title: Optional[str] = None,
    timezone: Optional[str] = None,
    meeting_mode: str = "google_meet",
    location: Optional[str] = None
):
    """
    Store booking details.
    attendee_emails → list of all attendee emails
    primary_email → first email only (DB backward compatibility)
    """

    primary_email = attendee_emails[0] if attendee_emails else None

    b = Booking(
        profile_id=profile.id,
        guest_name=guest_name,
        guest_email=primary_email,   # ✔ store only the first attendee
        start_time=start_dt,
        end_time=end_dt,
        google_event_id=google_event_id,
        title=title or profile.title,
        timezone=timezone,
        status="pending",

        # NEW FIELDS
        meeting_mode=meeting_mode,
        location=location
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
    event_payload = {
        "summary": summary,
        "description": description,
        "start": {"dateTime": start_dt.isoformat(), "timeZone": "UTC"},
        "end": {"dateTime": end_dt.isoformat(), "timeZone": "UTC"},
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
def get_profile_by_slug(db: Session, slug: str) -> BookingProfile:
    return db.query(BookingProfile).filter(BookingProfile.slug == slug).first()
