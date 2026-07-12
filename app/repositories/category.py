"""
app/repositories/category.py — Acceso a datos de Category
=========================================================
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.category import Category


class CategoryRepository:
    """CRUD de categories."""

    @staticmethod
    def get_by_id(db: Session, category_id: int) -> Category | None:
        return db.get(Category, category_id)

    @staticmethod
    def get_by_nombre(db: Session, nombre: str) -> Category | None:
        return db.scalar(select(Category).where(Category.nombre == nombre))

    @staticmethod
    def list_all(db: Session) -> list[Category]:
        return list(
            db.scalars(select(Category).order_by(Category.nombre.asc())).all()
        )

    @staticmethod
    def create(db: Session, category: Category) -> Category:
        db.add(category)
        db.flush()
        db.refresh(category)
        return category

    @staticmethod
    def update(db: Session, category: Category) -> Category:
        db.add(category)
        db.flush()
        db.refresh(category)
        return category

    @staticmethod
    def delete(db: Session, category: Category) -> None:
        db.delete(category)
        db.flush()
