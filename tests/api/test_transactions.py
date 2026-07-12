"""
Integration (API) — smoke de transactions (JWT + SQLite).

Valida el contrato HTTP; reglas de negocio → tests/services/test_transaction_service.py.
"""

from decimal import Decimal

import pytest

pytestmark = pytest.mark.integration


def test_transactions_require_auth(client):
    # Arrange / Act
    response = client.get("/api/v1/transactions")

    # Assert
    assert response.status_code == 401


def test_transaction_crud_smoke(client, auth_headers):
    # Arrange — dependencias vía API
    account = client.post(
        "/api/v1/accounts",
        json={"banco": "BBVA", "tipo": "corriente", "moneda": "COP", "saldo": "500"},
        headers=auth_headers,
    ).json()
    category = client.post(
        "/api/v1/categories",
        json={"nombre": "Mercado", "descripcion": ""},
        headers=auth_headers,
    ).json()
    sub = client.post(
        "/api/v1/subcategories",
        json={"category_id": category["id"], "nombre": "Verduras"},
        headers=auth_headers,
    ).json()
    payload = {
        "account_id": account["id"],
        "category_id": category["id"],
        "sub_category_id": sub["id"],
        "monto": "15.75",
        "tipo": "gasto",
        "fecha": "2026-07-11",
        "descripcion": "Tomates",
    }

    # Act
    created = client.post("/api/v1/transactions", json=payload, headers=auth_headers)
    assert created.status_code == 201, created.text
    tx_id = created.json()["id"]

    listed = client.get("/api/v1/transactions", headers=auth_headers)
    got = client.get(f"/api/v1/transactions/{tx_id}", headers=auth_headers)
    account_after = client.get(
        f"/api/v1/accounts/{account['id']}",
        headers=auth_headers,
    ).json()
    deleted = client.delete(f"/api/v1/transactions/{tx_id}", headers=auth_headers)
    account_restored = client.get(
        f"/api/v1/accounts/{account['id']}",
        headers=auth_headers,
    ).json()

    # Assert — listado paginado
    assert listed.status_code == 200
    body = listed.json()
    assert body["total"] == 1
    assert body["limit"] == 20
    assert any(t["id"] == tx_id for t in body["items"])
    assert got.status_code == 200
    assert got.json()["descripcion"] == "Tomates"
    assert Decimal(str(account_after["saldo"])) == Decimal("484.25")
    assert deleted.status_code == 204
    assert Decimal(str(account_restored["saldo"])) == Decimal("500.00")
