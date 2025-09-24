from pydantic import BaseModel, ConfigDict
from typing import Optional


class UserBase(BaseModel):
    age: int
    gender: str
    streak: Optional[int] = 0

    model_config = ConfigDict(from_attributes=True)


class ComplaintBase(BaseModel):
    user_id: int
    location_lat: float
    location_lon: float
    description: str
    category: str
    timestamp: str
    status: str

    model_config = ConfigDict(from_attributes=True)


class TripRequestBase(BaseModel):
    user_id: int
    latitude: float
    longitude: float
    speed: float
    timestamp: str

    model_config = ConfigDict(from_attributes=True)


class JourneyBase(BaseModel):
    id: int
    origin: str
    destination: str
    start_time: str
    end_time: str
    purpose: Optional[str] = None
    is_verified_by_user: Optional[bool] = False

    model_config = ConfigDict(from_attributes=True)


class LocationBase(BaseModel):
    latitude: float
    longitude: float
    name: str

    model_config = ConfigDict(from_attributes=True)


class NatpacResponseBase(BaseModel):
    trip_id: int
    user_id: int
    user_gender: str
    user_age: int
    journey_id: int
    origin: LocationBase
    destination: LocationBase
    start_time: str
    end_time: str
    mode: str
    distance_travelled: float
    co_travellers: int
    is_verified_by_user: bool

    model_config = ConfigDict(from_attributes=True)
