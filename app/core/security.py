from __future__ import annotations

from fastapi_users.authentication import AuthenticationBackend, BearerTransport, JWTStrategy
from app.core.config import get_settings


settings = get_settings()

bearer_transport = BearerTransport(tokenUrl="/api/auth/jwt/login")


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=settings.secret, lifetime_seconds=60 * 60 * 8)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)
