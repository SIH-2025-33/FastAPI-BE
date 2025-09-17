from datetime import time
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated, List
from sqlalchemy.orm import Session
from sqlalchemy import select
import requests

from database import get_database
from baseModel import UserBase, ComplaintBase, TripRequestBase, ModeResponseBase
from models import User, Complaint, Trip, LocationPoints, TripMode

db_dependency = Annotated[Session, Depends(get_database)]
router = APIRouter(prefix="/create", tags=["create"])


def travel_mode_interprter(tripsData: List[TripRequestBase]) -> dict:
    # response = [
    #     {
    #         "origin": {"latitude": 12, "longitude": 14, "timestamp": "12:00"},
    #         "destination": {"latitude": 12, "longitude": 14, "timestamp": "12:10"},
    #         "mode": "WALKING",
    #     },
    #     {
    #         "origin": {"latitude": 12, "longitude": 14, "timestamp": "12:15"},
    #         "destination": {"latitude": 12, "longitude": 14, "timestamp": "13:00"},
    #         "mode": "BUS",
    #     }
    # ]
    pass


def get_location_name(latitude: float, longitude: float):
    data = requests.get(
        f"https://nominatim.openstreetmap.org/reverse?format=json&lat={latitude}&lon={longitude}"
    )
    addr = data.get("address", {})
    neighbour = addr.get("neighbourhood")
    suburb = addr.get("suburb")
    village = addr.get("village")

    return neighbour or suburb or village


def distance_travelled(
    originLatitude: float,
    originLongitude: float,
    destLatitude: float,
    destLongitude: float,
):
    data = requests.get(
        f"http://router.project-osrm.org/route/v1/driving/74.{originLongitude},{originLatitude};{destLongitude},{destLatitude}?overview=false"
    )


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


@router.post("/trip", response_model=List[ModeResponseBase])
def add_trip(user_id: int, tripsData: List[TripRequestBase], db: db_dependency):
    try:
        trips = travel_mode_interprter(tripsData)
        modes = []

        for trip in trips:

            originPoints = LocationPoints(
                latitude=trip["origin"]["latitude"],
                longitude=trip["origin"]["longitude"],
                location_name=get_location_name(
                    trip["origin"]["latitude"], trip["origin"]["longitude"]
                ),
            )
            destinationPoints = LocationPoints(
                latitude=trip["destination"]["latitude"],
                longitude=trip["destination"]["longitude"],
                location_name=get_location_name(
                    trip["destination"]["latitude"], trip["destination"]["longitude"]
                ),
            )

            db.add(originPoints)
            db.add(destinationPoints)
            db.commit()
            db.refresh(originPoints)
            db.refresh(destinationPoints)

            stmt = select(TripMode).where(TripMode.mode_name == trip["mode"].upper())
            mode = db.execute(stmt).scalars().first()

            _trip = Trip(
                user_id=user_id,
                mode_id=mode.id,
                origin_location_id=originPoints.id,
                destination_location_id=destinationPoints.id,
                start_time=trip["origin"]["timestamp"],
                end_time=trip["destination"]["timestamp"],
                distance_travelled=distance_travelled(
                    originLatitude=originPoints.latitude,
                    originLongitude=originPoints.longitude,
                ),
            )

            db.add(_trip)
            db.commit()
            db.refresh(_trip)

            mode_res = ModeResponseBase(trip_id=_trip.id, mode_name=mode.mode_name)
            modes.append(mode_res)

            return modes

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}",
        )
