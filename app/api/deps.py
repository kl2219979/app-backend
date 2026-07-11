"""
app/api/deps.py — Dependencias de FastAPI
-----------------------------------------

QUÉ ES
    Funciones que FastAPI inyecta en los endpoints con `Depends(...)`.

POR QUÉ get_db EXISTE
    Cada request HTTP necesita su propia sesión de BD y debe cerrarla al final.
    Si abrieras conexiones a mano en cada endpoint, sería fácil olvidar el close
    y agotar el pool de Postgres.

CÓMO SE USA (ejemplo futuro)
    @router.post("/users")
    def create_user(db: Session = Depends(get_db)):
        ...
"""

from collections.abc import Generator

from sqlalchemy.orm import Session

from app.db.session import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """Entrega una sesión por request y la cierra sí o sí al terminar."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
