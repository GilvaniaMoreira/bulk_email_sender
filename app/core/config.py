"""Configurações da aplicação usando Pydantic Settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Configurações da aplicação carregadas de variáveis de ambiente."""

    # FastAPI
    APP_NAME: str = "Bulk Email Sender"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Redis
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    # Celery
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None

    # SMTP
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASS: str = ""
    SMTP_USE_TLS: bool = True
    SMTP_FROM_EMAIL: Optional[str] = None

    # Flower
    FLOWER_PORT: int = 5555

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )

    def __init__(self, **kwargs):
        """Inicializa as configurações e define URLs do Celery se não fornecidas."""
        super().__init__(**kwargs)

        # Define URLs do Celery baseadas no Redis se não fornecidas
        if not self.CELERY_BROKER_URL:
            self.CELERY_BROKER_URL = (
                f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
            )
        if not self.CELERY_RESULT_BACKEND:
            self.CELERY_RESULT_BACKEND = (
                f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
            )

        # Define email remetente padrão se não fornecido
        if not self.SMTP_FROM_EMAIL:
            self.SMTP_FROM_EMAIL = self.SMTP_USER


@lru_cache()
def get_settings() -> Settings:
    """Retorna instância singleton das configurações."""
    return Settings()


settings = get_settings()
