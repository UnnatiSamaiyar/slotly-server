# src/server/routes/calendar.py
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Any, Dict, List
import os
import requests
from datetime import datetime, timezone

from ..database import get_db
from ..services.user_service import get_user_by_sub
from ..utils.crypto import decrypt_token

router = APIRouter(prefix="/auth", tags=["calendar"])

GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_CALENDAR_EVENTS = (
    "https://www.googleapis.com/calendar/v3/calendars/primary/events"
)
GOOGLE_CALENDARS_LIST = "https://www.googleapis.com/calendar/v3/users/me/calendarList"


def refresh_access_token(refresh_token: str) -> Dict[str, Any]:
    """
    Exchange refresh_token for a new access_token.
    """
    data = {
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }

    res = requests.post(GOOGLE_TOKEN_URL, data=data, timeout=10)
    if res.status_code != 200:
        raise HTTPException(
            status_code=502, detail=f"Google token refresh failed: {res.text}"
        )
    return res.json()


@router.get("/calendar/events")
def get_calendar_events(
    user_sub: str, db: Session = Depends(get_db), max_results: int = 50
):
    """
    Return upcoming events for user's primary calendar.
    Query params:
      - user_sub (required) : google sub (identifier) for the user
      - max_results (optional) : maximum events to fetch
    """
    user = get_user_by_sub(db, user_sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user.refresh_token_enc:
        return {"calendar_connected": False, "events": []}

    # decrypt refresh token
    try:
        refresh_token = decrypt_token(user.refresh_token_enc)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to decrypt refresh token: {str(e)}"
        )

    # exchange refresh token for access token
    token_data = refresh_access_token(refresh_token)
    access_token = token_data.get("access_token")
    if not access_token:
        raise HTTPException(status_code=502, detail="No access token from Google")

    # fetch events. use RFC3339 now to get only future events
    now_iso = datetime.now(timezone.utc).isoformat()
    params = {
        "maxResults": max_results,
        "orderBy": "startTime",
        "singleEvents": "true",
        "timeMin": now_iso,
    }
    headers = {"Authorization": f"Bearer {access_token}"}

    events_res = requests.get(
        GOOGLE_CALENDAR_EVENTS, headers=headers, params=params, timeout=10
    )
    if events_res.status_code != 200:
        raise HTTPException(
            status_code=502, detail=f"Google calendar fetch failed: {events_res.text}"
        )

    events_payload = events_res.json()
    items = events_payload.get("items", [])

    # simplify the events to fields your UI will use
    def simplify(evt):
        start = evt.get("start", {})
        end = evt.get("end", {})

        # extract attendees
        attendees = [a.get("email") for a in evt.get("attendees", []) if a.get("email")]

        # extract Google Meet link
        meet_link = None
        conference = evt.get("conferenceData", {})
        for ep in conference.get("entryPoints", []):
            if ep.get("entryPointType") == "video":
                meet_link = ep.get("uri")
                break

        return {
            "id": evt.get("id"),
            "summary": evt.get("summary") or "No title",
            "start": start.get("dateTime") or start.get("date"),
            "end": end.get("dateTime") or end.get("date"),
            "location": evt.get("location"),
            "htmlLink": evt.get("htmlLink"),
            "organizer": evt.get("organizer", {}).get("email"),
            # ✅ NEW
            "attendees": attendees,
            "meetLink": meet_link,
        }

    simplified = [simplify(i) for i in items]
    return {"calendar_connected": True, "events": simplified}


@router.get("/calendar/list")
def list_calendars(user_sub: str, db: Session = Depends(get_db)):
    """
    Return list of calendars for the user (calendar list).
    """
    user = get_user_by_sub(db, user_sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user.refresh_token_enc:
        return {"calendar_connected": False, "calendars": []}

    try:
        refresh_token = decrypt_token(user.refresh_token_enc)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to decrypt refresh token: {str(e)}"
        )

    token_data = refresh_access_token(refresh_token)
    access_token = token_data.get("access_token")
    if not access_token:
        raise HTTPException(status_code=502, detail="No access token from Google")

    headers = {"Authorization": f"Bearer {access_token}"}
    res = requests.get(GOOGLE_CALENDARS_LIST, headers=headers, timeout=10)
    if res.status_code != 200:
        raise HTTPException(
            status_code=502, detail=f"Google calendar list failed: {res.text}"
        )

    payload = res.json()
    items = payload.get("items", [])
    simple = [{"id": i.get("id"), "summary": i.get("summary")} for i in items]
    return {"calendar_connected": True, "calendars": simple}


@router.post("/create")
def create_event(data: dict, db: Session = Depends(get_db)):
    user = get_user_by_sub(db, data["user_sub"])
    if not user:
        raise HTTPException(404, "User not found")

    refresh = user.refresh_token_enc
    access_token = refresh_to_access(refresh)

    event_body = {
        "summary": data["title"],
        "description": data.get("description", ""),
        "start": {"dateTime": data["start"], "timeZone": "Asia/Kolkata"},
        "end": {
            "dateTime": add_minutes_to_iso(data["start"], data["duration"]),
            "timeZone": "Asia/Kolkata",
        },
        "attendees": [{"email": data["invitee_email"]}],
    }

    google_res = requests.post(
        "https://www.googleapis.com/calendar/v3/calendars/primary/events",
        headers={"Authorization": f"Bearer {access_token}"},
        json=event_body,
    ).json()

    return {"status": "success", "event": google_res}
