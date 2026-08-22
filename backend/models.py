from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel
from sqlmodel import Field, Relationship, SQLModel


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str = Field(unique=True, index=True)
    password_hash: str
    avatar_url: Optional[str] = "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150"

    trips: List["Trip"] = Relationship(back_populates="user")


class Trip(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    title: str
    share_code: str = Field(unique=True, index=True)
    cover_image: Optional[str] = "https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=800"
    transport_budget: float = 0.0
    stay_budget: float = 0.0
    meals_budget: float = 0.0

    user: Optional[User] = Relationship(back_populates="trips")
    stops: List["Stop"] = Relationship(back_populates="trip", cascade_delete=True)


class Stop(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    trip_id: Optional[int] = Field(default=None, foreign_key="trip.id")
    city: str
    city_image: Optional[str] = "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=400"
    start_date: date
    end_date: date

    trip: Optional[Trip] = Relationship(back_populates="stops")
    activities: List["Activity"] = Relationship(back_populates="stop", cascade_delete=True)


class Activity(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    stop_id: Optional[int] = Field(default=None, foreign_key="stop.id")
    title: str
    activity_time: datetime
    cost: float
    category: str

    stop: Optional[Stop] = Relationship(back_populates="activities")


class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(SQLModel):
    email: Optional[str] = None


class UserLogin(SQLModel):
    email: str
    password: str


class UserRegister(SQLModel):
    name: str
    email: str
    password: str


class UserRead(SQLModel):
    id: int
    name: str
    email: str
    avatar_url: Optional[str] = None


class ActivityCreate(SQLModel):
    title: str
    activity_time: datetime
    cost: float
    category: str


class StopCreate(SQLModel):
    city: str
    city_image: Optional[str] = None
    start_date: date
    end_date: date
    activities: List[ActivityCreate] = []


class TripCreate(SQLModel):
    title: str
    share_code: str
    cover_image: Optional[str] = None
    transport_budget: float = 0.0
    stay_budget: float = 0.0
    meals_budget: float = 0.0
    user_id: Optional[int] = None
    stops: List[StopCreate] = []


class ActivityRead(SQLModel):
    id: int
    stop_id: Optional[int] = None
    title: str
    activity_time: datetime
    cost: float
    category: str


class StopRead(SQLModel):
    id: int
    trip_id: Optional[int] = None
    city: str
    city_image: Optional[str] = None
    start_date: date
    end_date: date
    activities: List[ActivityRead] = []


class TripRead(SQLModel):
    id: int
    user_id: Optional[int] = None
    title: str
    share_code: str
    cover_image: Optional[str] = None
    transport_budget: float
    stay_budget: float
    meals_budget: float
    total_budget: float
    stops: List[StopRead] = []


class AIGenerateTripRequest(BaseModel):
    prompt: str
    user_id: Optional[int] = None
