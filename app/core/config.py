"""
app/core/config.py — Configuración central de la aplicación
============================================================

QUÉ ES ESTE ARCHIVO
-------------------
Lee valores desde:
  1) variables de entorno del sistema, y/o
  2) el archivo `.env` en la raíz del proyecto,

y los expone como un objeto tipado llamado `settings`.

El resto del código NO debería hardcodear URLs, secretos ni puertos:
debe usar `from app.core.config import settings`.


PARA QUÉ SIRVE (en la práctica)
-------------------------------
- Cambiar la BD, el puerto o el CORS sin tocar la lógica de negocio.
- Que cada compañero tenga su propio `.env` (ej. puerto 5432 vs 5433).
- Que Docker Compose pueda sobrescribir HOST/URL al correr el servicio `api`.


CÓMO SE USA
-----------
    from app.core.config import settings

    settings.DATABASE_URL
    settings.cors_origins_list
    settings.is_production


NOTAS / MEJORAS A FUTURO
------------------------
1. Evitar desfase POSTGRES_* vs DATABASE_URL:
   Hoy existen por separado. Si cambias POSTGRES_PORT y olvidas DATABASE_URL,
   Alembic/API apuntan mal. Mejora: construir DATABASE_URL desde POSTGRES_* 
   (property o validator) y dejar de duplicarla en `.env`, o validar que coincidan.

2. Validar secretos en producción:
   Si APP_ENV=production y SECRET_KEY sigue en "change-me...", fallar al arrancar.

3. HOST / PORT:
   Hoy Uvicorn suele tomar host/puerto del CLI o de docker-compose, no de aquí.
   O usarlos en un script de arranque, o quitarlos hasta que hagan falta.

4. Tests:
   get_settings usa lru_cache. En tests que cambien env vars, llamar:
       get_settings.cache_clear()
   antes de crear Settings de nuevo.

5. CORS tipado:
   Se podría parsear a list[str] con un field_validator de Pydantic
   en lugar de una property manual (mismo resultado, un poco más “oficial”).

6. No subir complejidad de más:
   No hace falta varios Settings classes, YAML, ni consul/vault en este tamaño
   de proyecto académico/equipo pequeño.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Contenedor tipado de toda la configuración.

    BaseSettings (Pydantic):
      - Declara campos con tipo (str, int, bool, ...).
      - Busca automáticamente variables de entorno con el MISMO nombre
        que el campo (ej. campo DATABASE_URL ← env DATABASE_URL).
      - Si no encuentra la variable, usa el default que pones a la derecha de `=`.
    """

    # ------------------------------------------------------------------
    # model_config — cómo Pydantic carga el entorno
    # ------------------------------------------------------------------
    # SettingsConfigDict: diccionario de opciones de Pydantic Settings.
    #
    # env_file=".env"
    #   Para qué: leer también el archivo .env de la raíz.
    #   Por qué: en desarrollo no quieres exportar 15 variables a mano;
    #   copias .env.example → .env y listo.
    #
    # env_file_encoding="utf-8"
    #   Para qué: interpretar bien tildes/caracteres del .env.
    #   Por qué: evita errores raros de encoding en distintos SO.
    #
    # case_sensitive=True
    #   Para qué: DATABASE_URL y database_url NO son lo mismo.
    #   Por qué: forzamos un convenio claro (MAYÚSCULAS) igual que en .env.example.
    #
    # extra="ignore"
    #   Para qué: si el .env tiene una clave que no está en esta clase, se ignora.
    #   Por qué: Docker u otras herramientas a veces inyectan variables de más;
    #   no queremos que la app explote por eso.
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # ------------------------------------------------------------------
    # Aplicación
    # ------------------------------------------------------------------
    # APP_NAME: título que ve FastAPI (docs, OpenAPI).
    APP_NAME: str = "App Backend"

    # APP_ENV: "development" | "production" | etc.
    # Para qué: decidir comportamientos (logs, docs, validaciones).
    # Por qué: el mismo código corre en local y en servidor con distinto modo.
    APP_ENV: str = "development"

    # DEBUG: si True, FastAPI muestra más detalle y suele exponer /docs.
    # Por qué: en producción no quieres Swagger público ni stack traces abiertos.
    DEBUG: bool = True

    # API_V1_PREFIX: prefijo de todas las rutas v1 (ej. /api/v1/users).
    # Para qué: versionar la API sin romper clientes viejos el día que exista v2.
    API_V1_PREFIX: str = "/api/v1"

    # ------------------------------------------------------------------
    # Servidor HTTP (referencia; Uvicorn a menudo lo toma del CLI/Docker)
    # ------------------------------------------------------------------
    # HOST: interfaz de escucha. 0.0.0.0 = acepta conexiones de fuera de localhost.
    # Por qué en Docker/API: el contenedor debe ser alcanzable desde el host.
    HOST: str = "0.0.0.0"

    # PORT: puerto HTTP de la API (por defecto 8000).
    PORT: int = 8000

    # ------------------------------------------------------------------
    # PostgreSQL (BD desacoplada)
    # ------------------------------------------------------------------
    # Estas piezas las usa sobre todo Docker Compose para crear el contenedor
    # `db` (usuario, clave, nombre de base, puerto publicado en tu PC).
    #
    # POSTGRES_USER / POSTGRES_PASSWORD / POSTGRES_DB:
    #   credenciales y nombre de la base dentro de Postgres.
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "app_db"

    # POSTGRES_HOST:
    #   - localhost  → API o Alembic corriendo en tu PC, BD en Docker publicada.
    #   - db         → API dentro de Compose (nombre del servicio).
    POSTGRES_HOST: str = "localhost"

    # POSTGRES_PORT: puerto en el HOST que mapea a 5432 del contenedor.
    # Si 5432 está ocupado en tu PC, en .env pones 5433 (como te pasó a ti).
    POSTGRES_PORT: int = 5432

    # DATABASE_URL: cadena completa que usan SQLAlchemy y Alembic.
    # Formato: postgresql://USER:PASSWORD@HOST:PORT/DBNAME
    # Para qué: un solo string de conexión para el motor ORM.
    # Por qué existe además de POSTGRES_*: la app habla por URL; Compose
    # necesita las piezas sueltas para el contenedor oficial de Postgres.
    # CUIDADO: deben coincidir con POSTGRES_* (ver mejoras a futuro arriba).
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/app_db"

    # ------------------------------------------------------------------
    # Seguridad
    # ------------------------------------------------------------------
    # SECRET_KEY: secreto para firmar JWT u otras cosas criptográficas.
    # Por qué no hardcodear uno “de verdad” en el código: se filtraría en Git.
    # En producción DEBE ser largo, aleatorio y distinto por entorno.
    SECRET_KEY: str = "change-me-in-production"

    # ACCESS_TOKEN_EXPIRE_MINUTES: vida útil del access token (cuando implementes auth).
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # ------------------------------------------------------------------
    # CORS (Cross-Origin Resource Sharing)
    # ------------------------------------------------------------------
    # Lista de orígenes del frontend permitidos para llamar a la API desde el navegador.
    # En .env van separados por coma, ej:
    #   CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
    # Por qué: el navegador bloquea llamadas cross-origin si no lo permites.
    CORS_ORIGINS: str = "http://localhost:5173"

    # ------------------------------------------------------------------
    # Propiedades derivadas (no vienen del .env; se calculan)
    # ------------------------------------------------------------------
    @property
    def cors_origins_list(self) -> list[str]:
        """
        Convierte CORS_ORIGINS (string) en lista para FastAPI CORSMiddleware.

        Para qué: el middleware espera list[str], no un string con comas.
        Por qué property: no duplicar en .env una lista “rara”; el humano
        escribe texto simple y aquí lo partimos.
        """
        return [
            origin.strip()
            for origin in self.CORS_ORIGINS.split(",")
            if origin.strip()
        ]

    @property
    def is_production(self) -> bool:
        """
        Atajo booleano: ¿estamos en producción?

        Para qué: if settings.is_production: ...
        Por qué: no repetir .lower() == "production" por todo el código.
        """
        return self.APP_ENV.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    """
    Crea (y memoriza) una única instancia de Settings por proceso.

    lru_cache (functools):
      - La primera llamada ejecuta Settings() y guarda el resultado.
      - Las siguientes devoluciones reutilizan ese mismo objeto.
      - Para qué: no releer el .env en cada request.
      - Por qué: más eficiente y configuración estable durante el proceso.

    En tests que muten el entorno: get_settings.cache_clear()
    """
    return Settings()


# Instancia lista para importar en cualquier módulo:
#   from app.core.config import settings
settings = get_settings()
