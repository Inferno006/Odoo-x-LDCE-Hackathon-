import hashlib
import hmac
import secrets
from datetime import date, datetime
from typing import Annotated, Optional
from urllib.parse import quote_plus

from dotenv import load_dotenv

load_dotenv()

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, text
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
    User,
    UserLogin,
    UserRead,
    UserRegister,
)

SessionDep = Annotated[Session, Depends(get_session)]

DEFAULT_COVER = "https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=800"
DEFAULT_CITY = "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=400"
DEFAULT_AVATAR = "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150"

app = FastAPI(title="Globetrotter API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 120_000).hex()
    return f"{salt}${digest}"


def verify_password(password: str, password_hash: str) -> bool:
    try:
        salt, digest = password_hash.split("$", 1)
    except ValueError:
        return False
    check = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 120_000).hex()
    return hmac.compare_digest(check, digest)


def normalize_email(email: str) -> str:
    return email.strip().lower()


def unsplash_image_url(query: str, width: int) -> str:
    topic = quote_plus((query or "travel").strip() or "travel")
    return f"https://source.unsplash.com/{width}x500/?{topic},travel"


def apply_destination_images(trip: Trip) -> Trip:
    destination = trip.stops[0].city if trip.stops else trip.title
    trip.cover_image = unsplash_image_url(destination, 800)
    for stop in trip.stops:
        stop.city_image = unsplash_image_url(stop.city, 400)
    return trip


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
        user_id=trip.user_id,
        title=trip.title,
        share_code=trip.share_code,
        cover_image=trip.cover_image or DEFAULT_COVER,
        transport_budget=trip.transport_budget,
        stay_budget=trip.stay_budget,
        meals_budget=trip.meals_budget,
        total_budget=total_budget,
        stops=[
            StopRead(
                id=stop.id,
                trip_id=stop.trip_id,
                city=stop.city,
                city_image=stop.city_image or DEFAULT_CITY,
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


def user_to_read(user: User) -> UserRead:
    return UserRead(
        id=user.id,
        name=user.name,
        email=user.email,
        avatar_url=user.avatar_url or DEFAULT_AVATAR,
    )


def require_user(session: Session, user_id: Optional[int]) -> None:
    if user_id is None:
        return
    if session.get(User, user_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


def persist_trip(session: Session, trip: Trip) -> Trip:
    require_user(session, trip.user_id)
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


def _add_column_if_missing(table: str, column: str, ddl: str) -> None:
    inspector = inspect(engine)
    if table not in inspector.get_table_names():
        return
    existing = {col["name"] for col in inspector.get_columns(table)}
    if column in existing:
        return
    with engine.begin() as connection:
        connection.execute(text(f"ALTER TABLE {table} ADD COLUMN {ddl}"))


def migrate_schema() -> None:
    _add_column_if_missing("trip", "user_id", "user_id INTEGER REFERENCES user(id)")
    _add_column_if_missing("trip", "cover_image", "cover_image VARCHAR")
    _add_column_if_missing("stop", "city_image", "city_image VARCHAR")


def seed_sample_trips() -> None:
    with Session(engine) as session:
        existing = session.exec(select(Trip)).first()
        if existing is not None:
            return

        demo_user = session.exec(select(User).where(User.email == "maya@globetrotter.dev")).first()
        if demo_user is None:
            demo_user = User(
                name="Maya Chen",
                email="maya@globetrotter.dev",
                password_hash=hash_password("password123"),
                avatar_url=DEFAULT_AVATAR,
            )
            session.add(demo_user)
            session.commit()
            session.refresh(demo_user)

        kyoto = Trip(
            user_id=demo_user.id,
            title="Cherry Blossoms in Japan",
            share_code="JP-SAKURA",
            cover_image="https://images.unsplash.com/photo-1493976040376-45c5d0c05882?w=800",
            transport_budget=850.0,
            stay_budget=1200.0,
            meals_budget=450.0,
            stops=[
                Stop(
                    city="Tokyo",
                    city_image="https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=400",
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
                    city_image="https://images.unsplash.com/photo-1493976040376-45c5d0c05882?w=400",
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
            user_id=demo_user.id,
            title="Iceland Ring Road Highlights",
            share_code="IS-RING",
            cover_image="https://images.unsplash.com/photo-1504829857797-ddff23c279e4?w=800",
            transport_budget=600.0,
            stay_budget=900.0,
            meals_budget=320.0,
            stops=[
                Stop(
                    city="Reykjavik",
                    city_image="https://images.unsplash.com/photo-1476610182048-b716b8518aae?w=400",
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
                    city_image="https://images.unsplash.com/photo-1531366936337-7d223312f64d?w=400",
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
    migrate_schema()
    seed_sample_trips()


@app.post("/api/auth/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register_user(payload: UserRegister, session: SessionDep) -> UserRead:
    email = normalize_email(payload.email)
    if not payload.name.strip() or not email or not payload.password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="name, email, and password are required")
    existing = session.exec(select(User).where(User.email == email)).first()
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="email is already registered")
    user = User(
        name=payload.name.strip(),
        email=email,
        password_hash=hash_password(payload.password),
        avatar_url=DEFAULT_AVATAR,
    )
    session.add(user)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="email is already registered")
    session.refresh(user)
    return user_to_read(user)


@app.post("/api/auth/login", response_model=UserRead)
def login_user(payload: UserLogin, session: SessionDep) -> UserRead:
    email = normalize_email(payload.email)
    user = session.exec(select(User).where(User.email == email)).first()
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid email or password")
    return user_to_read(user)


@app.get("/api/trips", response_model=list[TripRead])
def list_trips(
    session: SessionDep,
    user_id: Optional[int] = Query(default=None),
) -> list[TripRead]:
    statement = select(Trip)
    if user_id is not None:
        require_user(session, user_id)
        statement = statement.where(Trip.user_id == user_id)
    trips = session.exec(statement).all()
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
    require_user(session, payload.user_id)
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

    trip.user_id = payload.user_id
    apply_destination_images(trip)
    saved = persist_trip(session, trip)
    return trip_to_read(saved)
