import os
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "GYANPRAKASHKSUHWAHA")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 1440))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# This connects FastAPI's Swagger UI to your login route
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def verify_password(plain_password, hashed_password):
    print(f"--- DEBUG LOGIN --- Password length received: {len(plain_password)}")
    print(f"--- DEBUG LOGIN --- Password value: '{plain_password}'")
    
    # Truncate at the byte level to be absolutely bulletproof against Unicode/Emojis
    truncated = plain_password.encode('utf-8')[:72].decode('utf-8', 'ignore')
    return pwd_context.verify(truncated, hashed_password)

def get_password_hash(password):
    print(f"--- DEBUG SIGNUP --- Password length received: {len(password)}")
    print(f"--- DEBUG SIGNUP --- Password value: '{password}'")
    
    truncated = password.encode('utf-8')[:72].decode('utf-8', 'ignore')
    return pwd_context.hash(truncated)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme)):
    """Dependency to extract and verify the JWT token from the request."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Local import to prevent circular dependency
    from .database import get_user_by_email
    user = get_user_by_email(email)
    
    if user is None:
        raise credentials_exception
        
    return user