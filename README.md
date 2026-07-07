# App Backend

API REST del proyecto, construida con **FastAPI** y **PostgreSQL**. Arquitectura cliente-servidor: el frontend (SPA con Vite) consume esta API.

## Equipo

| Rol | Responsable |
|-----|-------------|
| Scrum Master | — |
| Product Owner | — |
| Frontend (×2) | Rama propia (repo frontend) |
| Backend (×2) | Andrés → `dev_andres`, Kevin → `dev_kevin` |
| QA | Kevin |

## Estructura del repositorio

```
app-backend/
├── app/
│   ├── main.py              # Punto de entrada FastAPI
│   ├── api/                 # Capa de presentación (rutas HTTP)
│   │   ├── deps.py          # Dependencias inyectables
│   │   └── v1/
│   │       ├── router.py
│   │       └── endpoints/
│   ├── core/                # Configuración y seguridad
│   ├── db/                  # Conexión y base ORM
│   ├── models/              # Modelos SQLAlchemy (entidades)
│   ├── schemas/             # Esquemas Pydantic (DTOs)
│   ├── services/            # Lógica de negocio
│   └── repositories/        # Acceso a datos (patrón repositorio)
├── tests/                   # Pruebas automatizadas
├── alembic/                 # Migraciones de base de datos
├── scripts/                 # Scripts de utilidad
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

### Capas (clean architecture simplificada)

1. **Endpoints** (`api/`) — Reciben HTTP, validan entrada, delegan a servicios.
2. **Services** (`services/`) — Reglas de negocio, orquestan repositorios.
3. **Repositories** (`repositories/`) — Consultas y persistencia en PostgreSQL.
4. **Models / Schemas** — Entidades de BD y contratos de API separados.

## Ramas Git

```
main          → Producción (solo merges desde dev, vía PR)
  └── dev     → Integración del backend
        ├── dev_andres
        └── dev_kevin
```

### Flujo de trabajo

1. Cada desarrollador trabaja en su rama personal (`dev_andres` / `dev_kevin`).
2. Se hace **Pull Request** hacia `dev` para integrar cambios.
3. Tras QA en `dev`, se promueve a `main` con otro PR.
4. **Nunca** hacer push directo a `main`.

```bash
# Clonar y configurar
git clone <url-del-repo>
cd app-backend
cp .env.example .env

# Cambiar a tu rama de desarrollo
git checkout dev_kevin   # o dev_andres
```

## Requisitos

- Python 3.11+
- PostgreSQL 16+ (o Docker)
- pip / venv

## Inicio rápido

### Opción A: Docker (recomendado)

```bash
cp .env.example .env
docker compose up --build
```

API disponible en: http://localhost:8000  
Documentación: http://localhost:8000/docs

### Opción B: Local

```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
source .venv/bin/activate

# Levantar solo PostgreSQL con Docker
docker compose up db -d

# Iniciar servidor
uvicorn app.main:app --reload
```

## Comandos útiles

```bash
# Tests
pytest

# Linter
ruff check app tests

# Migraciones
alembic revision --autogenerate -m "descripcion"
alembic upgrade head
```

## Variables de entorno

Copia `.env.example` a `.env` y ajusta los valores. **No subas `.env` al repositorio.**

| Variable | Descripción |
|----------|-------------|
| `DATABASE_URL` | URL de conexión PostgreSQL |
| `SECRET_KEY` | Clave para tokens JWT |
| `CORS_ORIGINS` | Orígenes permitidos del frontend (Vite: `http://localhost:5173`) |

## QA

Kevin es responsable de QA. Las pruebas viven en `tests/`. Ejecutar `pytest` antes de cada PR hacia `dev`.

## Crear el repositorio en GitHub

Si aún no existe el remoto:

```bash
# En GitHub: New repository → app-backend (sin README ni .gitignore)

git remote add origin https://github.com/<tu-usuario>/app-backend.git
git push -u origin main
git push -u origin dev dev_andres dev_kevin
```
