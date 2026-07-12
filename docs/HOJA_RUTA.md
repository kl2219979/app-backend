# Hoja de ruta — pasos 1 a 5 (implementados)
# ==========================================
#
# Este documento describe qué se hizo en cada paso de maduración del backend.
#
# ---------------------------------------------------------------------------
# Paso 1 — Unificar Alembic (un solo head)
# ---------------------------------------------------------------------------
# Problema: había varias revisiones vacías en paralelo → dos heads.
# Solución: se eliminaron las migraciones vacías:
#   - 08a8c3ba63f4_add_initial_schema.py
#   - c70ed89af933_add_initial_schema.py
#   - 72606699bc47_add_initial_schema.py
# Quedó solo: 72b0c849201b_add_initial_schema.py (DDL real).
#
# Si tu BD local tenía un revision_id borrado:
#   docker compose up db -d
#   alembic stamp 72b0c849201b
#   # o, si la BD está vacía:
#   ./scripts/migrate.sh
#
# Verificar:
#   alembic heads   → debe mostrar un solo head
#
# ---------------------------------------------------------------------------
# Paso 2 — CRUD real de Account (JWT + service + repository)
# ---------------------------------------------------------------------------
# Capas:
#   schemas/account.py     AccountCreate / Update / Response (sin user_id en create)
#   services/account.py    AccountService (solo cuentas del usuario del token)
#   endpoints/account.py   /api/v1/accounts  (Bearer obligatorio)
#   repositories/account.py (ya existía)
#
# Flujo: Endpoint → Service → Repository → Postgres
#
# ---------------------------------------------------------------------------
# Paso 3 — Tests AAA de auth + accounts
# ---------------------------------------------------------------------------
#   tests/conftest.py          SQLite en memoria + fixtures auth_headers
#   tests/api/test_auth.py     register / login / me
#   tests/api/test_accounts.py create / list / get / update / delete
#   tests/core/test_security.py (ya existía)
#
# Correr:  pytest -q
#
# ---------------------------------------------------------------------------
# Paso 4 — Category, SubCategory, Transaction
# ---------------------------------------------------------------------------
# Misma plantilla que Account:
#   services/category.py, sub_category.py, transaction.py
#   endpoints con rutas plurales y JWT
#
# Reglas extra en TransactionService:
#   - la cuenta debe ser del usuario
#   - subcategoría debe pertenecer a la categoría
#
# ---------------------------------------------------------------------------
# Paso 5 — Limpieza y unificación
# ---------------------------------------------------------------------------
# - Schemas en PascalCase (AccountCreate, …) con alias camelCase legacy
# - Rutas plurales:
#     /accounts  /categories  /subcategories  /transactions  /users
# - Stubs de hot-reload eliminados
# - Users: alta solo en /auth/register; /users/{id} es perfil propio
# - services/ poblado (ya no carpeta vacía)
#
# Mapa rápido de API (todas salvo health/auth-login/register requieren JWT
# excepto register/login/health):
#   POST /api/v1/auth/register
#   POST /api/v1/auth/login
#   GET  /api/v1/auth/me
#   CRUD /api/v1/accounts
#   CRUD /api/v1/categories
#   CRUD /api/v1/subcategories
#   CRUD /api/v1/transactions
#   GET/PUT/DELETE /api/v1/users/{id}  (solo el propio id)
#
# Ver también: docs/SEGURIDAD.md, docs/REPOSITORIOS.md, docs/TESTING.md
#
# ---------------------------------------------------------------------------
# Paso 6 — Pirámide de tests (muchos unitarios, algunos integration, pocos E2E)
# ---------------------------------------------------------------------------
# Objetivo: madurar cobertura sin inflar E2E.
#
# Unit (mayoría):
#   tests/core/           security (hash + JWT)
#   tests/services/       test_*_service.py (account, category, sub_category,
#                         transaction, user)
#   tests/repositories/   test_*_repository.py (filtros, joins, lookups)
#   tests/helpers.py      factories make_* para Arrange sin HTTP
#
# Integration (algunos):
#   tests/api/            smoke HTTP con TestClient + SQLite
#                         (auth, accounts, categories, transactions, health)
#   tests/integration/    Postgres real — solo con RUN_INTEGRATION=1
#
# E2E (pocos, opt-in):
#   tests/e2e/test_critical_path.py
#     health → register → login → account → category/sub → transaction
#     Activar: RUN_E2E=1 E2E_BASE_URL=http://localhost:8000 pytest -m e2e
#
# Markers: unit | integration | e2e  (ver pyproject.toml y docs/TESTING.md)
#
# Comandos:
#   pytest -q                 # diario (Postgres/E2E se auto-omiten)
#   pytest -m unit -q         # solo unitarios
#   pytest -m integration -q  # API smoke (+ Postgres si RUN_INTEGRATION=1)
#
# Documentación detallada y política PR: docs/TESTING.md
#
# ---------------------------------------------------------------------------
# Paso 7 — CI, paginación, seeds y saldo de cuentas
# ---------------------------------------------------------------------------
# CI (GitHub Actions):
#   .github/workflows/ci.yml
#   - ruff check app tests
#   - pytest -q -m "not e2e"  (suite diaria; Postgres/E2E opt-in fuera de CI)
#
# Paginación + filtros (transactions):
#   GET /api/v1/transactions?limit=&offset=&account_id=&category_id=
#       &tipo=gasto|ingreso&date_from=&date_to=
#   Respuesta: { items, total, limit, offset }  (schemas/pagination.py)
#
# Tipo de movimiento + saldo:
#   transactions.tipo = "gasto" | "ingreso"  (migración a1b2c3d4e5f6)
#   gasto resta del Account.saldo; ingreso suma; delete/update revierten
#
# Seeds:
#   python scripts/seed.py
#   Catálogo en app/services/seed.py (idempotente)
#
# Aplicar en local tras pull:
#   ./scripts/migrate.sh
#   python scripts/seed.py
#   docker compose up --build -d   # si usas API en Docker
#
