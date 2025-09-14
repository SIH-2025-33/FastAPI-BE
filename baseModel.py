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
