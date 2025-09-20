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

    model_config = ConfigDict(from_attributes=True)