from datetime import time
import json
import os
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated, List
from sqlalchemy.orm import Session
from sqlalchemy import select
import google.generativeai as genai
import requests
from dotenv import load_dotenv

from database import get_database
from baseModel import UserBase, ComplaintBase, TripRequestBase, ModeResponseBase
from models import User, Complaint, Trip, LocationPoints, TripMode

load_dotenv()

db_dependency = Annotated[Session, Depends(get_database)]
router = APIRouter(prefix="/create", tags=["create"])
genai.configure(api_key=os.getenv("GEMINI_API"))


def travel_mode_interprter(tripsData: List[TripRequestBase]) -> dict:
 
    system_prompt = """
        You are a transport mode classifier. 

        You will receive as input a list of records, each containing:
        - latitude (float)
        - longitude (float)
        - speed (float, in km/h)
        - timestamp (HH:MM format)

        Your task:
        1. Analyze the sequence of records.
        2. Group them into trip segments with a clear origin and destination.
        - The origin is the first record of a segment.
        - The destination is the last record of a segment.
        3. Guess the mode of transport for each segment based on speed ranges and duration:
        - 0-7 km/h → "WALKING"
        - 8-25 km/h → "CYCLING"
        - 26-60 km/h → "BUS"
        - 61-120 km/h → "CAR"
        - >120 km/h → "TRAIN" or "FLIGHT" depending on context
        4. Output only JSON in this exact format:

        [
        {
            "origin": {"latitude": <float>, "longitude": <float>, "timestamp": "<HH:MM>"},
            "destination": {"latitude": <float>, "longitude": <float>, "timestamp": "<HH:MM>"},
            "mode": "<string>"
        },
        ...
        ]

        No extra text or explanation, only valid JSON.

    """

    model = genai.GenerativeModel("gemini-1.5-flash")
    chat = model.start_chat()
    chat.send_message(system_prompt)

    user_input = json.dumps([trip.dict() for trip in tripsData], default=str)
    resp = chat.send_message(user_input)

    try:
        return json.loads(resp.text)
    except json.JSONDecodeError:
        cleaned = resp.text.strip().split("```json")[-1].split("```")[0]
        return json.loads(cleaned)


def get_location_name(latitude: float, longitude: float) -> str:
    try:
        response = requests.get(
            f"https://nominatim.openstreetmap.org/reverse?format=json&lat={latitude}&lon={longitude}",
            headers={"User-Agent": "MyApp/1.0 (email@example.com)"},
        )
        if response.status_code != 200:
            return "Unknown"

        data = response.json()
        addr = data.get("address", {})
        neighbour = addr.get("neighbourhood")
        suburb = addr.get("suburb")
        village = addr.get("village")

        return neighbour or suburb or village or "Unknown"

    except Exception:
        return "Unknown"


def distance_travelled(
    originLatitude: float,
    originLongitude: float,
    destLatitude: float,
    destLongitude: float,
) -> float:
    try:
        url = (
            f"http://router.project-osrm.org/route/v1/driving/"
            f"{originLongitude},{originLatitude};{destLongitude},{destLatitude}?overview=false"
        )
        response = requests.get(url)
        if response.status_code != 200:
            return 0.0

        data = response.json()
        distance_meters = data["routes"][0]["distance"]
        return distance_meters / 1000
    except Exception:
        return 0.0


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
                    destLatitude=destinationPoints.latitude,
                    destLongitude=destinationPoints.longitude,
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


@router.post("/mode")
def mode_classify(tripsData: List[TripRequestBase]):
    return travel_mode_interprter(tripsData)
