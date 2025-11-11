from datetime import datetime, timedelta
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlmodel import Session, select

from utils.database.db import User, UserDB, get_session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

SECRET_KEY = "your-secret-key"
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
    iat : datetime
    exp : datetime

def create_access_token(data: dict):
    to_encode = data.copy()
    current_time = datetime.now()
    expire = current_time + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "iat" : current_time })
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), session : Session = Depends(get_session)) -> TokenData:
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
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