"""
app/schemas/ — Forma del JSON de la API
---------------------------------------

QUÉ ES
    Clases Pydantic que validan lo que entra y sale por HTTP.

POR QUÉ SEPARARLO DE models/
    - models/ habla con la BD (columnas, relaciones).
    - schemas/ habla con el cliente (qué campos se exponen en el JSON).

    Así no filtras password_hash u otros detalles internos al frontend.

Schemas de auth: `app/schemas/auth.py` (registro, token, usuario público).
Documentación: `docs/SEGURIDAD.md`.
"""
