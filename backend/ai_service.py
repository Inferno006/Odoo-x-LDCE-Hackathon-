import json
import os
from pathlib import Path
from uuid import uuid4

from dotenv import load_dotenv
from google import genai
from google.genai import types

from models import Activity, Stop, Trip, TripCreate

load_dotenv(Path(__file__).resolve().parent / ".env")
load_dotenv()

_client: genai.Client | None = None


def get_genai_client() -> genai.Client:
    global _client
    if _client is None:
        api_key = (os.environ.get("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or "").strip().strip('"')
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is not set")
        _client = genai.Client(api_key=api_key)
    return _client


def trip_from_create(payload: TripCreate) -> Trip:
    share_code = (payload.share_code or "").strip() or uuid4().hex[:8]
    return Trip(
        user_id=payload.user_id,
        title=payload.title,
        share_code=share_code,
        cover_image=payload.cover_image,
        transport_budget=payload.transport_budget,
        stay_budget=payload.stay_budget,
        meals_budget=payload.meals_budget,
        stops=[
            Stop(
                city=stop.city,
                city_image=stop.city_image,
                start_date=stop.start_date,
                end_date=stop.end_date,
                activities=[
                    Activity(
                        title=activity.title,
                        activity_time=activity.activity_time,
                        cost=activity.cost,
                        category=activity.category,
                    )
                    for activity in stop.activities
                ],
            )
            for stop in payload.stops
        ],
    )


def generate_ai_trip(prompt: str) -> Trip:
    client = get_genai_client()
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=(
            "You are a travel planner. Build a complete trip itinerary from the "
            "user prompt. Use realistic dates, budgets in INR (Indian Rupees), and unique share_code "
            "(short alphanumeric). Include at least one stop and activities with "
            "ISO datetimes.\n\nUser prompt:\n"
            f"{prompt}"
        ),
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=TripCreate,
        ),
    )

    parsed = response.parsed
    if isinstance(parsed, TripCreate):
        payload = parsed
    elif isinstance(parsed, dict):
        payload = TripCreate.model_validate(parsed)
    else:
        payload = TripCreate.model_validate(json.loads(response.text))

    return trip_from_create(payload)
