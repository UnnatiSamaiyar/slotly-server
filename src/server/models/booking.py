from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
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

    meet_link = Column(Text, nullable=True)
    attendees_json = Column(Text, nullable=True)
