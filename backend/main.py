from datetime import date, datetime
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from ai_service import generate_ai_trip, trip_from_create
from database import create_db_and_tables, engine, get_session
from models import (
    AIGenerateTripRequest,
    Activity,
    ActivityRead,
    Stop,
    StopRead,
    Trip,
    TripCreate,
    TripRead,
)

SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI(title="Globetrotter API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _activity_cost_total(trip: Trip) -> float:
    return sum(
        activity.cost
        for stop in trip.stops
        for activity in stop.activities
    )


def trip_to_read(trip: Trip) -> TripRead:
    total_budget = (
        trip.transport_budget
        + trip.stay_budget
        + trip.meals_budget
        + _activity_cost_total(trip)
    )
    return TripRead(
        id=trip.id,
        title=trip.title,
        share_code=trip.share_code,
        transport_budget=trip.transport_budget,
        stay_budget=trip.stay_budget,
        meals_budget=trip.meals_budget,
        total_budget=total_budget,
        stops=[
            StopRead(
                id=stop.id,
                trip_id=stop.trip_id,
                city=stop.city,
                start_date=stop.start_date,
                end_date=stop.end_date,
                activities=[
                    ActivityRead(
                        id=activity.id,
                        stop_id=activity.stop_id,
                        title=activity.title,
                        activity_time=activity.activity_time,
                        cost=activity.cost,
                        category=activity.category,
                    )
                    for activity in stop.activities
                ],
            )
            for stop in trip.stops
        ],
    )


def persist_trip(session: Session, trip: Trip) -> Trip:
    session.add(trip)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"share_code '{trip.share_code}' is already in use",
        )
    session.refresh(trip)
    return _load_trip(session, trip.id)


def _load_trip(session: Session, trip_id: int) -> Trip:
    trip = session.get(Trip, trip_id)
    if trip is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
    trip.stops
    for stop in trip.stops:
        stop.activities
    return trip


def _load_trip_by_share_code(session: Session, share_code: str) -> Trip:
    trip = session.exec(select(Trip).where(Trip.share_code == share_code)).first()
    if trip is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
    trip.stops
    for stop in trip.stops:
        stop.activities
    return trip


def seed_sample_trips() -> None:
    with Session(engine) as session:
        existing = session.exec(select(Trip)).first()
        if existing is not None:
            return

        kyoto = Trip(
            title="Cherry Blossoms in Japan",
            share_code="JP-SAKURA",
            transport_budget=850.0,
            stay_budget=1200.0,
            meals_budget=450.0,
            stops=[
                Stop(
                    city="Tokyo",
                    start_date=date(2026, 4, 2),
                    end_date=date(2026, 4, 5),
                    activities=[
                        Activity(
                            title="Senso-ji Temple & Asakusa walk",
                            activity_time=datetime(2026, 4, 2, 9, 30),
                            cost=0.0,
                            category="sightseeing",
                        ),
                        Activity(
                            title="Tsukiji outer market breakfast",
                            activity_time=datetime(2026, 4, 3, 7, 0),
                            cost=35.0,
                            category="food",
                        ),
                    ],
                ),
                Stop(
                    city="Kyoto",
                    start_date=date(2026, 4, 5),
                    end_date=date(2026, 4, 8),
                    activities=[
                        Activity(
                            title="Fushimi Inari sunrise hike",
                            activity_time=datetime(2026, 4, 6, 5, 45),
                            cost=0.0,
                            category="outdoors",
                        ),
                        Activity(
                            title="Kaiseki dinner in Gion",
                            activity_time=datetime(2026, 4, 7, 19, 0),
                            cost=120.0,
                            category="food",
                        ),
                    ],
                ),
            ],
        )
        iceland = Trip(
            title="Iceland Ring Road Highlights",
            share_code="IS-RING",
            transport_budget=600.0,
            stay_budget=900.0,
            meals_budget=320.0,
            stops=[
                Stop(
                    city="Reykjavik",
                    start_date=date(2026, 7, 10),
                    end_date=date(2026, 7, 12),
                    activities=[
                        Activity(
                            title="Hallgrimskirkja & harbor stroll",
                            activity_time=datetime(2026, 7, 10, 14, 0),
                            cost=10.0,
                            category="sightseeing",
                        ),
                    ],
                ),
                Stop(
                    city="Vik",
                    start_date=date(2026, 7, 12),
                    end_date=date(2026, 7, 15),
                    activities=[
                        Activity(
                            title="Reynisfjara black sand beach",
                            activity_time=datetime(2026, 7, 13, 11, 0),
                            cost=0.0,
                            category="outdoors",
                        ),
                        Activity(
                            title="Skogafoss photography stop",
                            activity_time=datetime(2026, 7, 14, 9, 0),
                            cost=0.0,
                            category="outdoors",
                        ),
                    ],
                ),
            ],
        )
        session.add(kyoto)
        session.add(iceland)
        session.commit()


@app.on_event("startup")
def on_startup() -> None:
    create_db_and_tables()
    seed_sample_trips()


@app.get("/api/trips", response_model=list[TripRead])
def list_trips(session: SessionDep) -> list[TripRead]:
    trips = session.exec(select(Trip)).all()
    results: list[TripRead] = []
    for trip in trips:
        trip.stops
        for stop in trip.stops:
            stop.activities
        results.append(trip_to_read(trip))
    return results


@app.post("/api/trips", response_model=TripRead, status_code=status.HTTP_201_CREATED)
def create_trip(payload: TripCreate, session: SessionDep) -> TripRead:
    trip = persist_trip(session, trip_from_create(payload))
    return trip_to_read(trip)


@app.get("/api/trips/share/{share_code}", response_model=TripRead)
def get_trip_by_share_code(share_code: str, session: SessionDep) -> TripRead:
    return trip_to_read(_load_trip_by_share_code(session, share_code))


@app.get("/api/trips/{trip_id}", response_model=TripRead)
def get_trip(trip_id: int, session: SessionDep) -> TripRead:
    return trip_to_read(_load_trip(session, trip_id))


@app.delete("/api/trips/{trip_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_trip(trip_id: int, session: SessionDep) -> None:
    trip = session.get(Trip, trip_id)
    if trip is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
    session.delete(trip)
    session.commit()


@app.post(
    "/api/ai-generate-trip",
    response_model=TripRead,
    status_code=status.HTTP_201_CREATED,
)
def ai_generate_trip(payload: AIGenerateTripRequest, session: SessionDep) -> TripRead:
    if not payload.prompt.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="prompt must not be empty",
        )
    try:
        trip = generate_ai_trip(payload.prompt)
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Gemini request failed: {exc}",
        ) from exc

    saved = persist_trip(session, trip)
    return trip_to_read(saved)
