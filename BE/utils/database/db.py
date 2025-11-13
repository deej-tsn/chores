import datetime
from enum import Enum
from typing import Annotated
from ..auth.password import get_password_hash
from fastapi import Depends, Query
from pydantic import BaseModel, EmailStr, constr
from sqlmodel import Date, Field, Session, SQLModel, create_engine, select, UniqueConstraint


class User(SQLModel):
    id: int | None = Field(default=None, primary_key=True)
    email : EmailStr = Field(index=True, nullable=False, unique=True)
    first_name : str = Field(index=True, nullable=False)
    second_name : str = Field(index=True, nullable=False)
    colour : str = Field(default='RED')

class UserCreate(BaseModel):
    email: EmailStr
    first_name: str
    second_name: str
    colour: str = "RED"
    password: Annotated[str, Query(min_length=8,max_length=72)]

class UserDB(User, table=True):
    hashed_password : str

class UserForm(BaseModel):
    email : str
    given_password : str

class TimeSlot(str, Enum):
    Morning = "Morning"
    Evening = "Evening"

class Timetable(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    day : datetime.date = Field(nullable=False)
    time : TimeSlot = Field(nullable=False)
    assigned : int | None = Field(default=None, foreign_key="userdb.id")
    __table_args__ = (UniqueConstraint("day" , "time", name='only_single_date_time'),)

class TimetablePublic(BaseModel):
    id: int
    day : datetime.date
    time : TimeSlot
    assigned : str | None

def get_last_monday() -> datetime.date:
    today = datetime.date.today()
    days_ahead = today.weekday()  # Monday is 0
    last_monday = today - datetime.timedelta(days=days_ahead)
    return last_monday

def add_this_weeks_dates():
    last_monday = get_last_monday()
    this_week_days = [last_monday + datetime.timedelta(days=i) for i in range(7)]

    timetable_entries = [
        Timetable(day=day, time=time_slot)
        for day in this_week_days
        for time_slot in TimeSlot
    ]
    with Session(engine) as session:
        # Fetch existing entries for next week
        existing_entries = session.exec(
            select(Timetable).where(Timetable.day.in_(this_week_days))
        ).all()
        existing_set = {(t.day, t.time) for t in existing_entries}

        # Filter out duplicates
        new_entries = [
            t for t in timetable_entries if (t.day, t.time) not in existing_set
        ]

        # Add all new entries at once
        session.add_all(new_entries)
        session.commit()

# while in development testing
def create_test_user():
    test_password = 'testing12345'
    test_user = UserDB(
        email="test@hotmail.com",
        first_name="Test",
        second_name="User",
        colour="BLUE",
        hashed_password=get_password_hash(test_password)
    )
    with Session(engine) as session:
        existing_user = session.exec(
            select(UserDB).where(UserDB.email == test_user.email)
        ).first()
        if not existing_user:
            session.add(test_user)
            session.commit()
    
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def get_session():
    with Session(engine) as session:
        yield session

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

SessionDep = Annotated[Session, Depends(get_session)]