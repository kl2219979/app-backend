"""
tests/conftest.py — Fixtures compartidas (Arrange del patrón AAA)
=================================================================

Pirámide de tests (ver docs/TESTING.md):
  - Unitarios: usan `db_session` (SQLite en memoria) sin HTTP.
  - Integración API: usan `client` + override de `get_db`.
  - Integration Postgres / E2E: marcados y omitidos por defecto.

Markers registrados en pyproject.toml: unit, integration, e2e.
"""

from __future__ import annotations

import os
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401 — registra tablas en Base.metadata
from app.api.deps import get_db
from app.db.base import Base
from app.main import app


def pytest_configure(config: pytest.Config) -> None:
    """Asegura markers conocidos aunque se ejecute fuera de pyproject."""
    config.addinivalue_line("markers", "unit: test unitario aislado (rápido)")
    config.addinivalue_line(
        "markers",
        "integration: test de integración (API TestClient o Postgres)",
    )
    config.addinivalue_line("markers", "e2e: end-to-end contra stack vivo")


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    """Arrange: sesión SQLite aislada por test (unitarios y API)."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """Arrange: TestClient con get_db apuntando a la BD de test."""

    def override_get_db() -> Generator[Session, None, None]:
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def registered_user(client: TestClient) -> dict:
    """Arrange: usuario creado vía /auth/register."""
    payload = {
        "nombres": "Ana",
        "apellidos": "Pérez",
        "fecha_nacimiento": "1995-05-10",
        "genero": "F",
        "correo": "ana@example.com",
        "usuario": "ana95",
        "contrasena": "secreto123",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201, response.text
    return payload


@pytest.fixture()
def auth_headers(client: TestClient, registered_user: dict) -> dict[str, str]:
    """Arrange: header Bearer tras login."""
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": registered_user["usuario"],
            "password": registered_user["contrasena"],
        },
    )
    assert response.status_code == 200, response.text
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def postgres_url() -> str | None:
    """URL Postgres para integration/e2e; None si no está habilitado."""
    if os.getenv("RUN_INTEGRATION", "").lower() not in {"1", "true", "yes"}:
        return None
    return os.getenv("TEST_DATABASE_URL") or os.getenv("DATABASE_URL")
