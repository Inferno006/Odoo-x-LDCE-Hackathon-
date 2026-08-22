import hashlib
import hmac
import os
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Annotated, Optional
from urllib.parse import quote_plus
from pydantic import BaseModel

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

from fastapi import Depends, FastAPI, HTTPException, Query, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import inspect, text
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

import bcrypt as _bcrypt

if not hasattr(_bcrypt, "__about__"):
    class _BcryptAbout:
        __version__ = getattr(_bcrypt, "__version__", "4.0.0")

    _bcrypt.__about__ = _BcryptAbout()

from ai_service import generate_ai_trip, trip_from_create
from database import create_db_and_tables, engine, get_session
from models import (
    AIGenerateTripRequest,
    Activity,
    ActivityCreate,
    ActivityRead,
    Stop,
    StopRead,
    Token,
    TokenData,
    Trip,
    TripCreate,
    TripRead,
    User,
    UserLogin,
    UserRead,
    UserRegister,
    Post,
)

SessionDep = Annotated[Session, Depends(get_session)]

DEFAULT_COVER = "https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=800"
DEFAULT_CITY = "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=400"
DEFAULT_AVATAR = "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

app = FastAPI(title="Globetrotter API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def _verify_legacy_pbkdf2(password: str, password_hash: str) -> bool:
    try:
        salt, digest = password_hash.split("$", 1)
    except ValueError:
        return False
    check = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 120_000).hex()
    return hmac.compare_digest(check, digest)


def verify_password(password: str, password_hash: str) -> bool:
    if password_hash.startswith("$2"):
        return pwd_context.verify(password, password_hash)
    return _verify_legacy_pbkdf2(password, password_hash)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta if expires_delta is not None else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: SessionDep,
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if not isinstance(email, str) or not email:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = session.exec(select(User).where(User.email == token_data.email)).first()
    if user is None:
        raise credentials_exception
    return user


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
    _add_column_if_missing("user", "role", "role VARCHAR DEFAULT 'user'")


def seed_sample_trips() -> None:
    with Session(engine) as session:
        existing = session.exec(select(Trip)).first()
        if existing is not None:
            return

        demo_user = session.exec(select(User).where(User.email == "aarav@globetrotter.dev")).first()
        if demo_user is None:
            demo_user = User(
                name="Aarav Sharma",
                email="aarav@globetrotter.dev",
                password_hash=hash_password("password123"),
                avatar_url=DEFAULT_AVATAR,
                role="user"
            )
            session.add(demo_user)
            session.commit()
            session.refresh(demo_user)

        admin_user = session.exec(select(User).where(User.email == "admin@globetrotter.dev")).first()
        if admin_user is None:
            admin_user = User(
                name="System Administrator",
                email="admin@globetrotter.dev",
                password_hash=hash_password("adminpassword"),
                avatar_url="https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150",
                role="admin"
            )
            session.add(admin_user)
            session.commit()

        golden_triangle = Trip(
            user_id=demo_user.id,
            title="Golden Triangle Tour",
            share_code="IN-GOLDEN",
            cover_image="https://images.unsplash.com/photo-1548013146-72479768bada?w=800",
            transport_budget=25000.0,
            stay_budget=35000.0,
            meals_budget=15000.0,
            stops=[
                Stop(
                    city="Delhi",
                    city_image="https://images.unsplash.com/photo-1587474260584-136574528ed5?w=400",
                    start_date=date(2026, 4, 2),
                    end_date=date(2026, 4, 5),
                    activities=[
                        Activity(
                            title="Red Fort & Chandni Chowk Walk",
                            activity_time=datetime(2026, 4, 2, 9, 30),
                            cost=0.0,
                            category="sightseeing",
                        ),
                        Activity(
                            title="Paranthe Wali Gali Breakfast",
                            activity_time=datetime(2026, 4, 3, 7, 0),
                            cost=1200.0,
                            category="food",
                        ),
                    ],
                ),
                Stop(
                    city="Agra",
                    city_image="https://images.unsplash.com/photo-1564507592333-c60657eea523?w=400",
                    start_date=date(2026, 4, 5),
                    end_date=date(2026, 4, 8),
                    activities=[
                        Activity(
                            title="Taj Mahal Sunrise View",
                            activity_time=datetime(2026, 4, 6, 5, 45),
                            cost=500.0,
                            category="sightseeing",
                        ),
                        Activity(
                            title="Mughlai Feast in Agra",
                            activity_time=datetime(2026, 4, 7, 19, 0),
                            cost=4500.0,
                            category="food",
                        ),
                    ],
                ),
            ],
        )
        kerala = Trip(
            user_id=demo_user.id,
            title="Kerala Backwaters Tour",
            share_code="IN-KERALA",
            cover_image="https://images.unsplash.com/photo-1593693397690-362cb9666fc2?w=800",
            transport_budget=18000.0,
            stay_budget=28000.0,
            meals_budget=12000.0,
            stops=[
                Stop(
                    city="Kochi",
                    city_image="https://images.unsplash.com/photo-1602216056096-3b40cc0c9944?w=400",
                    start_date=date(2026, 7, 10),
                    end_date=date(2026, 7, 12),
                    activities=[
                        Activity(
                            title="Fort Kochi & Chinese Fishing Nets Stroll",
                            activity_time=datetime(2026, 7, 10, 14, 0),
                            cost=500.0,
                            category="sightseeing",
                        ),
                    ],
                ),
                Stop(
                    city="Munnar",
                    city_image="https://images.unsplash.com/photo-1542856391-010fb87dcfed?w=400",
                    start_date=date(2026, 7, 12),
                    end_date=date(2026, 7, 15),
                    activities=[
                        Activity(
                            title="Tea Garden Safari in Munnar",
                            activity_time=datetime(2026, 7, 13, 11, 0),
                            cost=1500.0,
                            category="outdoors",
                        ),
                        Activity(
                            title="Athirappilly Waterfalls Stop",
                            activity_time=datetime(2026, 7, 14, 9, 0),
                            cost=0.0,
                            category="outdoors",
                        ),
                    ],
                ),
            ],
        )
        session.add(golden_triangle)
        session.add(kerala)
        
        # Seed posts
        p1 = Post(
            user_id=demo_user.id,
            destination="Delhi",
            content="Spent the day exploring the historical lanes of Chandni Chowk! The Paranthe Wali Gali breakfast was incredible. Definitely recommend visiting the Red Fort at sunset.",
            likes=24
        )
        p2 = Post(
            user_id=demo_user.id,
            destination="Munnar",
            content="Mist-covered tea gardens and pleasant weather! Munnar is absolute bliss in the morning. Stayed in a lovely local homestay.",
            likes=42
        )
        session.add(p1)
        session.add(p2)
        session.commit()


@app.on_event("startup")
def on_startup() -> None:
    create_db_and_tables()
    migrate_schema()
    seed_sample_trips()


def authenticate_user(session: Session, email: str, password: str) -> User:
    normalized = normalize_email(email)
    user = session.exec(select(User).where(User.email == normalized)).first()
    if user is None or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.password_hash.startswith("$2"):
        user.password_hash = hash_password(password)
        session.add(user)
        session.commit()
        session.refresh(user)
    return user


def issue_token(user: User) -> Token:
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return Token(access_token=access_token, token_type="bearer")


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


@app.post("/api/auth/login", response_model=Token)
async def login_user(request: Request, session: SessionDep) -> Token:
    content_type = (request.headers.get("content-type") or "").lower()
    if "application/json" in content_type:
        payload = UserLogin.model_validate(await request.json())
        email = payload.email
        password = payload.password
    else:
        form = await request.form()
        email = str(form.get("username") or form.get("email") or "")
        password = str(form.get("password") or "")
    user = authenticate_user(session, email, password)
    return issue_token(user)


@app.get("/api/auth/me", response_model=UserRead)
def read_current_user(current_user: Annotated[User, Depends(get_current_user)]) -> UserRead:
    return user_to_read(current_user)


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


class PostCreate(BaseModel):
    destination: str
    content: str


class PostRead(BaseModel):
    id: int
    user_id: int
    user_name: str
    user_avatar: str
    destination: str
    content: str
    created_at: datetime
    likes: int


@app.get("/api/users", response_model=list[UserRead])
def list_users(current_user: Annotated[User, Depends(get_current_user)], session: SessionDep) -> list[UserRead]:
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    users = session.exec(select(User)).all()
    return [user_to_read(u) for u in users]


@app.get("/api/admin/stats")
def get_admin_stats(current_user: Annotated[User, Depends(get_current_user)], session: SessionDep):
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    user_count = len(session.exec(select(User)).all())
    trip_count = len(session.exec(select(Trip)).all())
    post_count = len(session.exec(select(Post)).all())
    return {
        "user_count": user_count,
        "trip_count": trip_count,
        "post_count": post_count,
        "revenue": user_count * 1500
    }


@app.get("/api/posts", response_model=list[PostRead])
def get_posts(session: SessionDep, destination: Optional[str] = None) -> list[PostRead]:
    stmt = select(Post)
    if destination:
        stmt = stmt.where(Post.destination == destination)
    posts = session.exec(stmt).all()
    res = []
    for p in posts:
        u = session.get(User, p.user_id)
        res.append(PostRead(
            id=p.id,
            user_id=p.user_id,
            user_name=u.name if u else "Anonymous",
            user_avatar=u.avatar_url if u else DEFAULT_AVATAR,
            destination=p.destination,
            content=p.content,
            created_at=p.created_at,
            likes=p.likes
        ))
    return res


@app.post("/api/posts", response_model=PostRead, status_code=status.HTTP_201_CREATED)
def create_post(payload: PostCreate, current_user: Annotated[User, Depends(get_current_user)], session: SessionDep) -> PostRead:
    p = Post(
        user_id=current_user.id,
        destination=payload.destination,
        content=payload.content
    )
    session.add(p)
    session.commit()
    session.refresh(p)
    return PostRead(
        id=p.id,
        user_id=p.user_id,
        user_name=current_user.name,
        user_avatar=current_user.avatar_url or DEFAULT_AVATAR,
        destination=p.destination,
        content=p.content,
        created_at=p.created_at,
        likes=p.likes
    )


@app.post("/api/stops/{stop_id}/activities", response_model=ActivityRead, status_code=status.HTTP_201_CREATED)
def add_activity_to_stop(stop_id: int, payload: ActivityCreate, session: SessionDep) -> ActivityRead:
    stop = session.get(Stop, stop_id)
    if stop is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stop not found")
    activity = Activity(
        stop_id=stop_id,
        title=payload.title,
        activity_time=payload.activity_time,
        cost=payload.cost,
        category=payload.category
    )
    session.add(activity)
    session.commit()
    session.refresh(activity)
    return activity

