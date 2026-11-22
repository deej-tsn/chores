
from datetime import timedelta, date
from typing import Annotated

from fastapi import Depends, FastAPI, Form, HTTPException, Query, Response
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlmodel import Session, select, update

from .utils.stats.stats import get_count_per_person_since_start

from .utils.notifications.resend import start_notifications_scheduler

from .utils.database.db import (
    HomeChoreAssignment,
    HomeChoreClaim,
    HomeChorePeriodData,
    HomeChorePublic,
    SessionDep,
    Timetable,
    TimetableData,
    TimetablePublic,
    User,
    UserCreate,
    UserDB,
    add_period_assignments,
    add_weeks_dates,
    create_db_and_tables,
    create_guest_user,
    create_home_chores,
    create_test_user,
    fortnight_dependency,
    get_fortnight_start,
    get_home_chores_for_period,
    get_last_monday,
    seed_current_home_chore_period,
    week_dependency,
)

from .utils.auth.jwt import TokenData, create_access_token, get_current_user, get_optional_user, require_admin
from .utils.auth.password import get_password_hash, verify_password

from .config import get_settings, get_settings_dep

# The SPA dev origin. Do NOT add https://localhost:5173: the browser sends the origin string
# verbatim, and the app is meant to be opened at https://local.app.com:5173 (see AGENTS.md).
# "No 'Access-Control-Allow-Origin' header" on /token means the wrong URL was used.
origins = [
    "https://local.app.com:5173",
    "https://chores.dempseypalaciotascon.com",
    "https://www.chores.dempseypalaciotascon.com"
]

app = FastAPI(root_path="/api", redirect_slashes=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.on_event("startup")
def on_startup():
    settings = get_settings()

    # validation
    if settings.environment == "DEV":
        if not settings.test_user_email:
            raise KeyError("No 'TEST_USER_EMAIL' found in env")
        if not settings.test_user_password:
            raise KeyError("No 'TEST_USER_PASSWORD' found in env")

    # initialisation of database and notifications
    create_db_and_tables()
    start_notifications_scheduler(settings)

    if not settings.disable_guest_mode:
        create_guest_user()

    # home chores: catalogue + the current fortnight, in every environment
    create_home_chores()
    seed_current_home_chore_period()

    if settings.environment == "DEV":
        add_weeks_dates()
        create_test_user(
            test_email=settings.test_user_email,
            test_password=settings.test_user_password
        )

@app.post("/token")
async def login_for_access_token(response: Response, session: SessionDep, user : OAuth2PasswordRequestForm = Depends(), settings = Depends(get_settings_dep)):
    statement = select(UserDB).where(UserDB.email == user.username)
    found_user = session.exec(statement).first()
    if found_user is None or not verify_password(user.password, found_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(settings, data={
        "sub": found_user.email,
        "first_name": found_user.first_name,
        "second_name": found_user.second_name,
        "colour": found_user.colour,
        "role" : found_user.role
    })

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=3600,
        path="/",
    )

    return {'message' : 'token returned in cookie'}

@app.post("/logout")
def logout(response: Response):
    response.delete_cookie(
        key="access_token", 
        path="/",
        secure=True,
        samesite="none"
    )
    return {'message' : 'logged out'}

@app.post("/users/")
def create_user(response:Response, user: Annotated[UserCreate, Form()], session: SessionDep, settings= Depends(get_settings_dep)) -> User:
    existing_user = session.exec(select(UserDB).where(UserDB.email == user.email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = get_password_hash(user.password)
        # Create DB object
    db_user = UserDB(
        email=user.email,
        first_name=user.first_name,
        second_name=user.surename,
        colour=user.colour,
        hashed_password=hashed_password,
        role="read-only-user"
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    access_token = create_access_token(settings, data={
        "sub": db_user.email,
        "first_name": db_user.first_name,
        "second_name":db_user.second_name,
        "colour":db_user.colour,
        "role": db_user.role
    })

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=3600,
        path="/",
    )

    return db_user

@app.get("/users/")
def read_users(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
    user : UserDB = Depends(require_admin),
) -> list[User]:
    
    users = session.exec(select(UserDB).offset(offset).limit(limit)).all()
    return users

@app.get("/users/{user_id}")
def read_user(user_id: int, session: SessionDep, _ : UserDB = Depends(require_admin)) -> User:
    user = session.get(UserDB, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/user")
def get_user_from_token(user : TokenData = Depends(get_current_user)) -> TokenData:
    return user

@app.get("/chores/dog-walking")
def get_timetable(session : SessionDep, week : date = Depends(week_dependency)) -> TimetableData:
    current_date = date.today()
    last_monday = get_last_monday(week)

    week_data_statement = (
        select(Timetable, UserDB)
        .join(UserDB, isouter=True)
        .where(Timetable.day >= last_monday)
        .where(Timetable.day < last_monday + timedelta(days=7))
    )

    week_data = session.exec(week_data_statement).all()

    if len(week_data) == 0:
        # Generate data for the current week or the next 2 weeks
        if last_monday >= get_last_monday(current_date) and (
            last_monday - get_last_monday(current_date) <= timedelta(weeks=2)
        ):
            add_weeks_dates(last_monday)

            # Re-fetch the newly generated data
            week_data = session.exec(week_data_statement).all()

    timetable = []

    for row, user in week_data:
        name = None
        if user:
            name = user.first_name

        timetable.append(
            TimetablePublic(
                id=row.id,
                day=row.day,
                time=row.time,
                assigned=name
            )
        )

    return TimetableData(
        weekStart=last_monday,
        timetable=timetable
    )

class UpdateTimetableRequest(BaseModel):
    dayID : int
    assign_to_self : bool | None = None
    week : date

@app.patch("/chores/dog-walking")
def update_timetable(data : UpdateTimetableRequest, session : SessionDep, user: TokenData = Depends(get_current_user)) -> TimetableData:
    assignment = None
    if(data.assign_to_self):
        user_db = session.exec(select(UserDB).where(UserDB.email == user.sub)).first()
        if user_db is None:
            raise HTTPException(status_code=404, detail="User Not Found")
        if user_db.role not in ["admin", "user"]:
            raise HTTPException(status_code=401, detail="Unauthorised")
        assignment = user_db.id
    update_statement = update(Timetable).where(Timetable.id == data.dayID).values(assigned=assignment)
    session.exec(update_statement)
    session.commit()
    return get_timetable(session, week=data.week)

def build_home_chore_period(
    session: Session, period_start: date, viewer_email: str | None
) -> HomeChorePeriodData:
    viewer_id = None
    if viewer_email is not None:
        viewer = session.exec(select(UserDB).where(UserDB.email == viewer_email)).first()
        if viewer is not None:
            viewer_id = viewer.id

    chores = [
        HomeChorePublic(
            id=assignment.id,
            chore=chore.name,
            description=chore.description,
            claimed_by=[first_name for _, first_name in claims],
            claimed_by_me=any(user_id == viewer_id for user_id, _ in claims),
        )
        for assignment, chore, claims in get_home_chores_for_period(session, period_start)
    ]

    return HomeChorePeriodData(periodStart=period_start, chores=chores)

@app.get("/chores/home")
def get_home_chores(
    session : SessionDep,
    period : date = Depends(fortnight_dependency),
    user : TokenData | None = Depends(get_optional_user),
) -> HomeChorePeriodData:
    # Lazily seed the current fortnight and the next one, like the dog rota does
    # for weeks. Past periods stay empty rather than inventing assignments.
    current_period = get_fortnight_start(date.today())
    if current_period <= period <= current_period + timedelta(days=14):
        add_period_assignments(session, period)

    return build_home_chore_period(session, period, user.sub if user else None)

class UpdateHomeChoreRequest(BaseModel):
    assignmentID : int
    claimed : bool
    period : date

@app.patch("/chores/home")
def update_home_chore(
    data : UpdateHomeChoreRequest,
    session : SessionDep,
    user: TokenData = Depends(get_current_user),
) -> HomeChorePeriodData:
    user_db = session.exec(select(UserDB).where(UserDB.email == user.sub)).first()
    if user_db is None:
        raise HTTPException(status_code=404, detail="User Not Found")
    if user_db.role not in ["admin", "user"]:
        # Same 401 convention as PATCH /chores/dog-walking — the role matrix asserts it.
        raise HTTPException(status_code=401, detail="Unauthorised")

    assignment = session.get(HomeChoreAssignment, data.assignmentID)
    if assignment is None:
        raise HTTPException(status_code=404, detail="Chore Not Found")

    claim = session.exec(
        select(HomeChoreClaim)
        .where(HomeChoreClaim.assignment_id == data.assignmentID)
        .where(HomeChoreClaim.user_id == user_db.id)
    ).first()

    # Explicit `claimed` keeps the operation idempotent and safe to retry, and
    # means one person can never remove somebody else's claim.
    if data.claimed and claim is None:
        session.add(HomeChoreClaim(assignment_id=data.assignmentID, user_id=user_db.id))
        session.commit()
    elif not data.claimed and claim is not None:
        session.delete(claim)
        session.commit()

    return build_home_chore_period(session, get_fortnight_start(data.period), user_db.email)

@app.get("/count")
def get_total_stats_since_start( session : SessionDep, _ : UserDB = Depends(require_admin)):
    return get_count_per_person_since_start(session)

