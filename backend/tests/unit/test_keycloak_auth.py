"""Unit tests for Keycloak JWT validation and authorization helpers."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import jwt
import pytest
from fastapi import HTTPException

from app.config import Settings
from app.dependencies import require_roles
from app.infrastructure.keycloak.auth import KeycloakTokenValidator
from app.infrastructure.keycloak.models import CurrentUser


class StaticSigningKeyResolver:
    """Deterministic signing key resolver for unit tests."""

    def __init__(self, signing_key: str) -> None:
        self._signing_key = signing_key

    def prime(self) -> None:
        """No-op cache warmup for static test keys."""

    def resolve_signing_key(self, token: str) -> str:
        """Return the same key for every token under test."""

        del token
        return self._signing_key


def test_current_user_extracts_roles_from_realm_access() -> None:
    """CurrentUser should normalize subject, roles, and tenant context from claims."""

    current_user = CurrentUser.from_claims(
        {
            "sub": "user-123",
            "tenant_id": "tenant-a",
            "preferred_username": "alice",
            "email": "alice@example.com",
            "realm_access": {"roles": ["ADMIN", "ADMIN", "AUDITOR"]},
        }
    )

    assert current_user.subject == "user-123"
    assert current_user.roles == ("ADMIN", "AUDITOR")
    assert current_user.tenant_id == "tenant-a"
    assert current_user.preferred_username == "alice"
    assert current_user.email == "alice@example.com"


def test_token_validator_returns_current_user_for_valid_token() -> None:
    """KeycloakTokenValidator should accept a valid token and return normalized user context."""

    signing_key = "unit-test-secret-with-sufficient-length"
    settings = Settings(
        keycloak_issuer_url="https://issuer.example/realms/dpp",
        jwt_audience="dpp-backend",
        jwt_algorithm="HS256",
    )
    validator = KeycloakTokenValidator(
        settings,
        signing_key_resolver=StaticSigningKeyResolver(signing_key),
    )
    token = jwt.encode(
        {
            "sub": "user-123",
            "iss": "https://issuer.example/realms/dpp",
            "aud": "dpp-backend",
            "exp": datetime.now(tz=timezone.utc) + timedelta(minutes=5),
            "realm_access": {"roles": ["SUPPLIER"]},
            "tenant_id": "tenant-a",
        },
        key=signing_key,
        algorithm="HS256",
    )

    current_user = validator.validate_token(token)

    assert current_user.subject == "user-123"
    assert current_user.roles == ("SUPPLIER",)
    assert current_user.tenant_id == "tenant-a"


def test_require_roles_rejects_users_without_matching_role() -> None:
    """Role dependencies should reject users that lack the required realm role."""

    dependency = require_roles(["ADMIN"])

    with pytest.raises(HTTPException) as exc_info:
        dependency(CurrentUser(subject="user-123", roles=("SUPPLIER",)))

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Insufficient role membership."
