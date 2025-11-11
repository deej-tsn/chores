from typing import Annotated
from fastapi import Depends, Query
from pydantic import BaseModel, EmailStr, constr
from sqlmodel import Field, Session, SQLModel, create_engine, select


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
    password: Annotated[str, Query(min_length=8,max_length=72)]  # plain password

class UserDB(User, table=True):
    hashed_password : str

class UserForm(BaseModel):
    email : str
    given_password : str

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