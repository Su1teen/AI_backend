from typing import Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from urllib.parse import quote_plus

class Settings(BaseSettings):
    # HTTP Server Configuration
    PORT: int = Field(7000, description="HTTP server port")
    HOST: str = Field("0.0.0.0", description="HTTP server host")
    
    # Database Configuration
    DB_USER: str = Field(..., description="PostgreSQL username")
    DB_PASSWORD: str = Field(..., description="PostgreSQL password")
    DB_HOST: str = Field("localhost", description="PostgreSQL host")
    DB_PORT: int = Field(5432, description="PostgreSQL port")
    DB_NAME: str = Field(..., description="PostgreSQL database name")
    
    @property
    def DATABASE_URL(self) -> str:
        """Constructs the database connection URL."""
        return (
            f"postgresql://{quote_plus(self.DB_USER)}:"
            f"{quote_plus(self.DB_PASSWORD)}@"
            f"{self.DB_HOST}:"
            f"{self.DB_PORT}/"
            f"{quote_plus(self.DB_NAME)}"
        )

    # Security Configuration
    JWT_ALGORITHM: str = Field("HS256", description="JWT signing algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(60, description="Token expiration in minutes")

    # External Services
    OPENAI_API_KEY: str = Field(..., description="OpenAI API key")
    
    # Email Configuration (Optional)
    EMAIL_HOST: Optional[str] = Field(None, description="SMTP server host")
    EMAIL_PORT: Optional[int] = Field(None, description="SMTP server port")
    EMAIL_USER: Optional[str] = Field(None, description="SMTP username")
    EMAIL_PASSWORD: Optional[str] = Field(None, description="SMTP password")
    
    # Telegram Configuration (Optional)
    TELEGRAM_BOT_TOKEN: Optional[str] = Field(None, description="Telegram bot token")

    # Frontend Configuration
    FRONTEND_URL: str = Field("http://localhost:3000", description="Frontend application URL")
    
    # Development Flags
    DEBUG: bool = Field(False, description="Enable debug mode")

    # Pydantic Configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
        env_prefix="APP_",  # Optional: prefix all env vars with APP_
        env_nested_delimiter="__"  # Optional: for nested configs
    )

    @field_validator("PORT", "DB_PORT", "EMAIL_PORT", "ACCESS_TOKEN_EXPIRE_MINUTES", mode="before")
    @classmethod
    def validate_positive_integers(cls, v):
        """Validate that certain fields are positive integers."""
        try:
            v_int = int(v)
            if v_int <= 0:
                raise ValueError("must be positive")
            return v_int
        except (TypeError, ValueError) as e:
            raise ValueError(f"Invalid value: {v}. Must be a positive integer.") from e

    @field_validator("FRONTEND_URL", mode="before")
    @classmethod
    def validate_frontend_url(cls, v):
        """Ensure FRONTEND_URL ends without a trailing slash."""
        if v and v.endswith('/'):
            return v[:-1]
        return v

# Initialize settings (will raise ValidationError if required fields are missing)
try:
    settings = Settings()
except Exception as e:
    print(f"Failed to load settings: {e}")
    raise

# Optional: Verify settings on startup
if settings.DEBUG:
    print("Running in DEBUG mode")
    print(f"Database URL: {settings.DATABASE_URL}")