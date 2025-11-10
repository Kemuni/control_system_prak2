import logging

from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
from typing import Optional
from uuid import UUID
from decimal import Decimal
import math

from starlette.responses import JSONResponse

from database import get_db
from errors import ApiException
from models import Order, OrderStatus
from schemas import (
    OrderCreate, OrderUpdate, OrderResponse, ApiResponse, 
    ErrorDetail, PaginatedOrders
)
from auth import get_current_user_id

router = APIRouter(prefix="/orders", tags=["Orders"])
logger = logging.getLogger(__name__)

@router.post("/", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    current_user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Создание нового заказа"""
    try:
        # Вычисляем общую сумму заказа
        total_amount = Decimal(0)
        items_list = []
        
        for item in order_data.items:
            item_dict = item.model_dump(mode='json')
            items_list.append(item_dict)
            total_amount += item.price * item.amount
        
        # Создаем новый заказ
        new_order = Order(
            user_id=current_user_id,
            items=items_list,
            status=OrderStatus.CREATED,
            total_amount=total_amount
        )
        
        db.add(new_order)
        db.commit()
        db.refresh(new_order)
        
        return ApiResponse(
            success=True,
            data=OrderResponse.model_validate(new_order).model_dump(mode='json'),
            error=None
        )
    
    except Exception as e:
        db.rollback()
        logger.error(f"Order creation failed: {str(e)}")
        raise ApiException("ORDER_CREATION_FAILED", "Order creation failed")


@router.get("/{order_id}", response_model=ApiResponse)
async def get_order(
    order_id: UUID,
    current_user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Получение заказа по идентификатору"""
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        
        if not order:
            return ApiResponse(
                success=False,
                data=None,
                error=ErrorDetail(
                    code="ORDER_NOT_FOUND",
                    message="Order not found"
                )
            )
        
        # Проверяем права доступа - пользователь может видеть только свои заказы
        if order.user_id != current_user_id:
            raise ApiException(
                code="ACCESS_DENIED",
                message="You don't have permission to view this order"
            )
        
        return ApiResponse(
            success=True,
            data=OrderResponse.model_validate(order).model_dump(mode='json'),
            error=None
        )
    
    except Exception as e:
        logger.error(f"Order retrieval failed: {str(e)}")
        raise ApiException(
            code="FETCH_ORDER_FAILED",
            message="Order retrieval failed"
        )


@router.get("/", response_model=ApiResponse)
async def get_user_orders(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    status_filter: Optional[OrderStatus] = Query(None, description="Filter by status"),
    sort_by: str = Query("created_at", description="Sort field (created_at, updated_at, total_amount)"),
    sort_order: str = Query("desc", description="Sort order (asc, desc)"),
    current_user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Получение списка заказов текущего пользователя с пагинацией и сортировкой"""
    try:
        # Базовый запрос - только заказы текущего пользователя
        query = db.query(Order).filter(Order.user_id == current_user_id)
        
        # Применяем фильтр по статусу
        if status_filter:
            query = query.filter(Order.status == status_filter)
        
        # Применяем сортировку
        sort_column = getattr(Order, sort_by, Order.created_at)
        if sort_order == "asc":
            query = query.order_by(asc(sort_column))
        else:
            query = query.order_by(desc(sort_column))
        
        # Получаем общее количество заказов с текущими фильтрами
        total = query.count()
        
        # Считаем данные для пагинации
        pages = math.ceil(total / page_size) if total > 0 else 1
        offset = (page - 1) * page_size
        
        orders = query.offset(offset).limit(page_size).all()
        
        paginated_data = PaginatedOrders(
            items=[OrderResponse.model_validate(order) for order in orders],
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
        raise ApiException(
            code="FETCH_ORDERS_FAILED",
            message="Orders retrieval failed"
        )


@router.put("/{order_id}/status", response_model=ApiResponse)
async def update_order_status(
    order_id: UUID,
    update_data: OrderUpdate,
    current_user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Обновление статуса заказа"""
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        
        if not order:
            raise ApiException(
                code="ORDER_NOT_FOUND",
                message="Order not found"
            )
        
        # Проверяем права доступа - пользователь может изменять только свои заказы
        if order.user_id != current_user_id:
            raise ApiException(
                code="ACCESS_DENIED",
                message="You don't have permission to update this order"
            )
        
        # Проверяем валидность изменения статуса
        if order.status == OrderStatus.CANCELLED:
            raise ApiException(
                code="INVALID_STATUS_CHANGE",
                message="Cannot change status of cancelled order"
            )
        
        if order.status == OrderStatus.COMPLETED and update_data.status != OrderStatus.COMPLETED:
            raise ApiException(
                code="INVALID_STATUS_CHANGE",
                message="Cannot change status of completed order"
            )
        
        # Обновляем статус
        order.status = update_data.status
        db.commit()
        db.refresh(order)
        
        return ApiResponse(
            success=True,
            data=OrderResponse.model_validate(order).model_dump(mode='json'),
            error=None
        )
    
    except Exception as e:
        db.rollback()
        logger.error(f"Order update failed: {str(e)}")
        raise ApiException(
            code="UPDATE_ORDER_FAILED",
            message="Order update failed"
        )


@router.delete("/{order_id}", response_model=ApiResponse)
async def cancel_order(
    order_id: UUID,
    current_user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Отмена заказа (изменение статуса на 'отменён')"""
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        
        if not order:
            raise ApiException(
                code="ORDER_NOT_FOUND",
                message="Order not found"
            )
        
        # Проверяем права доступа
        if order.user_id != current_user_id:
            raise ApiException(
                code="ACCESS_DENIED",
                message="You don't have permission to cancel this order"
            )
        
        # Проверяем можно ли отменить заказ
        if order.status == OrderStatus.CANCELLED:
            raise ApiException(
                code="ORDER_ALREADY_CANCELLED",
                message="Order is already cancelled"
            )
        
        if order.status == OrderStatus.COMPLETED:
            raise ApiException(
                code="CANNOT_CANCEL_COMPLETED",
                message="Cannot cancel completed order"
            )
        
        # Отменяем заказ
        order.status = OrderStatus.CANCELLED
        db.commit()
        db.refresh(order)
        
        return ApiResponse(
            success=True,
            data=OrderResponse.model_validate(order).model_dump(mode='json'),
            error=None
        )
    
    except Exception as e:
        db.rollback()
        logger.error(f"Order cancel failed: {str(e)}")
        raise ApiException(
            code="CANCEL_ORDER_FAILED",
            message="Cancel order failed"
        )
