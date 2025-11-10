import logging
from datetime import timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from auth import hash_password, verify_password, create_access_token
from config import settings
from database import get_db
from errors import ApiException
from models import User
from schemas import (
    UserRegister, UserLogin, Token, UserResponse,
    ApiResponse, ErrorDetail
)

router = APIRouter(prefix="/auth", tags=["Authentication"])
logger = logging.getLogger(__name__)


@router.post("/register", status_code=201, response_model=ApiResponse)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Регистрация нового пользователя"""
    try:
        # Проверяем существует ли такой пользователь
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise ApiException("USER_ALREADY_EXISTS", "User with this email already exists")
        
        # Создаем нового пользователя
        new_user = User(
            email=str(user_data.email),
            password_hash=hash_password(user_data.password),
            name=user_data.name,
            roles=[role.value for role in user_data.roles]
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return ApiResponse(
            success=True,
            data=UserResponse.model_validate(new_user).model_dump(mode='json'),
            error=None
        )
    
    except Exception as e:
        db.rollback()
        logger.error(f"Users service error: {str(e)}")
        if isinstance(e, ApiException): raise e
        raise ApiException("REGISTRATION_FAILED", "Error during registration")


@router.post("/login", response_model=ApiResponse)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Авторизуем пользователя и возвращаем JWT токен"""
    try:
        user = db.query(User).filter(User.email == credentials.email).first()
        if not user or not verify_password(credentials.password, user.password_hash):
            raise ApiException("INVALID_CREDENTIALS", "Invalid email or password")
        
        # Создаем токен для авторизации
        access_token_expires = timedelta(minutes=settings.JWT_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email},
            expires_delta=access_token_expires
        )
        
        return ApiResponse(
            success=True,
            data=Token(access_token=access_token, token_type="bearer").model_dump(),
            error=None
        )
    
    except Exception as e:
        logger.error(f"Users service error: {str(e)}")
        if isinstance(e, ApiException): raise e
        raise ApiException("LOGIN_FAILED", "Error during login")
