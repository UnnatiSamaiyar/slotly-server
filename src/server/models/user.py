# from sqlalchemy import Column, Integer, String
# from sqlalchemy.orm import relationship
# from ..database import Base

# class User(Base):
#     __tablename__ = "users"

#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String)
#     email = Column(String, unique=True, index=True)
#     picture = Column(String)
#     google_sub = Column(String, unique=True, index=True)
#     refresh_token_enc = Column(String, nullable=True)

#     # NEW — required for Booking Profiles
#     booking_profiles = relationship("BookingProfile", back_populates="user")

#     # If you created event types earlier:
#     event_types = relationship("EventType", back_populates="user", cascade="all, delete-orphan")










# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from ..database import get_db
# from ..services.user_service import get_user_by_sub
# from ..models.user import User

# router = APIRouter(prefix="/user", tags=["user"])


# @router.get("/me")
# def get_me(user_sub: str, db: Session = Depends(get_db)):
#     """
#     Returns full user profile + booking profile
#     """
#     user: User = get_user_by_sub(db, user_sub)
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")

#     # 📌 Booking Profile (one user can have multiple profiles, we take the first)
#     primary_profile = user.booking_profiles[0] if user.booking_profiles else None

#     return {
#         "sub": user.google_sub,
#         "name": user.name,
#         "email": user.email,
#         "picture": user.picture,
#         "avatar_url": user.picture,

#         # Username = before @ (customize as needed)
#         "username": user.email.split("@")[0],

#         # 👇 Include Booking Profile Data
#         "profile_title": primary_profile.title if primary_profile else None,
#         "host_name": primary_profile.host_name if primary_profile else None,
#         "timezone": primary_profile.timezone if primary_profile else None,
#         "slug": primary_profile.slug if primary_profile else None,

#         # For UI conditional rendering
#         "has_booking_profile": primary_profile is not None
#     }





from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from ..database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    picture = Column(String)
    google_sub = Column(String, unique=True, index=True)
    refresh_token_enc = Column(String, nullable=True)

    booking_profiles = relationship("BookingProfile", back_populates="user")
    event_types = relationship("EventType", back_populates="user", cascade="all, delete-orphan")
