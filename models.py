from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    Float,
    ForeignKey,
    Time,
    func,
)
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True)
    age = Column(Integer, nullable=False)
    gender = Column(String)
    consent_start_time = Column(Time, nullable=False)
    consent_end_time = Column(Time, nullable=False)
    streak = Column(Integer, default=0)

    trip = relationship("Trip", back_populates="user")
    complaint = relationship("Complaint", back_populates="user")


class TripMode(Base):
    __tablename__ = "trip_mode"
    id = Column(Integer, primary_key=True, index=True)
    mode_name = Column(String)

    trip = relationship("Trip", back_populates="mode")


class Trip(Base):
    __tablename__ = "trip"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    mode_id = Column(Integer, ForeignKey("trip_mode.id"))
    journey_id = Column(Integer, nullable=False)
    origin_lat = Column(Float, nullable=False)
    origin_lon = Column(Float, nullable=False)
    destination_lat = Column(Float, nullable=False)
    destination_lon = Column(Float, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    distance_travelled = Column(Float, nullable=False)
    co_travellers = Column(Integer, default=0)
    is_verified_by_user = Column(Boolean, default=False)

    user = relationship("User", back_populates="trip")
    mode = relationship("TripMode", back_populates="trip")


class Complaint(Base):
    __tablename__ = "complaint"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    location_lat = Column(Float, nullable=False)
    location_lon = Column(Float, nullable=False)
    description = Column(String, nullable=False)
    category = Column(String)
    timestamp = Column(DateTime, default=func.now())
    status = Column(String)

    user = relationship("User", back_populates="complaint")
