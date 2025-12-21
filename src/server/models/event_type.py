from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from ..database import Base

class EventType(Base):
    __tablename__ = "event_types"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    title = Column(String, nullable=False)            # "30 min Meeting"
    slug = Column(String, unique=True, nullable=False) # /u/tushar/30-min-meet
    duration = Column(Integer, nullable=False)         # minutes
    location = Column(String, nullable=True)           # google_meet, zoom, phone

    availability_json = Column(Text, nullable=True)    # JSON for availability rules

    user = relationship("User", back_populates="event_types")
