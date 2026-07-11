"""
tests/conftest.py — Fixtures compartidas de pytest.

`client` expone un TestClient sobre la app FastAPI para probar endpoints
sin levantar un servidor real. Añade aquí fixtures de BD de prueba cuando
existan modelos y migraciones de test.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    """Cliente HTTP síncrono apuntando a la app en memoria."""
    return TestClient(app)
