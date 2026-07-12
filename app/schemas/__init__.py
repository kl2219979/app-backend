"""
app/schemas/ — Contratos HTTP (Pydantic)

Preferir PascalCase: AccountCreate, CategoryResponse, …
Los alias camelCase (accountCreate, …) se mantienen por compatibilidad.
"""

from app.schemas.account import AccountCreate, AccountResponse, AccountUpdate
from app.schemas.auth import Token, UserPublic, UserRegister
from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate
from app.schemas.pagination import Page, PageParams
from app.schemas.report import CategoryTotal, ReportSummary
from app.schemas.sub_category import SubCategoryCreate, SubCategoryResponse, SubCategoryUpdate
from app.schemas.transaction import TransactionCreate, TransactionResponse, TransactionUpdate
from app.schemas.user import UserCreate, UserResponse, UserUpdate

__all__ = [
    "AccountCreate",
    "AccountResponse",
    "AccountUpdate",
    "CategoryCreate",
    "CategoryResponse",
    "CategoryTotal",
    "CategoryUpdate",
    "Page",
    "PageParams",
    "ReportSummary",
    "SubCategoryCreate",
    "SubCategoryResponse",
    "SubCategoryUpdate",
    "Token",
    "TransactionCreate",
    "TransactionResponse",
    "TransactionUpdate",
    "UserCreate",
    "UserPublic",
    "UserRegister",
    "UserResponse",
    "UserUpdate",
]
