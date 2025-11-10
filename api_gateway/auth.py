from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

from config import settings

# Bearer токен
security = HTTPBearer()


def decode_access_token(token: str) -> dict:
    """Декодируем и проверяем JWT токен"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
        
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )


async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """Проверяем JWT токен и возвращаем его для дальнейшей передачи"""
    token = credentials.credentials
    decode_access_token(token)  # Просто проверяем валидность
    return token


async def get_token_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
) -> Optional[str]:
    """Получаем токен, если он есть (для незащищенных эндпоинтов)"""
    if credentials:
        return credentials.credentials
    return None
