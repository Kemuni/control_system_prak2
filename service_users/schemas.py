from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import List, Optional, Any
from datetime import datetime
from uuid import UUID
from enum import Enum


class UserRole(str, Enum):
    """Доступные роли пользователя"""
    ADMIN = "admin"
    CLIENT = "client"


class UserRegister(BaseModel):
    """Схема для регистрации пользователя"""
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    name: str = Field(..., min_length=1, max_length=100)
    roles: List[UserRole] = Field(default=[UserRole.CLIENT])
    
    @field_validator('roles')
    @classmethod
    def validate_roles(cls, v):
        if not v:
            return [UserRole.CLIENT]
        return v


class UserLogin(BaseModel):
    """Схема для авторизации пользователя"""
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """Схема для обновления пользователя"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None


class UserResponse(BaseModel):
    """Схема пользователя в ответах на запросы"""
    id: UUID
    email: str
    name: str
    roles: List[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """Схема JWT токена"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Схема payload в JWT"""
    user_id: Optional[str] = None
    email: Optional[str] = None


class ErrorDetail(BaseModel):
    """Схема детали ошибки"""
    code: str
    message: str


class ApiResponse(BaseModel):
    """Стандартный ответ нашего API"""
    success: bool
    data: Optional[Any] = None
    error: Optional[ErrorDetail] = None


class PaginatedUsers(BaseModel):
    """Схема ответа списка пользователя с пагинацией"""
    items: List[UserResponse]
    total: int
    page: int
    page_size: int
    pages: int
