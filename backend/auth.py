from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import logging

load_dotenv()

# Set up logging
logger = logging.getLogger(__name__)

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
if SECRET_KEY == "your-secret-key-change-in-production":
    logger.warning("Using default SECRET_KEY - change this in production!")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # Increased to 1 hour for easier testing

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security scheme
security = HTTPBearer()

# Hardcoded user for demo purposes
HARDCODED_USER = {
    "username": "admin",
    "email": "admin@example.com",
    "hashed_password": pwd_context.hash("admin123")
}

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class User(BaseModel):
    username: str
    email: Optional[str] = None

class UserInDB(User):
    hashed_password: str

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_user(username: str):
    if username == HARDCODED_USER["username"]:
        return UserInDB(**HARDCODED_USER)
    return None

def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        logger.info(f"Validating JWT token: {credentials.credentials[:20]}...")
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        logger.info(f"Token payload: {payload}")
        if username is None:
            logger.error("No username found in token payload")
            raise credentials_exception
        token_data = TokenData(username=username)
        logger.info(f"Token data: {token_data}")
    except JWTError as e:
        logger.error(f"JWT decode error: {str(e)}")
        raise credentials_exception
    except Exception as e:
        logger.error(f"Unexpected error in token validation: {str(e)}")
        raise credentials_exception
    
    user = get_user(username=token_data.username)
    if user is None:
        logger.error(f"User not found: {token_data.username}")
        raise credentials_exception
    
    logger.info(f"User authenticated successfully: {user.username}")
    return user
