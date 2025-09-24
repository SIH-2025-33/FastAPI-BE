import json
import math
import time
from typing import Any, Dict, List, Optional
import requests
import os
import google.generativeai as genai
from dotenv import load_dotenv

from baseModel import TripRequestBase
from models import DataCollector

load_dotenv()

USER_AGENT = os.getenv("USER_AGENT", "MyApp/1.0 (email@example.com)")
DEFAULT_TIMEOUT = 8.0
genai.configure(api_key=os.getenv("GEMINI_API"))


def get_location_name(latitude: float, longitude: float) -> str:

    try:
        url = "https://nominatim.openstreetmap.org/reverse"
        params = {
            "format": "json",
            "lat": latitude,
            "lon": longitude,
            "zoom": 18,
            "addressdetails": 1,
            "accept-language": "en",
        }
        headers = {"User-Agent": USER_AGENT}
        resp = requests.get(
            url, params=params, headers=headers, timeout=DEFAULT_TIMEOUT
        )

        if resp.status_code != 200:
            return "Unknown"

        data = resp.json()
        addr = data.get("address", {}) or {}
        for key in [
            "neighbourhood",
            "suburb",
            "village",
            "town",
            "city",
            "county",
            "state",
            "country",
        ]:
            if addr.get(key):
                return addr[key]
        if data.get("display_name"):
            parts = [p.strip() for p in data["display_name"].split(",")]
            return ", ".join(parts[:3]) if parts else data["display_name"]

        return "Unknown"
    except Exception:
        return "Unknown"


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0088  # Earth radius in km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = (
        math.sin(dphi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    )
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def distance_travelled(
    originLatitude: float,
    originLongitude: float,
    destLatitude: float,
    destLongitude: float,
) -> float:

    try:
        # Note: OSRM expects lon,lat ordering for coordinates
        url = (
            "http://router.project-osrm.org/route/v1/driving/"
            f"{originLongitude},{originLatitude};{destLongitude},{destLatitude}"
        )
        params = {"overview": "false", "alternatives": "false", "steps": "false"}
        headers = {"User-Agent": USER_AGENT}
        resp = _retry_get(
            url, params=params, headers=headers, timeout=DEFAULT_TIMEOUT, max_attempts=3
        )
        if resp and resp.status_code == 200:
            data = resp.json()
            routes = data.get("routes")
            if routes and isinstance(routes, list) and len(routes) > 0:
                distance_meters = routes[0].get("distance")
                if distance_meters is not None:
                    return float(distance_meters) / 1000.0
        # fallback to haversine if OSRM failed or returned nothing meaningful
        return haversine_km(
            originLatitude, originLongitude, destLatitude, destLongitude
        )
    except Exception:
        # safe fallback
        return haversine_km(
            originLatitude, originLongitude, destLatitude, destLongitude
        )


def _retry_get(
    url: str,
    params: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: float = DEFAULT_TIMEOUT,
    max_attempts: int = 3,
    backoff_base: float = 0.5,
) -> Optional[requests.Response]:
    attempt = 0
    backoff = backoff_base
    while attempt < max_attempts:
        try:
            resp = requests.get(url, params=params, headers=headers, timeout=timeout)
            if resp.status_code == 200 or (400 <= resp.status_code < 500):
                return resp
        except requests.RequestException:
            pass
        attempt += 1
        time.sleep(backoff)
        backoff *= 2
    return None


def travel_mode_interprter(tripsData: List[DataCollector]) -> dict:

    system_prompt = """
You are a transport mode classifier.

Input: A chronological list of records, each with:
- latitude (float)
- longitude (float)
- speed (float, in km/h)
- timestamp (ISO 8601 format, e.g., "YYYY-MM-DDTHH:MM:SS")

Your task:
1. Analyze the records in time order.
2. Group them into trip segments, each with a clear origin and destination:
   - Origin = first record of the segment.
   - Destination = last record of the segment.
3. Classify the transport mode based on speed:
   - 0-7 km/h → "WALKING"
   - 8-25 km/h → "CYCLING"
   - 26-60 km/h → "BUS"
   - 61-120 km/h → "CAR"
   - >120 km/h → "TRAIN" or "FLIGHT" depending on context.
4. Segmentation rule:
   - Form the longest possible continuous sequence where the average speed remains in the same range.
   - Do not split segments of the same mode unless there is a clear change in speed range or a significant pause.
5. Output format:
   - Only valid JSON in this exact structure:

[
  {
    "origin": {"latitude": <float>, "longitude": <float>, "timestamp": "<"YYYY-MM-DDTHH:MM:SS">"},
    "destination": {"latitude": <float>, "longitude": <float>, "timestamp": "<"YYYY-MM-DDTHH:MM:SS">"},
    "mode": "<string>"
  },
  ...
]

- Timestamps in output must only include the time component (`"YYYY-MM-DDTHH:MM:SS"`).
- Do not include any text, explanations, or additional fields outside the specified JSON.
"""

    def to_dict(obj):
        return {
            "latitude": obj.latitude,
            "longitude": obj.longitude,
            "speed": obj.speed,
            "timestamp": obj.timestamp,  # ISO format
        }

    model = genai.GenerativeModel("gemini-2.5-flash")
    chat = model.start_chat()
    chat.send_message(system_prompt)

    user_input = json.dumps([to_dict(trip) for trip in tripsData], default=str)
    resp = chat.send_message(user_input)

    text = resp.text.strip()
    if "```json" in text:
        text = text.split("```json")[-1].split("```")[0].strip()

    return json.loads(text)
