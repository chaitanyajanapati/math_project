"""Authentication router for user registration and login."""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

from app.models.auth import UserCreate, UserLogin, Token, User
from app.utils.auth import (
    authenticate_user,
    create_user,
    create_access_token,
    get_current_active_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """Register a new user."""
    try:
        logger.info(f"Registration attempt for email: {user_data.email}")
        
        user = create_user(
            email=user_data.email,
            username=user_data.username,
            password=user_data.password,
            grade=user_data.grade
        )
        
        logger.info(f"User registered successfully: {user_data.email}")
        
        # Return user without hashed_password
        return User(
            id=user["id"],
            email=user["email"],
            username=user["username"],
            grade=user["grade"],
            is_active=user["is_active"],
            created_at=user["created_at"]
        )
        
    except ValueError as e:
        logger.warning(f"Registration failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Registration error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login and get access token."""
    logger.info(f"Login attempt for: {form_data.username}")
    
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        logger.warning(f"Login failed for: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"], "user_id": user["id"]},
        expires_delta=access_token_expires
    )
    
    logger.info(f"Login successful for: {form_data.username}")
    
    # Return token and user info
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=User(
            id=user["id"],
            email=user["email"],
            username=user["username"],
            grade=user["grade"],
            is_active=user["is_active"],
            created_at=user["created_at"]
        )
    )


@router.get("/me", response_model=User)
async def get_me(current_user: User = Depends(get_current_active_user)):
    """Get current user info."""
    return current_user


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_active_user)):
    """Logout (client should delete token)."""
    logger.info(f"User logged out: {current_user.email}")
    return {"message": "Successfully logged out"}
