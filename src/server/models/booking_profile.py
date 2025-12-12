# from sqlalchemy import Column, Integer, String, ForeignKey
# from sqlalchemy.orm import relationship
# from ..database import Base

# class BookingProfile(Base):
#     __tablename__ = "booking_profiles"

#     id = Column(Integer, primary_key=True, index=True)
#     user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

#     title = Column(String)
#     slug = Column(String, unique=True, index=True)
#     duration = Column(Integer)
#     timezone = Column(String)
#     description = Column(String)
#     availability = Column(String)  # JSON string

#     # FIX — REQUIRED so User.booking_profiles connects
#     user = relationship("User", back_populates="booking_profiles")










# # src/server/models/booking.py

# from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Text
# from sqlalchemy.orm import relationship
# from ..database import Base
# from datetime import datetime

# class BookingProfile(Base):
#     __tablename__ = "booking_profiles"

#     id = Column(Integer, primary_key=True, index=True)
#     slug = Column(String, unique=True, index=True, nullable=False)
#     user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))

#     # NEW fields for Event Types screen
#     title = Column(String, default="Meeting", nullable=False)
#     description = Column(Text, nullable=True)
#     duration_minutes = Column(Integer, default=30)

#     active = Column(Boolean, default=True)

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










# from sqlalchemy import Column, Integer, String, ForeignKey
# from sqlalchemy.orm import relationship
# from ..database import Base

# class BookingProfile(Base):
#     __tablename__ = "booking_profiles"

#     id = Column(Integer, primary_key=True, index=True)
#     user_id = Column(Integer, ForeignKey("users.id"))

#     title = Column(String, nullable=False)
#     duration_minutes = Column(Integer, nullable=False)
#     slug = Column(String, unique=True, nullable=False)

#     user = relationship("User", back_populates="booking_profiles")






from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from ..database import Base
from datetime import datetime

class BookingProfile(Base):
    __tablename__ = "booking_profiles"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    duration_minutes = Column(Integer, default=30)
    title = Column(String, default="Meeting")
    description = Column(String, nullable=True)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="booking_profiles")
