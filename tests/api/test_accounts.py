"""
Integration (API) — smoke CRUD de accounts (JWT + SQLite).
"""

import pytest

pytestmark = pytest.mark.integration


def test_create_and_list_account(client, auth_headers):
    # Arrange
    payload = {
        "banco": "Bancolombia",
        "tipo": "ahorros",
        "moneda": "COP",
        "saldo": "1000.00",
    }

    # Act
    create_resp = client.post("/api/v1/accounts", json=payload, headers=auth_headers)
    list_resp = client.get("/api/v1/accounts", headers=auth_headers)

    # Assert
    assert create_resp.status_code == 201, create_resp.text
    created = create_resp.json()
    assert created["banco"] == "Bancolombia"
    assert "user_id" in created

    assert list_resp.status_code == 200
    accounts = list_resp.json()
    assert len(accounts) == 1
    assert accounts[0]["id"] == created["id"]


def test_accounts_require_auth(client):
    # Arrange / Act
    response = client.get("/api/v1/accounts")

    # Assert
    assert response.status_code == 401


def test_get_update_delete_account(client, auth_headers):
    # Arrange
    created = client.post(
        "/api/v1/accounts",
        json={"banco": "Nequi", "tipo": "digital", "moneda": "COP", "saldo": "50"},
        headers=auth_headers,
    ).json()
    account_id = created["id"]

    # Act
    get_resp = client.get(f"/api/v1/accounts/{account_id}", headers=auth_headers)
    upd_resp = client.put(
        f"/api/v1/accounts/{account_id}",
        json={"banco": "Nequi Pro"},
        headers=auth_headers,
    )
    del_resp = client.delete(f"/api/v1/accounts/{account_id}", headers=auth_headers)
    missing = client.get(f"/api/v1/accounts/{account_id}", headers=auth_headers)

    # Assert
    assert get_resp.status_code == 200
    assert upd_resp.status_code == 200
    assert upd_resp.json()["banco"] == "Nequi Pro"
    assert del_resp.status_code == 204
    assert missing.status_code == 404
