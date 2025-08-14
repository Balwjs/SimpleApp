from __future__ import annotations

from typing import Optional
from sqlmodel import SQLModel, Field
from fastapi_users_db_sqlalchemy.generics import GUID


class User(SQLModel, table=True):
    __tablename__ = "users"
    id: GUID = Field(default=None, primary_key=True)
    email: str = Field(index=True, nullable=False, unique=True)
    hashed_password: str
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False


class UserRead(SQLModel):
    id: GUID
    email: str
    is_active: bool
    is_superuser: bool
    is_verified: bool


class UserCreate(SQLModel):
    email: str
    password: str


class UserUpdate(SQLModel):
    email: Optional[str] = None
    password: Optional[str] = None
