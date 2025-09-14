from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
from sqlalchemy.orm import Session

from database import get_database
from models import User

router = APIRouter(prefix="/update", tags=["update"])
db_dependency = Annotated[Session, Depends(get_database)]


@router.patch("/increment_streak")
def daily_streak(user_id: int, db: db_dependency):
    user = db.query(User).filter(User.id == user_id).first()
    return {"daily_streak": user.streak}
