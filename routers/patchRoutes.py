from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy import select

from database import get_database
from models import User, Journey


router = APIRouter(prefix="/update", tags=["update"])
db_dependency = Annotated[Session, Depends(get_database)]


@router.patch("/increment_streak")
def daily_streak(user_id: int, db: db_dependency):
    stmt = select(User).where(User.id == user_id)
    user = db.execute(stmt).scalars().first()
    user.streak += 1
    try:
        db.commit()
        db.refresh(user)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occured: {str(e)}",
        )


@router.patch("/verify_journey")
def verify_journey(journey_id: int, db: db_dependency):
    """Update is_verified_by_user flag for all trips in a journey"""
    try:
        stmt = select(Journey).where(Journey.id == journey_id)
        journey = db.execute(stmt).scalars().first()
        journey.is_verified_by_user = True

        db.commit()
        return {"message": f"Journey {journey_id} verified successfully"}

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}",
        )


@router.patch("/journey_purpose")
def update_purpose(journey_id: int, purpose: str, db: db_dependency):

    try:
        stmt = select(Journey).where(Journey.id == journey_id)
        journey = db.execute(stmt).scalars().first()
        journey.purpose = purpose

        db.commit()
        return {"message": "Purpose verified successfully"}

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}",
        )
