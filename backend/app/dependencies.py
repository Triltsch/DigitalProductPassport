"""FastAPI dependency helpers for authentication and role checks."""

from __future__ import annotations

from functools import lru_cache
from typing import Sequence

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import get_settings
from app.infrastructure.keycloak.auth import KeycloakTokenValidator, TokenValidationError
from app.infrastructure.keycloak.models import CurrentUser


http_bearer = HTTPBearer(auto_error=False)


@lru_cache(maxsize=1)
def get_token_validator() -> KeycloakTokenValidator:
    """Build and cache the token validator shared across requests."""

    return KeycloakTokenValidator(get_settings())


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(http_bearer),
    token_validator: KeycloakTokenValidator = Depends(get_token_validator),
) -> CurrentUser:
    """Validate a bearer token and expose the authenticated user context."""

    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        return token_validator.validate_token(credentials.credentials)
    except TokenValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


def require_roles(required_roles: Sequence[str]):
    """Require the current user to hold at least one of the provided realm roles."""

    required_role_set = frozenset(required_roles)

    def dependency(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if required_role_set and not any(current_user.has_role(role) for role in required_role_set):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient role membership.",
            )

        return current_user

    return dependency
