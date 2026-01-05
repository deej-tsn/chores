from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlmodel import Session, select

from app.config import get_settings

from ..database.db import SessionDep, User, UserDB, get_session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")
settings = get_settings()

SECRET_KEY = settings.secret_key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class Token(BaseModel):
    access_token : str
    token_type : str

class TokenData(BaseModel):
    sub : str
    first_name : str
    second_name : str
    colour : str
    role: str
    iat : datetime
    exp : datetime

def create_access_token(data: dict):
    to_encode = data.copy()
    current_time = datetime.now()
    expire = current_time + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "iat" : current_time })
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(request : Request, session : Session = Depends(get_session)) -> TokenData:
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token = request.cookies.get("access_token")
    if token is None:
        raise credentials_exception
    try:
        payload : dict[str, any]= jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get('sub')
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # check that user still in database
    
    statement = select(UserDB).where(UserDB.email == email)
    found_user = session.exec(statement).first()
    if not found_user:
        raise credentials_exception
    return TokenData(**payload)

def require_admin(session : SessionDep, current_user: TokenData = Depends(get_current_user)) -> UserDB:
    ## search db from role
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    statement = select(UserDB).where(UserDB.email == current_user.sub)
    found_user = session.exec(statement).first()
    if not found_user:
        raise credentials_exception
    if found_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admins only"
        )
    return found_user