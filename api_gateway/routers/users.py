import httpx
import logging
from fastapi import APIRouter, Depends, Query, status
from typing import Optional

from starlette.responses import JSONResponse

from auth import verify_token, get_token_optional
from config import settings
from errors import ApiException
from schemas import (
    UserRegister, UserLogin, UserUpdate,
    UserResponseSuccess, TokenResponseSuccess, PaginatedUsersResponseSuccess
)

router = APIRouter(prefix="/users", tags=["Users"])
logger = logging.getLogger(__name__)


@router.post(
    "/register",
    response_model=UserResponseSuccess,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация нового пользователя",
    description="Создает нового пользователя в системе. Не требует авторизации."
)
async def register(user_data: UserRegister):
    """Регистрация нового пользователя"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.SERVICE_USERS_URL}/v1/auth/register",
                json=user_data.model_dump(mode='json'),
                timeout=30.0
            )
            return JSONResponse(response.json(), status_code=response.status_code)
    except httpx.RequestError as e:
        logger.error(f"Users service error: {str(e)}")
        raise ApiException("SERVICE_UNAVAILABLE", "Users service is unavailable")


@router.post(
    "/login",
    response_model=TokenResponseSuccess,
    summary="Авторизация пользователя",
    description="Авторизует пользователя и возвращает JWT токен. Не требует авторизации."
)
async def login(credentials: UserLogin):
    """Авторизация пользователя"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.SERVICE_USERS_URL}/v1/auth/login",
                json=credentials.model_dump(mode='json'),
                timeout=30.0
            )
            return JSONResponse(response.json(), status_code=response.status_code)
    except httpx.RequestError as e:
        logger.error(f"Users service error: {str(e)}")
        raise ApiException("SERVICE_UNAVAILABLE", "Users service is unavailable")


@router.get(
    "/me",
    response_model=UserResponseSuccess,
    summary="Получить профиль текущего пользователя",
    description="Возвращает информацию о текущем авторизованном пользователе. Требует авторизации."
)
async def get_current_user_profile(token: str = Depends(verify_token)):
    """Получение профиля текущего пользователя"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.SERVICE_USERS_URL}/v1/users/me",
                headers={"Authorization": f"Bearer {token}"},
                timeout=30.0
            )
            return JSONResponse(response.json(), status_code=response.status_code)
    except httpx.RequestError as e:
        logger.error(f"Users service error: {str(e)}")
        raise ApiException("SERVICE_UNAVAILABLE", "Users service is unavailable")


@router.put(
    "/me",
    response_model=UserResponseSuccess,
    summary="Обновить профиль текущего пользователя",
    description="Обновляет информацию о текущем авторизованном пользователе. Требует авторизации."
)
async def update_current_user_profile(
    update_data: UserUpdate,
    token: str = Depends(verify_token)
):
    """Обновление профиля текущего пользователя"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{settings.SERVICE_USERS_URL}/v1/users/me",
                json=update_data.model_dump(mode='json', exclude_none=True),
                headers={"Authorization": f"Bearer {token}"},
                timeout=30.0
            )
            return JSONResponse(response.json(), status_code=response.status_code)
    except httpx.RequestError as e:
        logger.error(f"Users service error: {str(e)}")
        raise ApiException("SERVICE_UNAVAILABLE", "Users service is unavailable")


@router.get(
    "/all",
    response_model=PaginatedUsersResponseSuccess,
    summary="Получить список всех пользователей",
    description="Возвращает список всех пользователей с пагинацией. Требует авторизации и права администратора."
)
async def get_all_users(
    page: int = Query(1, ge=1, description="Номер страницы"),
    page_size: int = Query(10, ge=1, le=100, description="Количество элементов на странице"),
    search: Optional[str] = Query(None, description="Поиск по имени или email"),
    role: Optional[str] = Query(None, description="Фильтр по роли"),
    token: str = Depends(verify_token)
):
    """Получение списка всех пользователей (только для администраторов)"""
    try:
        params = {"page": page, "page_size": page_size}
        if search:
            params["search"] = search
        if role:
            params["role"] = role
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.SERVICE_USERS_URL}/v1/users/",
                params=params,
                headers={"Authorization": f"Bearer {token}"},
                timeout=30.0
            )
            return JSONResponse(response.json(), status_code=response.status_code)
    except httpx.RequestError as e:
        logger.error(f"Users service error: {str(e)}")
        raise ApiException("SERVICE_UNAVAILABLE", "Users service is unavailable")
