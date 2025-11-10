from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Any
from datetime import datetime
from uuid import UUID
from decimal import Decimal
from enum import Enum


# ============== User Schemas ==============

class UserRole(str, Enum):
    """Доступные роли пользователя"""
    ADMIN = "admin"
    CLIENT = "client"


class UserRegister(BaseModel):
    """Схема для регистрации пользователя"""
    email: EmailStr = Field(..., description="Email пользователя")
    password: str = Field(..., min_length=8, description="Пароль (минимум 8 символов)")
    name: str = Field(..., min_length=1, max_length=100, description="Имя пользователя")
    roles: List[UserRole] = Field(default=[UserRole.CLIENT], description="Роли пользователя")


class UserLogin(BaseModel):
    """Схема для авторизации пользователя"""
    email: EmailStr = Field(..., description="Email пользователя")
    password: str = Field(..., description="Пароль")


class UserUpdate(BaseModel):
    """Схема для обновления профиля пользователя"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Новое имя")
    email: Optional[EmailStr] = Field(None, description="Новый email")


class UserResponse(BaseModel):
    """Схема пользователя в ответах"""
    id: UUID = Field(..., description="Уникальный идентификатор пользователя")
    email: str = Field(..., description="Email пользователя")
    name: str = Field(..., description="Имя пользователя")
    roles: List[str] = Field(..., description="Роли пользователя")
    created_at: datetime = Field(..., description="Дата создания")
    updated_at: datetime = Field(..., description="Дата последнего обновления")


class Token(BaseModel):
    """Схема JWT токена"""
    access_token: str = Field(..., description="JWT токен для авторизации")
    token_type: str = Field(default="bearer", description="Тип токена")


class PaginatedUsers(BaseModel):
    """Схема ответа списка пользователей с пагинацией"""
    items: List[UserResponse] = Field(..., description="Список пользователей")
    total: int = Field(..., description="Общее количество пользователей")
    page: int = Field(..., description="Текущая страница")
    page_size: int = Field(..., description="Количество элементов на странице")
    pages: int = Field(..., description="Общее количество страниц")


# ============== Order Schemas ==============

class OrderStatus(str, Enum):
    """Статусы заказа"""
    CREATED = "CREATED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class OrderItem(BaseModel):
    """Схема товара в заказе"""
    name: str = Field(..., min_length=1, max_length=200, description="Название товара")
    amount: int = Field(..., gt=0, description="Количество товара")
    description: str = Field(..., min_length=1, max_length=500, description="Описание товара")
    price: Decimal = Field(..., gt=0, description="Цена за единицу товара")


class OrderCreate(BaseModel):
    """Схема для создания заказа"""
    items: List[OrderItem] = Field(..., min_length=1, description="Список товаров в заказе (минимум 1)")


class OrderUpdate(BaseModel):
    """Схема для обновления статуса заказа"""
    status: OrderStatus = Field(..., description="Новый статус заказа")


class OrderResponse(BaseModel):
    """Схема заказа в ответах"""
    id: UUID = Field(..., description="Уникальный идентификатор заказа")
    user_id: UUID = Field(..., description="Идентификатор пользователя")
    items: List[dict] = Field(..., description="Список товаров в заказе")
    status: OrderStatus = Field(..., description="Статус заказа")
    total_amount: Decimal = Field(..., description="Итоговая сумма заказа")
    created_at: datetime = Field(..., description="Дата создания заказа")
    updated_at: datetime = Field(..., description="Дата последнего обновления")


class PaginatedOrders(BaseModel):
    """Схема ответа списка заказов с пагинацией"""
    items: List[OrderResponse] = Field(..., description="Список заказов")
    total: int = Field(..., description="Общее количество заказов")
    page: int = Field(..., description="Текущая страница")
    page_size: int = Field(..., description="Количество элементов на странице")
    pages: int = Field(..., description="Общее количество страниц")


# ============== Common Schemas ==============

class ErrorDetail(BaseModel):
    """Схема детали ошибки"""
    code: str = Field(..., description="Код ошибки")
    message: str = Field(..., description="Сообщение об ошибке")


class ApiResponse(BaseModel):
    """Стандартный ответ API"""
    success: bool = Field(..., description="Статус выполнения запроса")
    data: Optional[Any] = Field(None, description="Данные ответа")
    error: Optional[ErrorDetail] = Field(None, description="Информация об ошибке")


# ============== Typed API Response Models ==============

class UserResponseSuccess(BaseModel):
    """Успешный ответ с данными пользователя"""
    success: bool = Field(True, description="Статус выполнения запроса")
    data: UserResponse = Field(..., description="Данные пользователя")
    error: Optional[ErrorDetail] = Field(None, description="Информация об ошибке")


class TokenResponseSuccess(BaseModel):
    """Успешный ответ с JWT токеном"""
    success: bool = Field(True, description="Статус выполнения запроса")
    data: Token = Field(..., description="JWT токен")
    error: Optional[ErrorDetail] = Field(None, description="Информация об ошибке")


class PaginatedUsersResponseSuccess(BaseModel):
    """Успешный ответ со списком пользователей"""
    success: bool = Field(True, description="Статус выполнения запроса")
    data: PaginatedUsers = Field(..., description="Список пользователей с пагинацией")
    error: Optional[ErrorDetail] = Field(None, description="Информация об ошибке")


class OrderResponseSuccess(BaseModel):
    """Успешный ответ с данными заказа"""
    success: bool = Field(True, description="Статус выполнения запроса")
    data: OrderResponse = Field(..., description="Данные заказа")
    error: Optional[ErrorDetail] = Field(None, description="Информация об ошибке")


class PaginatedOrdersResponseSuccess(BaseModel):
    """Успешный ответ со списком заказов"""
    success: bool = Field(True, description="Статус выполнения запроса")
    data: PaginatedOrders = Field(..., description="Список заказов с пагинацией")
    error: Optional[ErrorDetail] = Field(None, description="Информация об ошибке")
