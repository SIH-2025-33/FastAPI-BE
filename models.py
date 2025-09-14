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

    trips = relationship("Trip", back_populates="user")
    complaints = relationship("Complaint", back_populates="user")


class TripMode(Base):
    __tablename__ = "trip_mode"
    id = Column(Integer, primary_key=True, index=True)
    mode_name = Column(String)

    trip = relationship("Trip", back_populates="mode")
    estimated_routes = relationship("EstimatedRouteTime", back_populates="mode")


class LocationPoints(Base):
    __tablename__ = "location_points"
    id = Column(Integer, primary_key=True, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    location_name = Column(String)

    origin_trips = relationship(
        "Trip",
        foreign_keys="[Trip.origin_location_id]",
        back_populates="origin_location",
    )
    destination_trips = relationship(
        "Trip",
        foreign_keys="[Trip.destination_location_id]",
        back_populates="destination_location",
    )


class EstimatedRouteTime(Base):
    __tablename__ = "estimated_route_time"
    id = Column(Integer, primary_key=True, index=True)
    origin_location_id = Column(Integer, ForeignKey("location_points.id"))
    destination_location_id = Column(Integer, ForeignKey("location_points.id"))
    mode_id = Column(Integer, ForeignKey("trip_mode.id"))
    estimated_duration_minutes = Column(Float)

    mode = relationship("TripMode", back_populates="estimated_routes")
    origin_location = relationship("LocationPoints", foreign_keys=[origin_location_id])
    destination_location = relationship(
        "LocationPoints", foreign_keys=[destination_location_id]
    )


class Trip(Base):
    __tablename__ = "trip"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    mode_id = Column(Integer, ForeignKey("trip_mode.id"))
    journey_id = Column(Integer, nullable=False)
    origin_location_id = Column(Integer, ForeignKey("location_points.id"))
    destination_location_id = Column(Integer, ForeignKey("location_points.id"))
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    distance_travelled = Column(Float, nullable=False)
    co_travellers = Column(Integer, default=0)
    is_verified_by_user = Column(Boolean, default=False)

    user = relationship("User", back_populates="trips")
    mode = relationship("TripMode", back_populates="trip")
    origin_location = relationship(
        "LocationPoints",
        foreign_keys=[origin_location_id],
        back_populates="origin_trips",
    )
    destination_location = relationship(
        "LocationPoints",
        foreign_keys=[destination_location_id],
        back_populates="destination_trips",
    )


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

    user = relationship("User", back_populates="complaints")
