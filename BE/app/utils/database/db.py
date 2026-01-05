import os
import datetime
from enum import Enum
from typing import Annotated, Optional

from fastapi import Depends, Query
from pydantic import BaseModel, EmailStr
from sqlmodel import (
    Date,
    Field,
    Session,
    SQLModel,
    create_engine,
    select,
    UniqueConstraint,
)

from ..auth.password import get_password_hash


# ─────────────────────────────────────────────
#               DATABASE PATH
# ─────────────────────────────────────────────

DB_PATH = os.getenv("DB_PATH", "data/database.db")
sqlite_url = f"sqlite:///{DB_PATH}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)


# ─────────────────────────────────────────────
#               MODELS
# ─────────────────────────────────────────────

class User(SQLModel):
    id: int | None = Field(default=None, primary_key=True)
    email: EmailStr = Field(index=True, nullable=False, unique=True)
    first_name: str = Field(index=True, nullable=False)
    second_name: str = Field(index=True, nullable=False)
    colour: str = Field(default="RED")
    role : str = Field(default="read-only-user")

class UserCreate(BaseModel):
    email: EmailStr
    first_name: str
    surename: str
    colour: Optional[str] = "RED"
    password: Annotated[str, Query(min_length=8, max_length=72)]

class UserDB(User, table=True):
    hashed_password: str

class UserForm(BaseModel):
    email: str
    given_password: str

class TimeSlot(str, Enum):
    Morning = "Morning"
    Evening = "Evening"

class Timetable(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    day: datetime.date = Field(nullable=False)
    time: TimeSlot = Field(nullable=False)
    assigned: int | None = Field(default=None, foreign_key="userdb.id")
    __table_args__ = (UniqueConstraint("day", "time", name="only_single_date_time"),)

class TimetablePublic(BaseModel):
    id: int
    day: datetime.date
    time: TimeSlot
    assigned: str | None


class TimetableData(BaseModel):
    weekStart: datetime.date
    timetable: list[TimetablePublic]


# ─────────────────────────────────────────────
#               UTILS
# ─────────────────────────────────────────────

def get_last_monday(date: datetime.date | None = None):
    if date is None:
        date = datetime.date.today()
    return date - datetime.timedelta(days=date.weekday())

def week_dependency(week: datetime.date | None = None):
    return get_last_monday(week)

def get_dog_walkers_for_today() -> dict:
    date = datetime.date.today()
    with Session(engine) as session:
        today_dog_walkers = session.exec(
            select(Timetable).where(Timetable.day == date)
        ).all()

        return {t.time : t.assigned for t in today_dog_walkers}

def get_email_list() -> list:
    with Session(engine) as session:
        emails = session.exec(
            select(UserDB.email).where(UserDB.role.in_(["admin", "user"]))
        ).all()
        return list(emails)

def add_weeks_dates(week : datetime.date | None = None):
    last_monday = get_last_monday(week)
    this_week_days = [last_monday + datetime.timedelta(days=i) for i in range(7)]

    timetable_entries = [
        Timetable(day=day, time=time_slot)
        for day in this_week_days
        for time_slot in TimeSlot
    ]

    with Session(engine) as session:
        existing_entries = session.exec(
            select(Timetable).where(Timetable.day.in_(this_week_days))
        ).all()
        existing_set = {(t.day, t.time) for t in existing_entries}

        new_entries = [
            t for t in timetable_entries if (t.day, t.time) not in existing_set
        ]

        session.add_all(new_entries)
        session.commit()


def create_test_user(test_email : str, test_password : str):
    test_user = UserDB(
        email=test_email,
        first_name="Test",
        second_name="User",
        colour="BLUE",
        hashed_password=get_password_hash(test_password),
        role="admin"
    )

    with Session(engine) as session:
        exists = session.exec(
            select(UserDB).where(UserDB.email == test_user.email)
        ).first()
        if not exists:
            session.add(test_user)
            session.commit()


# ─────────────────────────────────────────────
#               DB INIT / SESSION
# ─────────────────────────────────────────────

def get_session():
    with Session(engine) as session:
        yield session


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


SessionDep = Annotated[Session, Depends(get_session)]
