import httpx
import logging
from fastapi import APIRouter, Depends, Query, Path, status
from typing import Optional
from uuid import UUID

from starlette.responses import JSONResponse

from auth import verify_token
from config import settings
from errors import ApiException
from schemas import (
    OrderCreate, OrderUpdate, OrderStatus,
    OrderResponseSuccess, PaginatedOrdersResponseSuccess
)

router = APIRouter(prefix="/orders", tags=["Orders"])
logger = logging.getLogger(__name__)


@router.post(
    "/create",
    response_model=OrderResponseSuccess,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новый заказ",
    description="Создает новый заказ для текущего пользователя. Автоматически вычисляет итоговую сумму. Требует авторизации."
)
async def create_order(
    order_data: OrderCreate,
    token: str = Depends(verify_token)
):
    """Создание нового заказа"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.SERVICE_ORDERS_URL}/v1/orders/",
                json=order_data.model_dump(mode='json'),
                headers={"Authorization": f"Bearer {token}"},
                timeout=30.0
            )
            return JSONResponse(response.json(), status_code=response.status_code)
    except httpx.RequestError as e:
        logger.error(f"Orders service error: {str(e)}")
        raise ApiException("SERVICE_UNAVAILABLE", "Orders service is unavailable")


@router.get(
    "/my",
    response_model=PaginatedOrdersResponseSuccess,
    summary="Получить список заказов текущего пользователя",
    description="Возвращает список заказов текущего пользователя с пагинацией, фильтрацией и сортировкой. Требует авторизации."
)
async def get_user_orders(
    page: int = Query(1, ge=1, description="Номер страницы"),
    page_size: int = Query(10, ge=1, le=100, description="Количество элементов на странице"),
    status_filter: Optional[OrderStatus] = Query(None, description="Фильтр по статусу заказа"),
    sort_by: str = Query("created_at", description="Поле для сортировки (created_at, updated_at, total_amount)"),
    sort_order: str = Query("desc", description="Направление сортировки (asc, desc)"),
    token: str = Depends(verify_token)
):
    """Получение списка заказов текущего пользователя"""
    try:
        params = {
            "page": page,
            "page_size": page_size,
            "sort_by": sort_by,
            "sort_order": sort_order
        }
        if status_filter:
            params["status_filter"] = status_filter.value
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.SERVICE_ORDERS_URL}/v1/orders/",
                params=params,
                headers={"Authorization": f"Bearer {token}"},
                timeout=30.0
            )
            return JSONResponse(response.json(), status_code=response.status_code)
    except httpx.RequestError as e:
        logger.error(f"Orders service error: {str(e)}")
        raise ApiException("SERVICE_UNAVAILABLE", "Orders service is unavailable")


@router.get(
    "/{order_id}",
    response_model=OrderResponseSuccess,
    summary="Получить заказ по ID",
    description="Возвращает информацию о конкретном заказе по его идентификатору. Доступны только собственные заказы. Требует авторизации."
)
async def get_order(
    order_id: UUID = Path(..., description="Идентификатор заказа"),
    token: str = Depends(verify_token)
):
    """Получение заказа по идентификатору"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.SERVICE_ORDERS_URL}/v1/orders/{order_id}",
                headers={"Authorization": f"Bearer {token}"},
                timeout=30.0
            )
            return JSONResponse(response.json(), status_code=response.status_code)
    except httpx.RequestError as e:
        logger.error(f"Orders service error: {str(e)}")
        raise ApiException("SERVICE_UNAVAILABLE", "Orders service is unavailable")


@router.put(
    "/{order_id}/status",
    response_model=OrderResponseSuccess,
    summary="Обновить статус заказа",
    description="Обновляет статус заказа. Доступно только для собственных заказов. Нельзя изменить статус завершенных или отмененных заказов. Требует авторизации."
)
async def update_order_status(
    order_id: UUID = Path(..., description="Идентификатор заказа"),
    update_data: OrderUpdate = ...,
    token: str = Depends(verify_token)
):
    """Обновление статуса заказа"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{settings.SERVICE_ORDERS_URL}/v1/orders/{order_id}/status",
                json=update_data.model_dump(mode='json'),
                headers={"Authorization": f"Bearer {token}"},
                timeout=30.0
            )
            return JSONResponse(response.json(), status_code=response.status_code)
    except httpx.RequestError as e:
        logger.error(f"Orders service error: {str(e)}")
        raise ApiException("SERVICE_UNAVAILABLE", "Orders service is unavailable")


@router.delete(
    "/{order_id}",
    response_model=OrderResponseSuccess,
    summary="Отменить заказ",
    description="Отменяет заказ (изменяет статус на CANCELLED). Доступно только для собственных заказов. Нельзя отменить завершенные заказы. Требует авторизации."
)
async def cancel_order(
    order_id: UUID = Path(..., description="Идентификатор заказа"),
    token: str = Depends(verify_token)
):
    """Отмена заказа"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{settings.SERVICE_ORDERS_URL}/v1/orders/{order_id}",
                headers={"Authorization": f"Bearer {token}"},
                timeout=30.0
            )
            return JSONResponse(response.json(), status_code=response.status_code)
    except httpx.RequestError as e:
        logger.error(f"Orders service error: {str(e)}")
        raise ApiException("SERVICE_UNAVAILABLE", "Orders service is unavailable")
