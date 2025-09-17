from pydantic import BaseModel, ConfigDict
from datetime import time
from typing import Optional


class UserBase(BaseModel):
    age: int
    gender: str
    consent_start_time: time
    consent_end_time: time
    streak: Optional[int] = 0

    model_config = ConfigDict(from_attributes=True)

class ComplaintBase(BaseModel):
    user_id: int
    location_lat: float
    location_lon: float
    description: str
    category: str
    timestamp: time
    status: str

class TripRequestBase(BaseModel):
    latitude: float
    longitude: float
    speed: float
    timestamp: time


class ModeResponseBase(BaseModel):
    trip_id: id
    mode_name: str