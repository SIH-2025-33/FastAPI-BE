from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, select

from database import get_database
from models import Journey


db_dependency = Annotated[Session, Depends(get_database)]
router = APIRouter(prefix="/delete", tags=["delete"])


@router.delete("/delete_journey")
def delete_journey(journey_id: int, db: db_dependency):
    """Delete all trips associated with a journey_id for a specific user"""
    try:
        stmt = select(Journey).where(Journey.id == journey_id)
        journey = db.execute(stmt).scalars().first()
        
        if not journey:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No journey found with journey_id {journey_id}"
            )
            
        db.delete(journey)
        db.commit()
        return {"message": f"Journey {journey_id} deleted successfully"}

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )