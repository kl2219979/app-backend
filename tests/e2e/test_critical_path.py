"""
E2E — pocos caminos críticos contra el stack vivo.

Por diseño la pirámide tiene MUY pocos E2E. Este módulo está omitido
salvo que se active explícitamente:

  RUN_E2E=1 E2E_BASE_URL=http://localhost:8000 pytest -m e2e

Flujo cubierto:
  health → register → login → create account → create category/sub → transaction
"""

from __future__ import annotations

import os
import uuid

import httpx
import pytest

pytestmark = pytest.mark.e2e


@pytest.fixture()
def e2e_base_url() -> str:
    if os.getenv("RUN_E2E", "").lower() not in {"1", "true", "yes"}:
        pytest.skip("E2E deshabilitado. Exporta RUN_E2E=1 y opcionalmente E2E_BASE_URL.")
    return os.getenv("E2E_BASE_URL", "http://localhost:8000").rstrip("/")


def test_critical_money_path(e2e_base_url: str):
    # Arrange
    suffix = uuid.uuid4().hex[:8]
    register_payload = {
        "nombres": "E2E",
        "apellidos": "Runner",
        "fecha_nacimiento": "1992-02-02",
        "genero": "O",
        "correo": f"e2e_{suffix}@example.com",
        "usuario": f"e2e_{suffix}",
        "contrasena": "secreto12345",
    }

    with httpx.Client(base_url=e2e_base_url, timeout=30.0) as client:
        # Act — health
        health = client.get("/api/v1/health")
        assert health.status_code == 200, health.text

        # Act — register + login
        reg = client.post("/api/v1/auth/register", json=register_payload)
        assert reg.status_code == 201, reg.text

        login = client.post(
            "/api/v1/auth/login",
            data={
                "username": register_payload["usuario"],
                "password": register_payload["contrasena"],
            },
        )
        assert login.status_code == 200, login.text
        headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

        # Act — account + taxonomy + transaction
        account = client.post(
            "/api/v1/accounts",
            json={"banco": "E2E Bank", "tipo": "ahorros", "moneda": "COP", "saldo": "1"},
            headers=headers,
        )
        assert account.status_code == 201, account.text

        category = client.post(
            "/api/v1/categories",
            json={"nombre": f"E2ECat_{suffix}", "descripcion": "e2e"},
            headers=headers,
        )
        assert category.status_code == 201, category.text

        sub = client.post(
            "/api/v1/subcategories",
            json={
                "category_id": category.json()["id"],
                "nombre": f"E2ESub_{suffix}",
            },
            headers=headers,
        )
        assert sub.status_code == 201, sub.text

        tx = client.post(
            "/api/v1/transactions",
            json={
                "account_id": account.json()["id"],
                "category_id": category.json()["id"],
                "sub_category_id": sub.json()["id"],
                "monto": "9.99",
                "fecha": "2026-07-11",
                "descripcion": "e2e path",
            },
            headers=headers,
        )

        # Assert
        assert tx.status_code == 201, tx.text
        assert tx.json()["descripcion"] == "e2e path"
