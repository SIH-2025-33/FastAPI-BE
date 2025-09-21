from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy import select, and_

from database import get_database
from models import User, Trip, TripMode, Journey
from baseModel import JourneyBase

db_dependency = Annotated[Session, Depends(get_database)]
router = APIRouter(prefix="/get", tags=["get"])

# # CO2 emission factors in kg CO2 per km for different modes
# CO2_FACTORS = {
#     "WALKING": 0,  # No direct emissions
#     "CYCLING": 0,  # No direct emissions
#     "BUS": 0.082,  # Average bus emissions
#     "CAR": 0.17,  # Average car emissions
#     "TRAIN": 0.041,  # Average train emissions
#     "FLIGHT": 0.115,  # Average flight emissions per passenger km
# }


# @router.get("/emissions/{mode_name}")
# def calculate_emissions(user_id: int, mode_name: str, db: db_dependency):
#     """Calculate CO2 emissions for a user's trips by mode"""
#     try:
#         # Verify mode exists and standardize to uppercase
#         mode_name = mode_name.upper()
#         if mode_name not in CO2_FACTORS:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail=f"Invalid mode: {mode_name}",
#             )

#         # Get mode_id for the given mode_name
#         mode = db.query(TripMode).filter(TripMode.mode_name == mode_name).first()
#         if not mode:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail=f"Mode {mode_name} not found in database",
#             )

#         # Get all verified trips for the user with the specified mode
#         trips = (
#             db.query(Trip)
#             .filter(
#                 Trip.user_id == user_id,
#                 Trip.mode_id == mode.id,
#                 Trip.is_verified_by_user == True,
#             )
#             .all()
#         )

#         total_distance = sum(trip.distance_travelled for trip in trips)
#         co2_emissions = total_distance * CO2_FACTORS[mode_name]

#         # For non-emitting modes (walking, cycling), calculate emissions saved
#         # assuming the alternative would have been a car journey
#         if mode_name in ["WALKING", "CYCLING"]:
#             emissions_saved = total_distance * CO2_FACTORS["CAR"]
#             return {
#                 "user_id": user_id,
#                 "mode": mode_name,
#                 "total_distance_km": round(total_distance, 2),
#                 "emissions_saved_kg": round(emissions_saved, 2),
#             }
#         else:
#             return {
#                 "user_id": user_id,
#                 "mode": mode_name,
#                 "total_distance_km": round(total_distance, 2),
#                 "co2_emissions_kg": round(co2_emissions, 2),
#             }

#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"An error occurred: {str(e)}",
#         )


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


@router.get("/user/journey")
def get_all_journeys(user_id: int, db: db_dependency):
    stmt = select(Journey).where(Journey.user_id == user_id)
    journeys = db.execute(stmt).scalars().all()
    if not journeys:
        return {"message": "No journeys found for the user"}

    list_of_journeys = []
    for journey in journeys:
        journey_data = JourneyBase(
            id=journey.id,
            origin=journey.origin,
            destination=journey.destination,
            start_time=journey.start_time,
            end_time=journey.end_time,
            purpose=journey.purpose,
            is_verified_by_user=journey.is_verified_by_user,
        )
        list_of_journeys.append(journey_data)
    return list_of_journeys


@router.get("/journey")
def get_all_journeys_for_NATPAC(db: db_dependency):
    stmt = select(Journey)
    journeys = db.execute(stmt).scalars().all()
    if not journeys:
        return {"message": "No journeys found for the user"}

    list_of_journeys = []
    for journey in journeys:
        journey_data = JourneyBase(
            id=journey.id,
            origin=journey.origin,
            destination=journey.destination,
            start_time=journey.start_time,
            end_time=journey.end_time,
            purpose=journey.purpose,
            is_verified_by_user=journey.is_verified_by_user,
        )
        list_of_journeys.append(journey_data)
    return list_of_journeys
