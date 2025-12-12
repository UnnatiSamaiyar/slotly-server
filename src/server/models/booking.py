# from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
# from sqlalchemy.orm import relationship
# from ..database import Base
# from datetime import datetime

# class BookingProfile(Base):
#     __tablename__ = "booking_profiles"

#     id = Column(Integer, primary_key=True, index=True)
#     slug = Column(String, unique=True, index=True, nullable=False)
#     user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
#     duration_minutes = Column(Integer, default=30)
#     title = Column(String, default="Meeting")
#     created_at = Column(DateTime, default=datetime.utcnow)

#     user = relationship("User", back_populates="booking_profiles")


# class Booking(Base):
#     __tablename__ = "bookings"

#     id = Column(Integer, primary_key=True, index=True)
#     profile_id = Column(Integer, ForeignKey("booking_profiles.id", ondelete="CASCADE"))
#     guest_name = Column(String, nullable=False)
#     guest_email = Column(String, nullable=False)
#     start_time = Column(DateTime, nullable=False)
#     end_time = Column(DateTime, nullable=False)
#     google_event_id = Column(String, nullable=True)
#     created_at = Column(DateTime, default=datetime.utcnow)

#     profile = relationship("BookingProfile")






from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("booking_profiles.id"), nullable=False)

    guest_name = Column(String, nullable=False)
    guest_email = Column(String, nullable=False)

    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)

    google_event_id = Column(String, nullable=True)

    title = Column(String, nullable=True)
    timezone = Column(String, nullable=True)

    status = Column(String, default="pending")

    # ⭐⭐ NEW FIELDS ⭐⭐
    meeting_mode = Column(String, default="google_meet")     # "google_meet" or "in_person"
    location = Column(String, nullable=True)                 # Physical address if in-person

    profile = relationship("BookingProfile")
