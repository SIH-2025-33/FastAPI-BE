from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    func,
)
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True)
    age = Column(Integer, nullable=False)
    gender = Column(String)
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
    journey_id = Column(Integer, ForeignKey("journey.id", ondelete="CASCADE"))
    origin_location_id = Column(Integer, ForeignKey("location_points.id"))
    destination_location_id = Column(Integer, ForeignKey("location_points.id"))
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    distance_travelled = Column(Float, nullable=False)
    co_travellers = Column(Integer, default=0)

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
    trip_journey = relationship("Journey", back_populates="trips")


class Journey(Base):
    __tablename__ = "journey"
    id = Column(Integer, primary_key=True, index=True)
    origin = Column(String)
    destination = Column(String)
    purpose = Column(String)
    is_verified_by_user = Column(Boolean, default=False)

    trips = relationship("Trip", back_populates="trip_journey")


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


class DataCollector(Base):
    __tablename__ = "data_collector"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    speed = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=func.now())
