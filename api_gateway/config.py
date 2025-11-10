from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения из .env"""
    model_config = SettingsConfigDict(
        env_file="../.env",
        extra="ignore",
    )
    
    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Настройки текущего сервиса
    APP_HOST: str = Field(validation_alias="API_GATEWAY_HOST", default="0.0.0.0")
    APP_PORT: int = Field(validation_alias="API_GATEWAY_PORT", default=8000)
    
    # URLs внутренних сервисов
    SERVICE_USERS_URL: str = "http://localhost:8001"
    SERVICE_ORDERS_URL: str = "http://localhost:8002"


settings = Settings()  # type: ignore
