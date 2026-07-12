"""
Patrón AAA en tests (Arrange – Act – Assert)
============================================

QUÉ ES
------
Una forma simple de estructurar cada test en tres bloques claros:

1. Arrange (Preparar)
   Armas el escenario: datos, mocks, cliente HTTP, usuario de prueba, etc.

2. Act (Actuar)
   Ejecutas UNA acción: llamar una función o hacer un request.

3. Assert (Verificar)
   Compruebas el resultado: status code, valor devuelto, excepción, etc.

POR QUÉ
-------
- Se lee el test de arriba a abajo como una historia.
- Fallos más fáciles de diagnosticar (¿falló la prep, la acción o la expectativa?).
- Evita tests que hacen demasiadas cosas a la vez.

EJEMPLO
-------
    def test_verify_password_accepts_correct_password():
        # Arrange
        plain = "secreto123"
        hashed = hash_password(plain)

        # Act
        ok = verify_password(plain, hashed)

        # Assert
        assert ok is True

DÓNDE ESTÁN LOS TESTS
---------------------
  tests/api/          → endpoints HTTP (TestClient)
  tests/core/         → unidades sin BD (security, etc.)

Más adelante: tests de repositories/services con BD de prueba.
"""
