"""
tests/conftest.py — Fixtures compartidas de pytest
==================================================

QUÉ ES
------
Fixtures reutilizables por todos los tests (cliente HTTP, etc.).

AAA
---
Las fixtures suelen vivir en la fase Arrange: preparan el escenario
antes del Act del test.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    """
    Arrange: cliente HTTP contra la app en memoria (sin uvicorn real).

    Uso en un test:
        def test_algo(client):
            # Act
            response = client.get("/api/v1/health")
            # Assert
            assert response.status_code == 200
    """
    return TestClient(app)
