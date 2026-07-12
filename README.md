# App Backend

API REST del proyecto, construida con **FastAPI**, **SQLAlchemy**, **Alembic** y **PostgreSQL**.

Arquitectura: la base de datos vive desacoplada en su propio contenedor; el backend es dueño del esquema (Alembic) y de la lógica de datos (services / repositories).

> **Empieza aquí si quieres entender el proyecto:**  
> lee [`docs/COMO_FUNCIONA.md`](docs/COMO_FUNCIONA.md) — explica **qué hace cada pieza y por qué existe**, paso a paso.  
> Mapa de tablas y FK: [`docs/MODELOS.md`](docs/MODELOS.md).  
> Auth (hash + JWT): [`docs/SEGURIDAD.md`](docs/SEGURIDAD.md).  
> Repositories: [`docs/REPOSITORIOS.md`](docs/REPOSITORIOS.md).  
> Tests (patrón AAA): [`docs/TESTING.md`](docs/TESTING.md).  
> Hoja de ruta (pasos 1–7): [`docs/HOJA_RUTA.md`](docs/HOJA_RUTA.md).

## Equipo


| Rol           | Responsable                                |
| ------------- | ------------------------------------------ |
| Scrum Master  | —                                          |
| Product Owner | —                                          |
| Frontend (×2) | Rama propia (repo frontend)                |
| Backend (×2)  | Andrés → `dev_andres`, Kevin → `dev_kevin` |
| QA            | Kevin                                      |


## Arquitectura de datos

```
┌─────────────────────┐         puerto 5432          ┌──────────────────────────┐
│  Contenedor Postgres │ ◄─────────────────────────── │  Backend (FastAPI)       │
│  Solo motor + volumen│      DATABASE_URL            │  • Alembic → esquema     │
│  Sin lógica de negocio│                             │  • SQLAlchemy → modelos  │
└─────────────────────┘                             │  • Services → reglas     │
                                                    │  • Repositories → CRUD   │
                                                    └──────────────────────────┘
```


| Pieza             | Responsabilidad                                                          |
| ----------------- | ------------------------------------------------------------------------ |
| Contenedor `db`   | PostgreSQL listo en un puerto. Sin scripts de negocio ni DDL de dominio. |
| Alembic           | Crea y modifica el **esquema** (`alembic upgrade head`).                 |
| SQLAlchemy models | Mapean tablas ↔ Python.                                                  |
| Repositories      | Cómo se lee/escribe.                                                     |
| Services          | Qué se permite insertar/modificar (lógica de negocio).                   |


El frontend **nunca** habla con Postgres; solo con la API.

## Estructura del repositorio

```
app-backend/
├── app/
│   ├── main.py              # Punto de entrada FastAPI
│   ├── api/                 # Capa de presentación (rutas HTTP)
│   │   ├── deps.py
│   │   └── v1/
│   │       ├── router.py
│   │       └── endpoints/
│   ├── core/                # Configuración y seguridad
│   ├── db/                  # Conexión y base ORM
│   ├── models/              # Modelos SQLAlchemy (entidades)
│   ├── schemas/             # Esquemas Pydantic (DTOs)
│   ├── services/            # Lógica de negocio
│   └── repositories/        # Acceso a datos
├── alembic/                 # Migraciones (fuente de verdad del esquema)
│   └── versions/
├── scripts/
│   ├── setup.sh             # venv + deps
│   ├── migrate.sh           # espera BD + alembic upgrade head
│   ├── wait_for_db.py
│   └── entrypoint.sh        # usado por el contenedor api
├── tests/
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
git clone <url-del-repo>
cd app-backend
cp .env.example .env
git checkout dev_kevin   # o dev_andres
```

## Requisitos

- Python 3.11+
- Docker (para PostgreSQL)
- pip / venv

## Inicio rápido

### Opción A: BD desacoplada + API local (recomendado en desarrollo)

```bash
chmod +x scripts/setup.sh scripts/migrate.sh
./scripts/setup.sh
source .venv/bin/activate

# 1) Solo la base de datos
docker compose up db -d

# 2) Aplicar esquema (Alembic)
./scripts/migrate.sh



# 3) API
uvicorn app.main:app --reload
```

API: [http://localhost:8000](http://localhost:8000)  
Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

### Opción B: Stack completo con Docker

```bash
cp .env.example .env
docker compose up --build
```

El contenedor `api` espera a Postgres, corre `alembic upgrade head` y luego arranca Uvicorn.

## Migraciones (Alembic)

Cuando agregues o cambies modelos en `app/models/`:

```bash
# Generar revisión a partir de los modelos
alembic revision --autogenerate -m "descripcion_del_cambio"

# Revisar el archivo en alembic/versions/ y luego aplicar
./scripts/migrate.sh
# o: alembic upgrade head
```

Importa el modelo nuevo en `app/models/__init__.py` para que Alembic lo detecte.

## Comandos útiles

```bash
# Solo Postgres
docker compose up db -d

# Migraciones
./scripts/migrate.sh

# Seeds (categorías iniciales, idempotente)
python scripts/seed.py

# Tests
pytest -q                 # suite diaria (unit + API smoke)
pytest -m unit -q         # solo unitarios
pytest -m integration -q  # smokes API
# Postgres opt-in: RUN_INTEGRATION=1 TEST_DATABASE_URL=... pytest tests/integration
# E2E opt-in:     RUN_E2E=1 E2E_BASE_URL=http://localhost:8000 pytest -m e2e

# Linter
ruff check app tests
```

CI en GitHub Actions (`.github/workflows/ci.yml`): Ruff + Pytest en cada push/PR a `main`/`dev`.

Guía completa (pirámide, AAA, markers, política PR): [`docs/TESTING.md`](docs/TESTING.md).

### Listado de transacciones (paginado)

```http
GET /api/v1/transactions?limit=20&offset=0&account_id=1&tipo=gasto&date_from=2026-01-01
Authorization: Bearer <token>
```

Respuesta:

```json
{ "items": [ ... ], "total": 42, "limit": 20, "offset": 0 }
```

`tipo`: `gasto` (resta saldo) o `ingreso` (suma saldo).

## Variables de entorno

Copia `.env.example` a `.env` y ajusta los valores. **No subas `.env` al repositorio.**


| Variable       | Descripción                                                      |
| -------------- | ---------------------------------------------------------------- |
| `POSTGRES_*`   | Piezas de conexión a Postgres (la URL se arma sola en `config.py`) |
| `SECRET_KEY`   | Clave para tokens JWT                                            |
| `CORS_ORIGINS` | Orígenes permitidos del frontend (Vite: `http://localhost:5173`) |


## QA

Kevin es responsable de QA. Las pruebas viven en `tests/` y siguen la pirámide:
**muchos unitarios**, **algunos de integración**, **pocos E2E** (ver [`docs/TESTING.md`](docs/TESTING.md)).

Antes de cada PR hacia `dev`:

```bash
pytest -q
```

Checklist mínimo:

- Nuevas reglas de negocio → `tests/services/`
- SQL no trivial → `tests/repositories/`
- Contrato HTTP nuevo → un smoke en `tests/api/` (no duplicar toda la lógica)

## Crear el repositorio en GitHub

Si aún no existe el remoto:

```bash
# En GitHub: New repository → app-backend (sin README ni .gitignore)

git remote add origin https://github.com/<tu-usuario>/app-backend.git
git push -u origin main
git push -u origin dev dev_andres dev_kevin
```

