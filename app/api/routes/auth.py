from __future__ import annotations

from typing import List

from fastapi import APIRouter
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import AuthenticationBackend

from app.core.security import auth_backend
from app.db.user_db import get_user_db
from app.models.user import User, UserCreate, UserRead, UserUpdate


fastapi_users = FastAPIUsers[User, str](
    get_user_db,
    [auth_backend],
)


def get_auth_routers() -> List[APIRouter]:
    return [
        fastapi_users.get_auth_router(auth_backend),
        fastapi_users.get_register_router(UserRead, UserCreate),
        fastapi_users.get_users_router(UserRead, UserUpdate),
    ]
