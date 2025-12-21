# from fastapi import APIRouter, HTTPException
# from pydantic import BaseModel
# from google.oauth2 import id_token
# from google.auth.transport import requests
# import os

# router = APIRouter(prefix="/auth", tags=["Auth"])

# class TokenRequest(BaseModel):
#     token: str

# @router.post("/google")
# async def google_auth(data: TokenRequest):
#     try:
#         id_info = id_token.verify_oauth2_token(
#             data.token,
#             requests.Request(),
#             os.getenv("GOOGLE_CLIENT_ID")
#         )

#         email = id_info.get("email")
#         name = id_info.get("name")
#         picture = id_info.get("picture")

#         # TODO: store user in DB here
#         return {
#             "status": "success",
#             "email": email,
#             "name": name,
#             "picture": picture
#         }

#     except Exception:
#         raise HTTPException(status_code=400, detail="Invalid Google token")



from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import os
import requests
from sqlalchemy.orm import Session
from ..database import get_db
from ..services.user_service import get_user_by_sub, create_user, store_refresh_token

router = APIRouter(prefix="/auth", tags=["auth"])

class GoogleCodePayload(BaseModel):
    code: str

@router.post("/google")
def google_auth(payload: GoogleCodePayload, db: Session = Depends(get_db)):

    # STEP 1 — Exchange code for tokens
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": payload.code,
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),  # MUST MATCH GOOGLE CONSOLE
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
        "redirect_uri": "http://localhost:3000/auth/google/callback",
        "grant_type": "authorization_code"
    }

    token_res = requests.post(token_url, data=data)
    print("🔍 GOOGLE TOKEN RESPONSE:", token_res.text)

    token_response = token_res.json()

    if "error" in token_response:
        raise HTTPException(status_code=400, detail=token_response["error"])

    access_token = token_response["access_token"]
    refresh_token = token_response.get("refresh_token")

    # STEP 2 — Fetch Google user info
    userinfo = requests.get(
        "https://www.googleapis.com/oauth2/v2/userinfo",
        headers={"Authorization": f"Bearer {access_token}"}
    ).json()

    email = userinfo["email"]
    name = userinfo["name"]
    picture = userinfo.get("picture")
    sub = userinfo["id"]

    # STEP 3 — Save or get user
    user = get_user_by_sub(db, sub)
    if not user:
        user = create_user(db, name, email, picture, sub)

    # STEP 4 — Save refresh token if present
    if refresh_token:
        store_refresh_token(db, user.id, refresh_token)

    # STEP 5 — RETURN FULL USER PROFILE (REQUIRED FOR DASHBOARD)
    return {
        "sub": user.google_sub,
        "name": user.name,
        "email": user.email,
        "picture": user.picture,
        "avatar_url": user.picture,

        # These may not exist in User → so use getattr()
        "username": getattr(user, "username", None),
        "profile_title": getattr(user, "profile_title", None),
        "host_name": getattr(user, "host_name", None),
        "timezone": getattr(user, "timezone", None),
        "slug": getattr(user, "slug", None),
        "has_booking_profile": bool(getattr(user, "slug", None))
    }


@router.get("/calendar-status")
def calendar_status(user_sub: str, db: Session = Depends(get_db)):
    user = get_user_by_sub(db, user_sub)
    if not user:
        raise HTTPException(404, "User not found")

    return {
        "calendar_connected": bool(user.refresh_token_enc)
    }

