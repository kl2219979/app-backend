"""
app/core/config.py — Configuración central de la aplicación
============================================================

QUÉ ES
------
Lee variables de entorno y/o `.env`, y las expone como `settings` tipado.
El resto del código usa `from app.core.config import settings` (sin hardcodear).

CÓMO SE USA
-----------
    settings.DATABASE_URL       # siempre coherente con POSTGRES_*
    settings.cors_origins_list
    settings.is_production

REFACTOR (fuente de verdad de la BD)
------------------------------------
- Configuras POSTGRES_USER / PASSWORD / DB / HOST / PORT.
- DATABASE_URL se ARMA sola a partir de esas piezas.
- Si defines DATABASE_URL en el entorno, esa gana (override explícito).

Docker Compose:
  - En el host: POSTGRES_PORT puede ser 5433 (puerto publicado).
  - En el servicio `api`: se fuerza POSTGRES_HOST=db y POSTGRES_PORT=5432
    (puerto interno del contenedor Postgres).

Tests: si cambias env vars, llama get_settings.cache_clear().
"""

from __future__ import annotations

from functools import lru_cache
from typing import Self
from urllib.parse import quote_plus

from pydantic import Field, computed_field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Valores inseguros que no se permiten si APP_ENV=production.
_INSECURE_SECRET_PREFIXES = ("change-me", "secret", "changeme")


class Settings(BaseSettings):
    """
    Contenedor tipado de configuración (Pydantic BaseSettings).

    Cada campo se rellena desde una variable de entorno del mismo nombre,
    o desde `.env`, o con el default de la derecha.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # --- Aplicación ---
    APP_NAME: str = "App Backend"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    # --- HTTP (referencia; Uvicorn suele tomar host/port del CLI o Compose) ---
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # --- PostgreSQL (piezas = fuente de verdad) ---
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "app_db"
    # localhost = API en el host; db = API dentro de Compose.
    POSTGRES_HOST: str = "localhost"
    # Puerto al que se conecta el cliente (5433 en host si 5432 está ocupado;
    # 5432 dentro de la red Docker hacia el servicio db).
    POSTGRES_PORT: int = 5432

    # Override opcional desde env DATABASE_URL (si viene, tiene prioridad).
    database_url_override: str | None = Field(
        default=None,
        validation_alias="DATABASE_URL",
        description="Si se define, reemplaza la URL armada con POSTGRES_*.",
    )

    # --- Seguridad ---
    SECRET_KEY: str = "change-me-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # --- CORS: orígenes separados por coma en el .env ---
    CORS_ORIGINS: str = "http://localhost:5173"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def DATABASE_URL(self) -> str:
        """
        URL de conexión para SQLAlchemy / Alembic.

        Prioridad:
          1) DATABASE_URL en el entorno (override)
          2) Armada desde POSTGRES_*
        """
        if self.database_url_override:
            return self.database_url_override

        user = quote_plus(self.POSTGRES_USER)
        password = quote_plus(self.POSTGRES_PASSWORD)
        return (
            f"postgresql://{user}:{password}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def is_production(self) -> bool:
        """True cuando APP_ENV indica producción."""
        return self.APP_ENV.lower() == "production"

    @property
    def cors_origins_list(self) -> list[str]:
        """Lista de orígenes para CORSMiddleware (parte CORS_ORIGINS)."""
        return [
            origin.strip()
            for origin in self.CORS_ORIGINS.split(",")
            if origin.strip()
        ]

    @field_validator("POSTGRES_PORT")
    @classmethod
    def port_must_be_valid(cls, value: int) -> int:
        """El puerto debe estar en el rango TCP válido."""
        if not 1 <= value <= 65535:
            raise ValueError("POSTGRES_PORT must be between 1 and 65535")
        return value

    @model_validator(mode="after")
    def reject_insecure_secret_in_production(self) -> Self:
        """En producción, obliga a un SECRET_KEY real (no el default de plantilla)."""
        if not self.is_production:
            return self

        key = self.SECRET_KEY.strip().lower()
        if len(self.SECRET_KEY) < 32 or any(
            key.startswith(prefix) for prefix in _INSECURE_SECRET_PREFIXES
        ):
            raise ValueError(
                "SECRET_KEY must be a strong random value when APP_ENV=production "
                "(min 32 chars, not a placeholder like 'change-me-...')."
            )
        return self


@lru_cache
def get_settings() -> Settings:
    """
    Una sola instancia de Settings por proceso (lru_cache).

    En tests que muten el entorno:
        get_settings.cache_clear()
    """
    return Settings()


settings = get_settings()
