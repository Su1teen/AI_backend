# backend/config.py

from typing import Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from urllib.parse import quote_plus
class Settings(BaseSettings):
    # HTTP
    PORT: int = Field(7000, description="Порт HTTP-сервера")

    # PostgreSQL
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql://{quote_plus(self.DB_USER)}:"
            f"{quote_plus(self.DB_PASSWORD)}@"
            f"{self.DB_HOST}:"
            f"{self.DB_PORT}/"
            f"{quote_plus(self.DB_NAME)}"
        )

    # OpenAI
    OPENAI_API_KEY: str

    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Email (SMTP)
    EMAIL_HOST: str
    EMAIL_PORT: int
    EMAIL_USER: str
    EMAIL_PASSWORD: str

    # Telegram (опционально)
    TELEGRAM_BOT_TOKEN: Optional[str] = None

    # Frontend URL
    FRONTEND_URL: str

    # Конфигурация Pydantic v2
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore" 
    )

    # Валидация, чтобы указанные поля были положительными
    @field_validator("PORT", "DB_PORT", "EMAIL_PORT", "ACCESS_TOKEN_EXPIRE_MINUTES", mode="before")
    @classmethod
    def _validate_positive(cls, v):
        v = int(v)
        if v <= 0:
            raise ValueError("must be positive")
        return v

# Инстанс настроек
settings = Settings()
