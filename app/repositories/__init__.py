"""
app/repositories/ — Cómo se habla con la BD
-------------------------------------------

QUÉ ES
    Funciones/clases que hacen SELECT, INSERT, UPDATE, DELETE con SQLAlchemy.

POR QUÉ EXISTE
    Concentra el SQL/ORM en un solo sitio.
    Si mañana cambias una query, no tienes que buscarla en todos los endpoints.

QUÉ NO VA AQUÍ
    Reglas de negocio ("¿puede este usuario hacer esto?").
    Eso pertenece a services/.
"""
