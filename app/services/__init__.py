"""
app/services/ — Reglas de negocio
---------------------------------

QUÉ ES
    El lugar donde decides QUÉ se puede hacer.

POR QUÉ EXISTE
    Ejemplo: "no crear dos usuarios con el mismo email",
    "solo un admin puede borrar X", "calcular el total del pedido".

    Eso NO va en el endpoint (que solo recibe HTTP)
    ni en el repository (que solo sabe hacer SQL).

FLUJO
    Endpoint → Service (decide) → Repository (persiste) → Postgres
"""
