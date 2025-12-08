
from datetime import timedelta, date
from typing import Annotated

from fastapi import Depends, FastAPI, Form, HTTPException, Query, Response
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlmodel import select, update

from .utils.database.db import SessionDep, Timetable, TimetableData, TimetablePublic, User, UserCreate, UserDB, add_weeks_dates, create_db_and_tables, get_last_monday, create_test_user, week_dependency

from .utils.auth.jwt import TokenData, create_access_token, get_current_user, require_admin
from .utils.auth.password import get_password_hash, verify_password

from .config import Settings

origins = [
    "https://local.app.com:5173",
    "https://chores.dempseypalaciotascon.com",
    "https://www.chores.dempseypalaciotascon.com"
]

app = FastAPI(root_path="/api", redirect_slashes=True)

def get_settings():
    return Settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    settings = get_settings()
    if settings.environment == "DEV":
        add_weeks_dates()
        if settings.test_user_email == "":
            raise KeyError("No 'TEST_USER_EMAIL' found in env")
        if settings.test_user_email == "":
            raise KeyError("No 'TEST_USER_PASSWORD' found in env")
        create_test_user(test_email=settings.test_user_email, test_password=settings.test_user_password)

@app.post("/token")
async def login_for_access_token(response: Response, session: SessionDep, user : OAuth2PasswordRequestForm = Depends()):
    statement = select(UserDB).where(UserDB.email == user.username)
    found_user = session.exec(statement).first()
    if found_user is None or not verify_password(user.password, found_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(data={
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

@app.post("/users/")
def create_user(response:Response, user: Annotated[UserCreate, Form()], session: SessionDep) -> User:
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
        role="user"
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    access_token = create_access_token(data={
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

@app.get("/logout")
def logout(response: Response):
    response.delete_cookie(key="access_token", path="/")
    return {'message' : 'logged out'}

@app.get("/timetable")
def get_timetable(session : SessionDep, week : date = Depends(week_dependency)) -> TimetableData:
    current_date = date.today()
    last_monday = get_last_monday(week)
    week_data_statement = select(Timetable, UserDB).join(UserDB, isouter=True).where(Timetable.day >= last_monday).where(Timetable.day < last_monday + timedelta(days=7))
    week_data = session.exec(week_data_statement).all()
    if(len(week_data) == 0):
        if(last_monday > current_date and ((last_monday - current_date) <= timedelta(weeks=2))):
            add_weeks_dates(last_monday)
            return get_timetable(session=session, week=last_monday)

    timetable = []
    for (row,user) in week_data:
        name = None
        if(user):
            name = user.first_name
        timetable.append(TimetablePublic(
            id=row.id,
            day=row.day,
            time=row.time,
            assigned=name
        ))
    return TimetableData(weekStart=last_monday, timetable=timetable)

class UpdateTimetableRequest(BaseModel):
    dayID : int
    assign_to_self : bool | None = None
    week : date

@app.patch("/timetable")
def update_timetable(data : UpdateTimetableRequest, session : SessionDep, user: TokenData = Depends(get_current_user)) -> TimetableData:
    assignment = None
    if(data.assign_to_self):
        user_db = session.exec(select(UserDB).where(UserDB.email == user.sub)).first()
        if user_db is None:
            raise HTTPException(status_code=404, detail="User Not Found")
        assignment = user_db.id
    update_statement = update(Timetable).where(Timetable.id == data.dayID).values(assigned=assignment)
    session.exec(update_statement)
    session.commit()
    return get_timetable(session, week=data.week)