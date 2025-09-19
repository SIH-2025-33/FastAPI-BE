from pydantic import BaseModel, ConfigDict
from typing import Optional


class UserBase(BaseModel):
    age: int
    gender: str
    consent_start_time: str
    consent_end_time: str
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
    latitude: float
    longitude: float
    speed: float
    timestamp: str

    model_config = ConfigDict(from_attributes=True)


class ModeResponseBase(BaseModel):
    trip_id: int
    mode_name: str

    model_config = ConfigDict(from_attributes=True)