"""
app/repositories/sub_category.py — Acceso a datos de SubCategory
================================================================
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.sub_category import SubCategory


class SubCategoryRepository:
    """CRUD de sub_categories."""

    @staticmethod
    def get_by_id(db: Session, sub_category_id: int) -> SubCategory | None:
        return db.get(SubCategory, sub_category_id)

    @staticmethod
    def list_by_category(db: Session, category_id: int) -> list[SubCategory]:
        return list(
            db.scalars(
                select(SubCategory)
                .where(SubCategory.category_id == category_id)
                .order_by(SubCategory.nombre.asc())
            ).all()
        )

    @staticmethod
    def list_all(db: Session) -> list[SubCategory]:
        return list(
            db.scalars(select(SubCategory).order_by(SubCategory.nombre.asc())).all()
        )

    @staticmethod
    def create(db: Session, sub_category: SubCategory) -> SubCategory:
        db.add(sub_category)
        db.flush()
        db.refresh(sub_category)
        return sub_category

    @staticmethod
    def update(db: Session, sub_category: SubCategory) -> SubCategory:
        db.add(sub_category)
        db.flush()
        db.refresh(sub_category)
        return sub_category

    @staticmethod
    def delete(db: Session, sub_category: SubCategory) -> None:
        db.delete(sub_category)
        db.flush()
