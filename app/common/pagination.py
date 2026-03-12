from __future__ import annotations

from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.sql import Select


class Pagination(BaseModel):
    limit: int = Field(default=50, ge=1, le=200)
    offset: int = Field(default=0, ge=0)


def apply_pagination(stmt: Select, p: Pagination) -> Select:
    return stmt.limit(p.limit).offset(p.offset)


def total_stmt(stmt: Select) -> Select:
    """SELECT count(*) FROM (<stmt>) AS subq"""
    return select(func.count()).select_from(stmt.subquery())


def add_total_over(stmt: Select, label: str = "total") -> Select:
    return stmt.add_columns(func.count().over().label(label))
