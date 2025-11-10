from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения из .env"""
    model_config = SettingsConfigDict(
        env_file="../.env",
        extra="ignore",
    )
    
    # База данных
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    
    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Настройки текущего сервиса
    APP_HOST: str = Field(validation_alias="SERVICE_ORDERS_HOST", default="0.0.0.0")
    APP_PORT: int = Field(validation_alias="SERVICE_ORDERS_PORT", default=8002)
    
    @property
    def DATABASE_URL(self) -> str:  # noqa
        """Собираем и возвращаем URL базы данных"""
        return (
            f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


settings = Settings()  # type: ignore
