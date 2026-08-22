import json
import os
from uuid import uuid4

from google import genai
from google.genai import types

from models import Activity, Stop, Trip, TripCreate

_client: genai.Client | None = None


def get_genai_client() -> genai.Client:
    global _client
    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise RuntimeError(
                "Set GEMINI_API_KEY or GOOGLE_API_KEY to use AI trip generation."
            )
        _client = genai.Client(api_key=api_key)
    return _client


def trip_from_create(payload: TripCreate) -> Trip:
    share_code = (payload.share_code or "").strip() or uuid4().hex[:8]
    return Trip(
        title=payload.title,
        share_code=share_code,
        transport_budget=payload.transport_budget,
        stay_budget=payload.stay_budget,
        meals_budget=payload.meals_budget,
        stops=[
            Stop(
                city=stop.city,
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
        model="gemini-2.5-flash",
        contents=(
            "You are a travel planner. Build a complete trip itinerary from the "
            "user prompt. Use realistic dates, budgets in USD, and unique share_code "
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
