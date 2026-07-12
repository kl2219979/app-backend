"""
Guía de testing del backend
===========================

Este documento es la referencia completa de cómo (y por qué) testamos.
Complementa el patrón AAA con la **pirámide de tests** del equipo.

---------------------------------------------------------------------------
1. Principio del equipo (pirámide)
---------------------------------------------------------------------------

    ┌─────────────────────────────┐
    │  E2E (pocos)                │  Stack vivo: API + Postgres reales
    ├─────────────────────────────┤
    │  Integration (algunos)      │  TestClient HTTP o Postgres opcional
    ├─────────────────────────────┤
    │  Unit (muchos)              │  Services, repositories, security
    └─────────────────────────────┘

Regla práctica:
  - La mayor parte de la cobertura vive en **unitarios**.
  - Los tests HTTP (`tests/api`) son **smoke** del contrato, no reescriben
    toda la lógica del service.
  - Los E2E solo cubren caminos de negocio críticos y están **apagados**
    por defecto (hay que activarlos con variables de entorno).

Por qué:
  - Unitarios son rápidos, estables y baratos de mantener.
  - Demasiados E2E vuelven el CI frágil y lento.
  - Si una regla de negocio falla, el unitario del service la señala primero.

---------------------------------------------------------------------------
2. Patrón AAA (Arrange – Act – Assert)
---------------------------------------------------------------------------

Cada test se lee como una mini-historia en tres bloques:

1. Arrange — preparas datos, fixtures, usuario, payloads.
2. Act     — ejecutas UNA acción (llamar service, repo o un request).
3. Assert  — verificas status, valores, excepciones.

Ejemplo unitario (service)::

    def test_create_rejects_foreign_account(db_session):
        # Arrange
        owner = make_user(db_session, correo="a@x.com", usuario="owner")
        other = make_user(db_session, correo="b@x.com", usuario="other")
        ...
        # Act / Assert
        with pytest.raises(HTTPException) as exc:
            TransactionService.create(db_session, owner, data)
        assert exc.value.status_code == 404

Evita tests que hacen muchas acciones seguidas sin aserciones intermedias
(salvo smokes de integración deliberadamente cortos).

---------------------------------------------------------------------------
3. Mapa de carpetas
---------------------------------------------------------------------------

  tests/
  ├── conftest.py              Fixtures globales (db_session, client, auth)
  ├── helpers.py               Factories (make_user, make_account, …)
  ├── core/                    UNIT — security, utilidades sin BD HTTP
  ├── services/                UNIT — reglas de negocio (prioridad alta)
  ├── repositories/            UNIT — consultas SQLAlchemy / ownership
  ├── api/                     INTEGRATION — TestClient + SQLite en memoria
  ├── integration/             INTEGRATION — Postgres real (opt-in)
  └── e2e/                     E2E — HTTP contra servidor vivo (opt-in)

Markers (pyproject.toml)::

  @pytest.mark.unit
  @pytest.mark.integration
  @pytest.mark.e2e

Cada módulo de tests declara ``pytestmark = pytest.mark.<capa>``.

---------------------------------------------------------------------------
4. Fixtures y factories
---------------------------------------------------------------------------

``db_session``
  Motor SQLite en memoria, tablas creadas/destruídas por test.
  Sirve para unitarios de service/repository y para API (vía override).

``client``
  ``TestClient`` de FastAPI con ``get_db`` sobreescrito a ``db_session``.
  No necesita Docker ni Postgres.

``registered_user`` / ``auth_headers``
  Arrange de flujos autenticados en ``tests/api``.

``tests/helpers.py``
  ``make_user``, ``make_account``, ``make_category``, ``make_sub_category``,
  ``make_transaction`` — crean filas sin HTTP. Preferirlas en unitarios.

Importante:
  - Los unitarios de service NO deben depender de endpoints.
  - Los smokes de API NO deben duplicar todas las ramas del service
    (mismatched subcategory, 409 de nombre, etc. → van en services/).

---------------------------------------------------------------------------
5. Qué testear en cada capa
---------------------------------------------------------------------------

UNIT — services (prioridad #1)
  - Ownership (cuenta / transacción solo del usuario del “JWT” simulado).
  - Validaciones de negocio (subcategoría ∈ categoría).
  - Conflictos 409, not found 404, forbidden 403.
  - Efectos de update/delete sobre la sesión.

UNIT — repositories
  - Filtros por user_id / joins (Transaction ↔ Account).
  - Lookups por correo/usuario.
  - Ordenamientos básicos.

UNIT — core
  - bcrypt (hash ≠ plaintext, verify ok/fail).
  - JWT create/decode/expiry.

INTEGRATION — api/
  - Status codes del contrato público.
  - Auth requerida (401 sin Bearer).
  - Un happy-path CRUD corto por recurso nuevo.

INTEGRATION — integration/ (opt-in)
  - Conectividad Postgres + presencia de ``alembic_version``.
  - Ampliar solo si hay bugs de dialecto SQLite vs Postgres.

E2E — e2e/ (opt-in)
  - Un camino crítico: health → register → login → account →
    category/sub → transaction.
  - No agregues E2E por cada endpoint.

---------------------------------------------------------------------------
6. Cómo ejecutar
---------------------------------------------------------------------------

Suite diaria (unit + API smoke; Postgres/E2E se auto-omiten)::

    source .venv/bin/activate
    pytest -q

Solo unitarios::

    pytest -m unit -q

Solo integración API (y smoke Postgres si RUN_INTEGRATION=1)::

    pytest -m integration -q

Postgres real::

    docker compose up db -d
    ./scripts/migrate.sh
    RUN_INTEGRATION=1 \\
      TEST_DATABASE_URL="postgresql+psycopg2://postgres:postgres@localhost:5432/app_db" \\
      pytest -m integration -q tests/integration

E2E (API + DB ya levantados, p. ej. ``docker compose up``)::

    RUN_E2E=1 E2E_BASE_URL=http://localhost:8000 pytest -m e2e -q

Verbose / un archivo::

    pytest tests/services/test_transaction.py -v

---------------------------------------------------------------------------
7. Política al agregar código nuevo
---------------------------------------------------------------------------

Cuando agregues un endpoint o regla:

1. Escribe primero (o junto) **unitarios del service** para la regla nueva.
2. Si tocas SQL no trivial, añade unitario de **repository**.
3. Añade **como máximo un smoke** en ``tests/api`` si el contrato HTTP es nuevo.
4. No abras un E2E nuevo salvo camino de producto crítico acordado con QA.
5. Documenta el caso especial aquí o en ``docs/HOJA_RUTA.md`` si cambia la
   estrategia.

Checklist PR (QA / Kevin)::

  [ ] ``pytest -q`` en verde
  [ ] Nuevas reglas de negocio cubiertas en ``tests/services``
  [ ] Sin secretos en fixtures
  [ ] Markers correctos (unit / integration / e2e)

---------------------------------------------------------------------------
8. Qué NO hacer
---------------------------------------------------------------------------

  - No uses la BD de producción en tests.
  - No dependas del orden de ejecución entre archivos.
  - No mocks excesivos del ORM si un SQLite en memoria basta (más realista).
  - No copies el mismo assert en service + API + E2E (pirámide, no triplicar).
  - No desactives markers para “hacer pasar” el CI: arregla la causa.

---------------------------------------------------------------------------
9. Relación con otras docs
---------------------------------------------------------------------------

  - ``docs/HOJA_RUTA.md`` — qué se implementó por pasos (incluye testing).
  - ``docs/SEGURIDAD.md`` — JWT / bcrypt (cubierto en tests/core).
  - ``docs/REPOSITORIOS.md`` — contrato de acceso a datos.
  - ``docs/MODELOS.md`` — tablas y FK (contexto para factories).
  - ``README.md`` — comandos rápidos ``pytest`` / markers.

---------------------------------------------------------------------------
10. Inventario actual (orientativo)
---------------------------------------------------------------------------

  Unit:
    tests/core/test_security.py
    tests/services/test_*_service.py      (account, category, sub_category,
                                           transaction, user)
    tests/services/test_seed_catalog.py
    tests/repositories/test_*_repository.py
                                          (account, category, transaction, user)

  Integration:
    tests/api/test_health.py
    tests/api/test_auth.py
    tests/api/test_accounts.py
    tests/api/test_categories.py
    tests/api/test_transactions.py
    tests/integration/test_postgres_smoke.py   (opt-in)

  E2E:
    tests/e2e/test_critical_path.py            (opt-in)

CI:
  .github/workflows/ci.yml — ruff + pytest -m "not e2e"

Nota: los basenames deben ser únicos entre carpetas
(``test_account_service.py`` vs ``test_account_repository.py``) para evitar
errores de collection de pytest.

Actualiza este inventario cuando agregues módulos relevantes.
"""
