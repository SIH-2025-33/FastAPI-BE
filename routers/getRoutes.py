from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy import select, and_


from database import get_database
from models import User, Trip, TripMode


db_dependency = Annotated[Session, Depends(get_database)]
router = APIRouter(prefix="/read", tags=["read"])


@router.get("/user/streak")
def get_user_streak(user_id: int, db: db_dependency):
    stmt = select(User).where(User.id == user_id)
    user = db.execute(stmt).scalars().first()
    return {"streak": user.streak}


@router.get("/user/distance/{mode}")
def get_user_distance_travelled(user_id: int, mode: str, db: db_dependency):
    stmt = select(TripMode).where(TripMode.mode_name == mode.upper())
    mode = db.execute(stmt).scalars().first()
    stmt = select(Trip).where(and_(Trip.user_id == user_id, Trip.mode_id == mode.id))
    trips = db.execute(stmt).scalars().all()

    total_distance_travelled = 0
    if trips:
        for trip in trips:
            total_distance_travelled += trip.distance_travelled
            
    return {"distance_travelled": total_distance_travelled}
