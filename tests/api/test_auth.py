"""
Tests AAA de autenticación (API + BD de prueba SQLite).
"""


def test_register_creates_user(client):
    # Arrange
    payload = {
        "nombres": "Luis",
        "apellidos": "Gómez",
        "fecha_nacimiento": "1990-01-01",
        "genero": "M",
        "correo": "luis@example.com",
        "usuario": "luis90",
        "contrasena": "clavesegura",
    }

    # Act
    response = client.post("/api/v1/auth/register", json=payload)

    # Assert
    assert response.status_code == 201
    body = response.json()
    assert body["correo"] == "luis@example.com"
    assert body["usuario"] == "luis90"
    assert "contrasena" not in body
    assert "contrasena_hash" not in body


def test_register_rejects_duplicate_email(client, registered_user):
    # Arrange
    payload = {
        **registered_user,
        "usuario": "otro_usuario",
    }

    # Act
    response = client.post("/api/v1/auth/register", json=payload)

    # Assert
    assert response.status_code == 409


def test_login_returns_token(client, registered_user):
    # Arrange / Act
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": registered_user["correo"],
            "password": registered_user["contrasena"],
        },
    )

    # Assert
    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


def test_login_rejects_bad_password(client, registered_user):
    # Arrange / Act
    response = client.post(
        "/api/v1/auth/login",
        data={"username": registered_user["usuario"], "password": "mala"},
    )

    # Assert
    assert response.status_code == 401


def test_me_requires_auth(client):
    # Arrange / Act
    response = client.get("/api/v1/auth/me")

    # Assert
    assert response.status_code == 401


def test_me_returns_current_user(client, auth_headers, registered_user):
    # Arrange / Act
    response = client.get("/api/v1/auth/me", headers=auth_headers)

    # Assert
    assert response.status_code == 200
    assert response.json()["usuario"] == registered_user["usuario"]
