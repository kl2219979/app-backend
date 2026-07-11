# Cómo funciona este backend (guía paso a paso)

Esta guía explica **qué es cada cosa** y **por qué existe**.
Léela en orden la primera vez.

---

## 1. La idea general (el “por qué” de todo)

Imagina tres piezas separadas:

```
[ Frontend Vite ]  --HTTP-->  [ API FastAPI ]  --SQL-->  [ PostgreSQL ]
     (pantallas)               (lógica)                   (datos guardados)
```

- El **frontend** solo habla con la API (nunca con la base de datos).
- La **API** decide qué se puede hacer (crear usuario, listar, etc.).
- **PostgreSQL** solo guarda y entrega datos. No sabe de reglas de negocio.

Por eso decimos que la base está **desacoplada**:
vive en su propio contenedor Docker, escucha en un puerto, y el resto se conecta a ella.
Si mañana cambias el frontend o la API, la BD sigue siendo la misma “caja” de datos.

---

## 2. ¿Qué problema resuelve cada herramienta?

| Herramienta | Pregunta que responde | Analogía |
|-------------|----------------------|----------|
| **Docker / Postgres** | ¿Dónde corre la base y cómo la enciendo? | Una nevera: guarda cosas, no cocina. |
| **Alembic** | ¿Cómo se crean/cambian las *tablas*? | Los planos de la cocina (dónde van los estantes). |
| **SQLAlchemy (models)** | ¿Cómo represento una tabla en Python? | Etiquetas en español para cada estante. |
| **Repositories** | ¿Cómo leo/escribo filas en la BD? | Abrir la nevera y sacar/guardar un plato. |
| **Services** | ¿Está *permitido* hacer esto? | El cocinero decide la receta. |
| **Endpoints (API)** | ¿Qué URL llama el frontend? | La ventanilla que atiende pedidos. |
| **Schemas (Pydantic)** | ¿El JSON que llega es válido? | Revisar que el pedido tenga todos los campos. |

Regla mental:

- **Alembic** = estructura (columnas, tablas) → “cómo es la nevera por dentro”.
- **Services** = lógica → “qué platos se pueden cocinar”.
- **Repositories** = acceso técnico → “cómo se guarda el plato”.

---

## 3. El flujo cuando enciendes todo

### Opción A — Desarrollo (recomendada para aprender)

```bash
./scripts/setup.sh              # 1) Prepara Python
docker compose up db -d         # 2) Enciende SOLO la base
./scripts/migrate.sh            # 3) Crea/actualiza las tablas
uvicorn app.main:app --reload   # 4) Enciende la API
```

Qué pasa en cada paso:

1. **setup.sh**  
   - **Qué:** crea un entorno virtual (`.venv`), instala librerías, copia `.env`.  
   - **Por qué:** para no ensuciar el Python del sistema y tener las mismas dependencias que el equipo.

2. **docker compose up db -d**  
   - **Qué:** levanta un contenedor con PostgreSQL en el puerto 5432.  
   - **Por qué:** así todos usan la misma versión de Postgres sin instalarla a mano.  
   - **Importante:** en este momento la BD está **vacía** (sin tus tablas de negocio). Solo existe el motor y una base llamada `app_db`.

3. **migrate.sh**  
   - **Qué:** espera a que Postgres responda y luego ejecuta `alembic upgrade head`.  
   - **Por qué:** las tablas las define el backend (modelos + migraciones), no el contenedor. Así el esquema viaja con el código en Git.

4. **uvicorn**  
   - **Qué:** arranca FastAPI y escucha HTTP (por defecto puerto 8000).  
   - **Por qué:** es el proceso que atiende al frontend.

### Opción B — Todo con Docker

```bash
docker compose up --build
```

Aquí el servicio `api` usa `scripts/entrypoint.sh`, que hace automáticamente:

1. Esperar a Postgres (`wait_for_db.py`)
2. Migrar (`alembic upgrade head`)
3. Arrancar Uvicorn

**Por qué un entrypoint:** si la API arranca antes que Postgres esté listo, fallaría al conectar. El entrypoint evita esa carrera.

---

## 4. Archivo por archivo (qué / por qué)

### `docker-compose.yml`

- **Qué:** describe dos servicios: `db` (Postgres) y `api` (backend).
- **Por qué:** un solo comando levanta la infraestructura. Puedes subir solo `db` si programas la API en tu máquina.
- **Detalle clave:** `api` apunta a `POSTGRES_HOST=db` porque dentro de Docker los servicios se encuentran por **nombre de servicio**, no por `localhost`.

### `Dockerfile`

- **Qué:** receta para construir la imagen de la API (Python + dependencias).
- **Por qué:** que la API corra igual en tu PC, en la de un compañero o en un servidor.
- **Detalle:** el `ENTRYPOINT` llama a `entrypoint.sh` antes de Uvicorn.

### `scripts/setup.sh`

- **Qué:** prepara el entorno de desarrollo.
- **Por qué:** un onboarding de un comando, sin pasos olvidados.

### `scripts/wait_for_db.py`

- **Qué:** intenta `SELECT 1` cada segundo hasta que Postgres responde (máx. ~30 s).
- **Por qué:** Postgres tarda unos segundos en arrancar. Sin esta espera, migrate/API fallarían “a veces” de forma aleatoria.

### `scripts/migrate.sh`

- **Qué:** espera la BD y aplica migraciones Alembic.
- **Por qué:** comando simple para desarrollo local cuando la API corre fuera de Docker.

### `scripts/entrypoint.sh`

- **Qué:** lo mismo que migrate, pero pensado para el contenedor `api`, y después ejecuta el comando final (`uvicorn ...`).
- **Por qué:** el contenedor no debe servir HTTP con un esquema desactualizado.
- **`exec "$@"`:** reemplaza el script por Uvicorn para que las señales (stop/restart) lleguen bien al proceso correcto.

### `.env` / `.env.example`

- **Qué:** contraseñas, URL de la BD, CORS, secretos.
- **Por qué:** no hardcodear secretos en el código. `.env` no se sube a Git; `.env.example` sí (sin secretos reales).

### `app/core/config.py`

- **Qué:** lee el `.env` y lo expone como `settings`.
- **Por qué:** un solo lugar para configuración; el resto del código usa `settings.DATABASE_URL`, etc.

### `app/db/base.py`

- **Qué:** clase `Base` de la que heredan todos los modelos.
- **Por qué:** Alembic mira `Base.metadata` para saber qué tablas “deberían” existir.

### `app/db/session.py`

- **Qué:** crea el motor SQLAlchemy y la fábrica `SessionLocal`.
- **Por qué:** abrir/cerrar conexiones de forma controlada. Aquí no hay reglas de negocio, solo el cable hacia Postgres.

### `app/api/deps.py` → `get_db`

- **Qué:** abre una sesión por request HTTP y la cierra al terminar.
- **Por qué:** cada petición usa su sesión y no deja conexiones colgadas.

### `alembic/env.py` + `alembic/versions/`

- **Qué:** configuración de migraciones y carpeta donde se guardan los “cambios de esquema” (archivos Python generados).
- **Por qué:** cuando agregas una columna, no editas la BD a mano: generas una revisión, la revisas, y la aplicas. El historial queda en Git.

Ciclo normal cuando creas un modelo nuevo:

```bash
# 1. Escribes app/models/user.py (class User(Base): ...)
# 2. Lo importas en app/models/__init__.py
# 3. Generas la migración:
alembic revision --autogenerate -m "add users"
# 4. Aplicas:
./scripts/migrate.sh
```

### Capas dentro de `app/`

```
Request HTTP
    ↓
endpoints/     → reciben la petición, casi sin lógica
    ↓
schemas/       → validan el JSON de entrada/salida
    ↓
services/      → deciden SI se puede y QUÉ hacer (reglas)
    ↓
repositories/  → ejecutan el SQL vía SQLAlchemy
    ↓
PostgreSQL
```

**Por qué tantas carpetas:** para que el proyecto no se convierta en un solo archivo gigante. Mañana puedes cambiar cómo guardas datos sin reescribir las URLs, o cambiar una regla sin tocar el SQL.

| Capa | Decide | No debería |
|------|--------|------------|
| Endpoint | Ruta, status code, Depends | Reglas de negocio largas |
| Service | Permisos, validaciones de dominio | Detalles de SQL |
| Repository | Queries, `add`, `commit` | Reglas tipo “¿el usuario es admin?” |
| Model | Columnas y relaciones | Respuestas HTTP |
| Schema | Forma del JSON | Hablar con la BD |

---

## 5. Qué NO hace el contenedor de la base

El servicio `db`:

- Sí: corre PostgreSQL, guarda datos en un volumen, abre el puerto 5432.
- No: no crea tus tablas de usuarios/productos, no valida email, no sabe de JWT.

Eso es a propósito. Si el SQL de negocio viviera dentro del contenedor:

- el esquema se desincronizaría del código Python,
- sería más difícil versionar cambios entre compañeros,
- mezclarías infraestructura con lógica.

---

## 6. Mapa mental rápido

```
¿Quiero encender solo la BD?          → docker compose up db -d
¿Quiero crear/actualizar tablas?      → ./scripts/migrate.sh
¿Quiero servir la API en local?       → uvicorn app.main:app --reload
¿Agregué un modelo nuevo?             → autogenerate + migrate
¿Dónde pongo una regla de negocio?    → app/services/
¿Dónde pongo un SELECT/INSERT?        → app/repositories/
¿Dónde pongo una URL nueva?           → app/api/v1/endpoints/
```

---

## 7. Si algo falla

| Síntoma | Causa probable | Qué revisar |
|---------|----------------|-------------|
| `Connection refused` a Postgres | La BD no está arriba | `docker compose up db -d` y `wait_for_db` |
| API arranca pero no hay tablas | No corriste migraciones | `./scripts/migrate.sh` |
| Autogenerate no ve tu modelo | No lo importaste | `app/models/__init__.py` |
| Frontend no puede llamar a la API | CORS | `CORS_ORIGINS` en `.env` |
| En Docker la API no encuentra la BD | Usaste `localhost` dentro del contenedor | En compose debe ser host `db` |

---

Cuando entiendas esta guía, el código comentado en cada archivo refuerza el mismo mensaje: **qué hace** y **por qué está ahí**.
