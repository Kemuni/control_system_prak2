from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Any
from datetime import datetime
from uuid import UUID
from decimal import Decimal
from models import OrderStatus


class OrderItem(BaseModel):
    """Схема товара в заказе"""
    name: str = Field(..., min_length=1, max_length=200, description="Название товара")
    amount: int = Field(..., gt=0, description="Количество товара")
    description: str = Field(..., min_length=1, max_length=500, description="Описание товара")
    price: Decimal = Field(..., gt=0, description="Цена за единицу товара")
    
    @field_validator('price')
    @classmethod
    def validate_price(cls, v):
        """Проверяем что цена имеет не более 2 знаков после запятой"""
        if v.as_tuple().exponent < -2:
            raise ValueError("Цена должна иметь не более 2 знаков после запятой")
        return v


class OrderCreate(BaseModel):
    """Схема для создания заказа"""
    items: List[OrderItem] = Field(..., min_length=1, description="Список товаров в заказе")
    
    @field_validator('items')
    @classmethod
    def validate_items(cls, v):
        if not v:
            raise ValueError("Заказ должен содержать хотя бы один товар")
        return v


class OrderUpdate(BaseModel):
    """Схема для обновления статуса заказа"""
    status: OrderStatus = Field(..., description="Новый статус заказа")


class OrderResponse(BaseModel):
    """Схема заказа в ответах на запросы"""
    id: UUID
    user_id: UUID
    items: List[dict]
    status: OrderStatus
    total_amount: Decimal
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ErrorDetail(BaseModel):
    """Схема детали ошибки"""
    code: str
    message: str


class ApiResponse(BaseModel):
    """Стандартный ответ нашего API"""
    success: bool
    data: Optional[Any] = None
    error: Optional[ErrorDetail] = None


class PaginatedOrders(BaseModel):
    """Схема ответа списка заказов с пагинацией"""
    items: List[OrderResponse]
    total: int
    page: int
    page_size: int
    pages: int


class TokenData(BaseModel):
    """Схема payload в JWT"""
    user_id: Optional[str] = None
    email: Optional[str] = None
