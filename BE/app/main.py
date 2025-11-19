
from datetime import timedelta
from typing import Annotated

from fastapi import Depends, FastAPI, Form, HTTPException, Query, Response
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlmodel import select, update

from .utils.database.db import SessionDep, Timetable, TimetablePublic, User, UserCreate, UserDB, add_this_weeks_dates, create_db_and_tables, get_last_monday, create_test_user

from .utils.auth.jwt import TokenData, create_access_token, get_current_user
from .utils.auth.password import get_password_hash, verify_password

origins = [
    "https://local.app.com:5173"
]

app = FastAPI()

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
    add_this_weeks_dates()
    create_test_user()

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
        "colour": found_user.colour
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
        hashed_password=hashed_password
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    access_token = create_access_token(data={
        "sub": db_user.email,
        "first_name": db_user.first_name,
        "second_name":db_user.second_name,
        "colour":db_user.colour
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
    _ : TokenData = Depends(get_current_user),
) -> list[User]:
    users = session.exec(select(UserDB).offset(offset).limit(limit)).all()
    return users

@app.get("/users/{user_id}")
def read_user(user_id: int, session: SessionDep) -> User:
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
def get_timetable(session : SessionDep) -> list[TimetablePublic]:
    last_monday = get_last_monday()
    this_week_data_statement = select(Timetable, UserDB).join(UserDB, isouter=True).where(Timetable.day >= last_monday).where(Timetable.day < last_monday + timedelta(days=7))
    this_week_data = session.exec(this_week_data_statement).all()
    result = []
    for (date,user) in this_week_data:
        name = None
        if(user):
            name = user.first_name
        result.append(TimetablePublic(
            id=date.id,
            day=date.day,
            time=date.time,
            assigned=name
        ))
    return result

class UpdateTimetableRequest(BaseModel):
    dayID : int
    assign_to_self : bool | None = None

@app.patch("/timetable")
def update_timetable(data : UpdateTimetableRequest, session : SessionDep, user: TokenData = Depends(get_current_user)) -> list[TimetablePublic]:
    assignment = None
    if(data.assign_to_self):
        user_db = session.exec(select(UserDB).where(UserDB.email == user.sub)).first()
        if user_db is None:
            raise HTTPException(status_code=404, detail="User Not Found")
        assignment = user_db.id
    update_statement = update(Timetable).where(Timetable.id == data.dayID).values(assigned=assignment)
    session.exec(update_statement)
    session.commit()
    return get_timetable(session)