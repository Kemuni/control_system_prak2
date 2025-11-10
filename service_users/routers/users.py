import logging

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional
import math

from database import get_db
from errors import ApiException
from models import User
from schemas import (
    UserResponse, UserUpdate, ApiResponse, 
    ErrorDetail, PaginatedUsers
)
from auth import get_current_user, require_admin

router = APIRouter(prefix="/users", tags=["Users"])
logger = logging.getLogger(__name__)


@router.get("/me", response_model=ApiResponse)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Получаем профиль текущего пользователя"""
    try:
        return ApiResponse(
            success=True,
            data=UserResponse.model_validate(current_user).model_dump(mode='json'),
            error=None
        )
    except Exception as e:
        logger.error(f"Users service error: {str(e)}")
        raise ApiException("FETCH_PROFILE_FAILED", "Error during fetching profile")


@router.put("/me", response_model=ApiResponse)
async def update_current_user_profile(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Обновляем профиль текущего пользователя"""
    try:
        # Проверяем что новая почта не совпадает с текущей и не имеется у других пользователей
        if update_data.email and update_data.email != current_user.email:
            existing_user = db.query(User).filter(User.email == update_data.email).first()
            if existing_user:
                raise ApiException("EMAIL_ALREADY_EXISTS", "User with this email already exists")
        
        # Обновление полей
        if update_data.name is not None:
            current_user.name = update_data.name
        if update_data.email is not None:
            current_user.email = update_data.email
        
        db.commit()
        db.refresh(current_user)
        
        return ApiResponse(
            success=True,
            data=UserResponse.model_validate(current_user).model_dump(mode='json'),
            error=None
        )
    
    except Exception as e:
        db.rollback()
        logger.error(f"Users service error: {str(e)}")
        raise ApiException("UPDATE_PROFILE_FAILED", "Error during updating profile")


@router.get("/", response_model=ApiResponse)
async def get_all_users(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search by name or email"),
    role: Optional[str] = Query(None, description="Filter by role"),
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Получаем всех пользователей с пагинацией (только для админов)"""
    try:
        query = db.query(User)
        
        # Применяем фильтры
        if search:
            query = query.filter(
                or_(
                    User.name.ilike(f"%{search}%"),
                    User.email.ilike(f"%{search}%")
                )
            )
        
        if role:
            query = query.filter(User.roles.contains([role]))
        
        # Получаем общее кол-во пользователей с текущими фильтрами
        total = query.count()
        
        # Считаем данные для пагинации
        pages = math.ceil(total / page_size)
        offset = (page - 1) * page_size

        users = query.offset(offset).limit(page_size).all()

        paginated_data = PaginatedUsers(
            items=[UserResponse.model_validate(user) for user in users],
            total=total,
            page=page,
            page_size=page_size,
            pages=pages
        )
        
        return ApiResponse(
            success=True,
            data=paginated_data.model_dump(mode='json'),
            error=None
        )
    
    except Exception as e:
        logger.error(f"Users service error: {str(e)}")
        raise ApiException("FETCH_USERS_FAILED", "Error during getting all users")
