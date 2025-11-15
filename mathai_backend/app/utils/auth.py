"""Authentication utilities for JWT and password handling."""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import uuid
import json
from pathlib import Path

from app.models.auth import TokenData, User
from app.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# JWT settings
SECRET_KEY = getattr(settings, 'secret_key', "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[TokenData]:
    """Decode and verify JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        user_id: str = payload.get("user_id")
        if email is None:
            return None
        return TokenData(email=email, user_id=user_id)
    except JWTError:
        return None


# Simple user storage (will be replaced with database)
USERS_FILE = Path("data/users.json")


def get_user_by_email(email: str) -> Optional[dict]:
    """Get user by email from storage."""
    if not USERS_FILE.exists():
        return None
    
    try:
        users = json.loads(USERS_FILE.read_text())
        return users.get(email)
    except Exception:
        return None


def create_user(email: str, username: str, password: str, grade: int = 8) -> dict:
    """Create a new user."""
    USERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    # Load existing users
    users = {}
    if USERS_FILE.exists():
        try:
            users = json.loads(USERS_FILE.read_text())
        except Exception:
            pass
    
    # Check if user exists
    if email in users:
        raise ValueError("User already exists")
    
    # Create new user
    user_id = str(uuid.uuid4())
    user = {
        "id": user_id,
        "email": email,
        "username": username,
        "hashed_password": get_password_hash(password),
        "grade": grade,
        "is_active": True,
        "created_at": datetime.utcnow().isoformat()
    }
    
    users[email] = user
    USERS_FILE.write_text(json.dumps(users, indent=2))
    
    return user


def authenticate_user(email: str, password: str) -> Optional[dict]:
    """Authenticate a user."""
    user = get_user_by_email(email)
    if not user:
        return None
    if not verify_password(password, user["hashed_password"]):
        return None
    return user


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Get the current authenticated user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token_data = decode_access_token(token)
    if token_data is None or token_data.email is None:
        raise credentials_exception
    
    user = get_user_by_email(token_data.email)
    if user is None:
        raise credentials_exception
    
    # Convert to User model (exclude hashed_password)
    return User(
        id=user["id"],
        email=user["email"],
        username=user["username"],
        grade=user["grade"],
        is_active=user["is_active"],
        created_at=datetime.fromisoformat(user["created_at"])
    )


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get the current active user."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
