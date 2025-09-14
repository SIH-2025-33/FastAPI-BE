from datetime import time
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
from sqlalchemy.orm import Session

from database import get_database
from baseModel import UserBase
from models import User

db_dependency = Annotated[Session, Depends(get_database)]
router = APIRouter(prefix="/create", tags=["create"])


@router.post("/user")
def create_user(user: UserBase, db: db_dependency):
    db_user = User(
        age=user.age,
        gender=user.gender,
        consent_start_time=user.consent_start_time,
        consent_end_time=user.consent_end_time,
    )

    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        return {"user_id": db_user.id}

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}",
        )
