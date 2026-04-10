"""Unit tests for Keycloak JWT validation and authorization helpers.

Scope
-----
- ``CurrentUser`` claim normalization
- ``KeycloakTokenValidator`` happy-path and every failure branch
- ``require_roles`` allow-path, reject-path, and empty-list guard
- ``get_current_user`` FastAPI dependency (missing / wrong-scheme bearer)
- ``lru_cache`` isolation: caches are cleared after every test to prevent
  stale instances leaking between test cases.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.config import Settings, get_settings
from app.dependencies import get_current_user, get_token_validator, require_roles
from app.infrastructure.keycloak.auth import KeycloakTokenValidator, TokenValidationError
from app.infrastructure.keycloak.models import CurrentUser


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def clear_lru_caches() -> None:
    """Clear module-level LRU caches before and after each test.

    ``get_token_validator`` and ``get_settings`` are cached singletons; without
    a teardown step their instances bleed across test cases, leading to subtle
    ordering-dependent failures.
    """
    get_token_validator.cache_clear()
    get_settings.cache_clear()
    yield
    get_token_validator.cache_clear()
    get_settings.cache_clear()


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
    """KeycloakTokenValidator should accept a valid RS256 token and return normalized user context.

    A real RSA key pair is generated in-process so no external Keycloak is required.
    """
    from cryptography.hazmat.primitives.asymmetric import rsa

    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()

    settings = Settings(
        keycloak_issuer_url="https://issuer.example/realms/dpp",
        jwt_audience="dpp-backend",
        jwt_algorithm="RS256",
    )
    validator = KeycloakTokenValidator(
        settings,
        signing_key_resolver=StaticSigningKeyResolver(public_key),
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
        key=private_key,
        algorithm="RS256",
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


def test_require_roles_allows_user_with_matching_role() -> None:
    """require_roles should pass through users that hold one of the required roles."""

    dependency = require_roles(["SUPPLIER", "ADMIN"])

    # Should not raise; returns the same CurrentUser instance unmodified.
    user = CurrentUser(subject="user-456", roles=("SUPPLIER",))
    result = dependency(user)

    assert result is user


def test_require_roles_raises_value_error_for_empty_list() -> None:
    """require_roles([]) should raise ValueError immediately at decoration time.

    An empty required_roles list is almost certainly a programming mistake; the
    guard prevents silently granting all authenticated callers access.
    """

    with pytest.raises(ValueError, match="require_roles\\(\\) called with an empty role list"):
        require_roles([])


# ---------------------------------------------------------------------------
# KeycloakTokenValidator — negative paths
# ---------------------------------------------------------------------------


def _make_rs256_validator(
    *,
    issuer: str = "https://issuer.example/realms/dpp",
    audience: str = "dpp-backend",
) -> tuple["KeycloakTokenValidator", "Any"]:
    """Build a validator wired to an in-process RSA key pair for negative-path tests.

    Returns the validator and the private key needed to sign test tokens.
    The public key is passed to ``StaticSigningKeyResolver`` so no JWKS endpoint
    is required.
    """
    from cryptography.hazmat.primitives.asymmetric import rsa

    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()
    settings = Settings(
        keycloak_issuer_url=issuer,
        jwt_audience=audience,
        jwt_algorithm="RS256",
    )
    validator = KeycloakTokenValidator(
        settings,
        signing_key_resolver=StaticSigningKeyResolver(public_key),
    )
    return validator, private_key


def test_validate_token_rejects_expired_token() -> None:
    """validate_token should raise TokenValidationError for a token past its expiry."""

    validator, private_key = _make_rs256_validator()
    token = jwt.encode(
        {
            "sub": "user-expired",
            "iss": "https://issuer.example/realms/dpp",
            "aud": "dpp-backend",
            # exp in the past → token is expired
            "exp": datetime.now(tz=timezone.utc) - timedelta(seconds=30),
            "realm_access": {"roles": []},
        },
        key=private_key,
        algorithm="RS256",
    )

    with pytest.raises(TokenValidationError):
        validator.validate_token(token)


def test_validate_token_rejects_wrong_issuer() -> None:
    """validate_token should reject a token whose issuer does not match the configured realm."""

    validator, private_key = _make_rs256_validator()
    token = jwt.encode(
        {
            "sub": "user-bad-iss",
            "iss": "https://evil.example/realms/other",  # wrong issuer
            "aud": "dpp-backend",
            "exp": datetime.now(tz=timezone.utc) + timedelta(minutes=5),
            "realm_access": {"roles": []},
        },
        key=private_key,
        algorithm="RS256",
    )

    with pytest.raises(TokenValidationError):
        validator.validate_token(token)


def test_validate_token_rejects_wrong_audience() -> None:
    """validate_token should reject a token whose audience does not match the configured value."""

    validator, private_key = _make_rs256_validator()
    token = jwt.encode(
        {
            "sub": "user-bad-aud",
            "iss": "https://issuer.example/realms/dpp",
            "aud": "some-other-service",  # wrong audience
            "exp": datetime.now(tz=timezone.utc) + timedelta(minutes=5),
            "realm_access": {"roles": []},
        },
        key=private_key,
        algorithm="RS256",
    )

    with pytest.raises(TokenValidationError):
        validator.validate_token(token)


def test_validate_token_rejects_tampered_signature() -> None:
    """validate_token should surface a TokenValidationError when the signature is invalid."""

    validator, private_key = _make_rs256_validator()
    token = jwt.encode(
        {
            "sub": "user-tampered",
            "iss": "https://issuer.example/realms/dpp",
            "aud": "dpp-backend",
            "exp": datetime.now(tz=timezone.utc) + timedelta(minutes=5),
            "realm_access": {"roles": []},
        },
        key=private_key,
        algorithm="RS256",
    )
    # Corrupt the signature portion (last segment) to simulate tampering.
    header, payload, _ = token.split(".")
    tampered_token = f"{header}.{payload}.invalidsignature"

    with pytest.raises(TokenValidationError):
        validator.validate_token(tampered_token)


def test_validate_token_rejects_disallowed_algorithm() -> None:
    """validate_token should raise TokenValidationError for any algorithm outside the allowlist.

    This guards against algorithm-confusion attacks where an attacker presents a
    ``none``-algorithm or symmetric-algorithm token to bypass signature verification.
    """

    # Configure a validator with a non-RS256 algorithm that is not on the allowlist.
    settings = Settings(
        keycloak_issuer_url="https://issuer.example/realms/dpp",
        jwt_audience="dpp-backend",
        jwt_algorithm="HS512",  # not in _ALLOWED_ALGORITHMS
    )
    validator = KeycloakTokenValidator(
        settings,
        signing_key_resolver=StaticSigningKeyResolver("dummy-key"),
    )
    # The token content does not matter; the guard fires before jwt.decode() is called.
    # The dummy key is intentionally short; suppress the PyJWT key-length warning.
    import warnings

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        token = jwt.encode(
            {
                "sub": "user-alg",
                "iss": "https://issuer.example/realms/dpp",
                "aud": "dpp-backend",
                "exp": datetime.now(tz=timezone.utc) + timedelta(minutes=5),
                "realm_access": {"roles": []},
            },
            key="dummy-key",
            algorithm="HS512",
        )

    with pytest.raises(TokenValidationError, match="Unsupported JWT algorithm"):
        validator.validate_token(token)


# ---------------------------------------------------------------------------
# get_current_user dependency — 401 paths
# ---------------------------------------------------------------------------


def _make_stub_validator() -> "KeycloakTokenValidator":
    """Build a validator with a static RS256 key pair for auth dependency tests."""
    from cryptography.hazmat.primitives.asymmetric import rsa

    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()
    settings = Settings(
        keycloak_issuer_url="https://issuer.example/realms/dpp",
        jwt_audience="dpp-backend",
        jwt_algorithm="RS256",
    )
    return KeycloakTokenValidator(
        settings,
        signing_key_resolver=StaticSigningKeyResolver(public_key),
    )


def test_get_current_user_returns_401_for_missing_bearer() -> None:
    """get_current_user should return HTTP 401 when no Authorization header is present."""
    from fastapi import Depends, FastAPI

    from app.infrastructure.keycloak.models import CurrentUser as _CurrentUser

    mini_app = FastAPI()
    mini_app.dependency_overrides[get_token_validator] = _make_stub_validator

    @mini_app.get("/protected")
    def _protected(user: _CurrentUser = Depends(get_current_user)) -> dict:
        return {"sub": user.subject}

    client = TestClient(mini_app, raise_server_exceptions=False)
    response = client.get("/protected")

    assert response.status_code == 401


def test_get_current_user_returns_401_for_invalid_scheme() -> None:
    """get_current_user should return HTTP 401 when Authorization uses a non-Bearer scheme."""
    from fastapi import Depends, FastAPI

    from app.infrastructure.keycloak.models import CurrentUser as _CurrentUser

    mini_app = FastAPI()
    mini_app.dependency_overrides[get_token_validator] = _make_stub_validator

    @mini_app.get("/protected")
    def _protected(user: _CurrentUser = Depends(get_current_user)) -> dict:
        return {"sub": user.subject}

    client = TestClient(mini_app, raise_server_exceptions=False)
    # Send a Basic auth header, which should be rejected with 401
    response = client.get("/protected", headers={"Authorization": "Basic dXNlcjpwYXNz"})

    assert response.status_code == 401
