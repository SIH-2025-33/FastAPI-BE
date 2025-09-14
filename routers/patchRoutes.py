from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy import select

from database import get_database
from models import User

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
