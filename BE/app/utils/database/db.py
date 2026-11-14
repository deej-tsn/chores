import os
import datetime
from enum import Enum
from typing import Annotated, Optional

from fastapi import Depends, Query
from pydantic import BaseModel, EmailStr
from sqlalchemy import func
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
#           HOME CHORES (FORTNIGHTLY)
# ─────────────────────────────────────────────

class HomeChore(SQLModel, table=True):
    """Catalogue of fortnightly household chores (house cleaning, grocery shopping, ...)."""
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, nullable=False, unique=True)
    description: str = Field(default="")
    # Soft delete: deactivating a chore keeps its historical assignments intact.
    active: bool = Field(default=True)

class HomeChoreAssignment(SQLModel, table=True):
    """One chore, in one fortnight. `period_start` is the anchored fortnight Monday."""
    id: int | None = Field(default=None, primary_key=True)
    period_start: datetime.date = Field(nullable=False, index=True)
    chore_id: int = Field(nullable=False, foreign_key="homechore.id")
    __table_args__ = (
        UniqueConstraint("period_start", "chore_id", name="only_single_chore_per_period"),
    )

class HomeChoreClaim(SQLModel, table=True):
    """Zero or more owners per assignment — the same chore can be shared."""
    id: int | None = Field(default=None, primary_key=True)
    assignment_id: int = Field(nullable=False, foreign_key="homechoreassignment.id")
    user_id: int = Field(nullable=False, foreign_key="userdb.id")
    __table_args__ = (
        UniqueConstraint("assignment_id", "user_id", name="only_single_claim_per_user"),
    )

class HomeChorePublic(BaseModel):
    id: int                    # assignment id; PATCH targets this
    chore: str
    description: str
    claimed_by: list[str]
    claimed_by_me: bool        # computed server-side: first names are not unique keys

class HomeChorePeriodData(BaseModel):
    periodStart: datetime.date
    chores: list[HomeChorePublic]


# ─────────────────────────────────────────────
#               UTILS
# ─────────────────────────────────────────────

def get_last_monday(date: datetime.date | None = None):
    if date is None:
        date = datetime.date.today()
    return date - datetime.timedelta(days=date.weekday())

def week_dependency(week: datetime.date | None = None):
    return get_last_monday(week)

# Fortnights are anchored to a fixed Monday. This is a permanent contract:
# changing it re-keys every existing period and orphans existing claims.
FORTNIGHT_ANCHOR = datetime.date(2025, 12, 8)
FORTNIGHTS_IN_DAYS = 14

def get_fortnight_start(d: datetime.date | None = None) -> datetime.date:
    """Normalise any date to the Monday that starts its fortnight."""
    d = d or datetime.date.today()
    # Floor division keeps pre-anchor dates in the correct earlier period.
    offset = ((d - FORTNIGHT_ANCHOR).days // FORTNIGHTS_IN_DAYS) * FORTNIGHTS_IN_DAYS
    return FORTNIGHT_ANCHOR + datetime.timedelta(days=offset)

def fortnight_dependency(period: datetime.date | None = None) -> datetime.date:
    return get_fortnight_start(period)

def get_dog_walkers_for_today() -> dict:
    today = datetime.date.today()
    with Session(engine) as session:
        stmt = (
            select(
                Timetable.time,
                func.coalesce(
                     (UserDB.first_name + " " + UserDB.second_name),
                    "Unassigned"
                ).label("name")
            )
            .join(UserDB, UserDB.id == Timetable.assigned, isouter=True)
            .where(Timetable.day == today)
        )

        rows = session.exec(stmt).all()

        return {time.value : name for time, name in rows}

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


DEFAULT_HOME_CHORES = (
    ("Clean the house", "Whole-house clean: kitchen, bathroom, floors."),
    ("Grocery shopping", "Run the household grocery shop."),
)

def create_home_chores() -> None:
    """Insert any missing catalogue rows. Safe to run on every startup."""
    with Session(engine) as session:
        existing_names = set(session.exec(select(HomeChore.name)).all())
        new_chores = [
            HomeChore(name=name, description=description)
            for name, description in DEFAULT_HOME_CHORES
            if name not in existing_names
        ]
        if not new_chores:
            return
        session.add_all(new_chores)
        session.commit()

def add_period_assignments(session: Session, period_start: datetime.date) -> None:
    """Insert the missing (period, chore) rows for one fortnight.

    Takes the caller's session on purpose. `add_weeks_dates()` opens its own
    `Session(engine)`, which escapes the `get_session` test override and writes
    to the real database — do not copy that pattern here.
    """
    period_start = get_fortnight_start(period_start)
    active_chores = session.exec(select(HomeChore).where(HomeChore.active)).all()
    existing_chore_ids = set(
        session.exec(
            select(HomeChoreAssignment.chore_id).where(
                HomeChoreAssignment.period_start == period_start
            )
        ).all()
    )
    new_assignments = [
        HomeChoreAssignment(period_start=period_start, chore_id=chore.id)
        for chore in active_chores
        if chore.id is not None and chore.id not in existing_chore_ids
    ]
    if not new_assignments:
        return
    session.add_all(new_assignments)
    session.commit()

def seed_current_home_chore_period() -> None:
    """Startup helper: make sure the current fortnight exists in every environment."""
    with Session(engine) as session:
        add_period_assignments(session, get_fortnight_start())

def get_home_chores_for_period(
    session: Session, period_start: datetime.date
) -> list[tuple[HomeChoreAssignment, HomeChore, list[tuple[int, str]]]]:
    """Return (assignment, chore, [(user_id, first_name)]) for one fortnight."""
    rows = session.exec(
        select(HomeChoreAssignment, HomeChore)
        .join(HomeChore, HomeChore.id == HomeChoreAssignment.chore_id)
        .where(HomeChoreAssignment.period_start == period_start)
        .order_by(HomeChore.name)
    ).all()

    claim_rows = session.exec(
        select(HomeChoreClaim.assignment_id, UserDB.id, UserDB.first_name)
        .join(UserDB, UserDB.id == HomeChoreClaim.user_id)
        .join(HomeChoreAssignment, HomeChoreAssignment.id == HomeChoreClaim.assignment_id)
        .where(HomeChoreAssignment.period_start == period_start)
        .order_by(UserDB.first_name)
    ).all()

    claims_by_assignment: dict[int, list[tuple[int, str]]] = {}
    for assignment_id, user_id, first_name in claim_rows:
        claims_by_assignment.setdefault(assignment_id, []).append((user_id, first_name))

    return [
        (assignment, chore, claims_by_assignment.get(assignment.id or -1, []))
        for assignment, chore in rows
    ]

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

def create_guest_user():
    guest_user = UserDB(
        email="guest@example.com",
        first_name="Guest",
        second_name="User",
        colour="GREEN",
        hashed_password=get_password_hash("guestpassword"),
        role="guest"
    )

    with Session(engine) as session:
        exists = session.exec(
            select(UserDB).where(UserDB.email == guest_user.email)
        ).first()
        if not exists:
            session.add(guest_user)
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
