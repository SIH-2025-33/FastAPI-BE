from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, select


from database import get_database
from baseModel import UserBase, ComplaintBase, TripRequestBase, JourneyBase
from models import (
    User,
    Complaint,
    Trip,
    LocationPoints,
    TripMode,
    DataCollector,
    Journey,
)
from Tools.helperMethods import (
    get_location_name,
    distance_travelled,
    travel_mode_interprter,
)


db_dependency = Annotated[Session, Depends(get_database)]
router = APIRouter(prefix="/create", tags=["create"])


@router.post("/user")
def create_user(user: UserBase, db: db_dependency):
    db_user = User(
        age=user.age,
        gender=user.gender,
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


@router.post("/trip", response_model=JourneyBase)
def add_trip(user_id: int, timestamp: str, db: db_dependency):
    try:
        stmt = (
            select(DataCollector)
            .where(
                and_(
                    DataCollector.user_id == user_id,
                    DataCollector.timestamp <= datetime.fromisoformat(timestamp),
                    DataCollector.is_used.is_(False),
                )
            )
            .order_by(DataCollector.timestamp)
        )
        tripsData = db.execute(stmt).scalars().all()
        trips = travel_mode_interprter(tripsData)

        journey = Journey(
            origin=get_location_name(
                trips[0]["origin"]["latitude"], trips[0]["origin"]["longitude"]
            ),
            destination=get_location_name(
                trips[-1]["destination"]["latitude"],
                trips[-1]["destination"]["longitude"],
            ),
            user_id=user_id,
            start_time=datetime.fromisoformat(trips[0]["origin"]["timestamp"]),
            end_time=datetime.fromisoformat(trips[-1]["destination"]["timestamp"]),
        )
        db.add(journey)
        db.commit()
        db.refresh(journey)

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
                journey_id=journey.id,
                origin_location_id=originPoints.id,
                destination_location_id=destinationPoints.id,
                start_time=datetime.fromisoformat(trip["origin"]["timestamp"]),
                end_time=datetime.fromisoformat(trip["destination"]["timestamp"]),
                distance_travelled=distance_travelled(
                    originLatitude=originPoints.latitude,
                    originLongitude=originPoints.longitude,
                    destLatitude=destinationPoints.latitude,
                    destLongitude=destinationPoints.longitude,
                ),
            )

            db.add(_trip)
            db.commit()
            db.refresh(_trip)

            for tripData in tripsData:
                tripData.is_used = True
                db.add(tripData)

            db.commit()

        return JourneyBase(
            id=journey.id,
            origin=journey.origin,
            destination=journey.destination,
            start_time=str(journey.start_time),
            end_time=str(journey.end_time),
            purpose=journey.purpose,
            is_verified_by_user=journey.is_verified_by_user,
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}",
        )


@router.post("/api_required_data")
def create_api_required_data(tripDatas: List[TripRequestBase], db: db_dependency):
    for tripData in tripDatas:
        data = DataCollector(
            user_id=tripData.user_id,
            latitude=tripData.latitude,
            longitude=tripData.longitude,
            speed=tripData.speed,
            timestamp=datetime.fromisoformat(tripData.timestamp),
        )

        try:
            db.add(data)
            db.commit()
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An error occurred: {str(e)}",
            )
