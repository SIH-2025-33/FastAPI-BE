from datetime import time
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
from sqlalchemy.orm import Session

from database import get_database
from baseModel import UserBase, ComplaintBase
from models import User, Complaint

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


@router.post("/complaint")
def raise_complaint(complaint: ComplaintBase, db: db_dependency):
    userComplaint = Complaint(
        user_id=complaint.user_id,
        location_lon=complaint.location_lon,
        location_lat=complaint.location_lat,
        description=complaint.description,
        category=complaint.category,
        status=complaint.status,
    )

    try:
        db.add(userComplaint)
        db.commit()
        db.refresh(userComplaint)

        return {"message": "Complaint stored successfully."}

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}",
        )
