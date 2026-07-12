"""
Integration (API) — smoke CRUD de categories / subcategories (JWT + SQLite).

Pocos tests HTTP: la lógica detallada vive en tests/services.
"""

import pytest

pytestmark = pytest.mark.integration


def test_categories_require_auth(client):
    # Arrange / Act
    response = client.get("/api/v1/categories")

    # Assert
    assert response.status_code == 401


def test_category_and_subcategory_crud_smoke(client, auth_headers):
    # Arrange / Act — category
    create_cat = client.post(
        "/api/v1/categories",
        json={"nombre": "Ocio", "descripcion": "Entretenimiento"},
        headers=auth_headers,
    )
    assert create_cat.status_code == 201, create_cat.text
    cat_id = create_cat.json()["id"]

    # Act — subcategory
    create_sub = client.post(
        "/api/v1/subcategories",
        json={"category_id": cat_id, "nombre": "Cine", "descripcion": ""},
        headers=auth_headers,
    )
    assert create_sub.status_code == 201, create_sub.text
    sub_id = create_sub.json()["id"]

    listed = client.get(
        f"/api/v1/subcategories?category_id={cat_id}",
        headers=auth_headers,
    )
    assert listed.status_code == 200
    assert len(listed.json()) == 1

    # Cleanup
    assert (
        client.delete(f"/api/v1/subcategories/{sub_id}", headers=auth_headers).status_code
        == 204
    )
    assert (
        client.delete(f"/api/v1/categories/{cat_id}", headers=auth_headers).status_code
        == 204
    )
