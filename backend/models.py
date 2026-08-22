from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel
from sqlmodel import Field, Relationship, SQLModel


class Trip(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    share_code: str = Field(unique=True, index=True)
    transport_budget: float = 0.0
    stay_budget: float = 0.0
    meals_budget: float = 0.0

    stops: List["Stop"] = Relationship(back_populates="trip", cascade_delete=True)


class Stop(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    trip_id: Optional[int] = Field(default=None, foreign_key="trip.id")
    city: str
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


class ActivityCreate(SQLModel):
    title: str
    activity_time: datetime
    cost: float
    category: str


class StopCreate(SQLModel):
    city: str
    start_date: date
    end_date: date
    activities: List[ActivityCreate] = []


class TripCreate(SQLModel):
    title: str
    share_code: str
    transport_budget: float = 0.0
    stay_budget: float = 0.0
    meals_budget: float = 0.0
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
    start_date: date
    end_date: date
    activities: List[ActivityRead] = []


class TripRead(SQLModel):
    id: int
    title: str
    share_code: str
    transport_budget: float
    stay_budget: float
    meals_budget: float
    total_budget: float
    stops: List[StopRead] = []


class AIGenerateTripRequest(BaseModel):
    prompt: str
