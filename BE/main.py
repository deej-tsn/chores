
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import select

from utils.database.db import SessionDep, User, UserCreate, UserDB, create_db_and_tables, get_session

from utils.auth.jwt import Token, TokenData, create_access_token, get_current_user
from utils.auth.password import get_password_hash, verify_password

origins = [
    "http://localhost:5173"
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

@app.post("/token")
async def login_for_access_token(session: SessionDep, user : OAuth2PasswordRequestForm = Depends()) -> Token:
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
    return Token(access_token=access_token, token_type="bearer")

@app.post("/users/")
def create_user(user: UserCreate, session: SessionDep) -> User:
    existing_user = session.exec(select(UserDB).where(UserDB.email == user.email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = get_password_hash(user.password)
        # Create DB object
    db_user = UserDB(
        email=user.email,
        first_name=user.first_name,
        second_name=user.second_name,
        colour=user.colour,
        hashed_password=hashed_password
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)

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