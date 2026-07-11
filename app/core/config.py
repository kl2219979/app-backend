"""
app/core/config.py — Configuración
----------------------------------

QUÉ ES
    Lee variables del entorno / archivo `.env` y las expone como `settings`.

POR QUÉ EXISTE
    Evita hardcodear contraseñas, URLs y secretos en el código.
    Cambias `.env` y el comportamiento cambia, sin tocar Python.

PARA LA BD DESACOPLADA
    DATABASE_URL es el "cable" hacia Postgres:
      - En tu PC:        localhost:5432
      - En Docker Compose (servicio api): host `db` (lo pone docker-compose.yml)
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Valores tipados. Si falta una variable, usa el default de abajo."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    APP_NAME: str = "App Backend"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    HOST: str = "0.0.0.0"
    PORT: int = 8000

    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "app_db"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/app_db"

    SECRET_KEY: str = "change-me-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    CORS_ORIGINS: str = "http://localhost:5173"

    @property
    def cors_origins_list(self) -> list[str]:
        """Parte la cadena CORS_ORIGINS en una lista para el middleware."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def is_production(self) -> bool:
        return self.APP_ENV.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    """Lee el entorno una vez por proceso (más eficiente)."""
    return Settings()


settings = get_settings()
