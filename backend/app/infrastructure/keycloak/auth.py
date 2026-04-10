"""Keycloak JWT validation primitives used by FastAPI dependencies."""

from __future__ import annotations

from typing import Any, Protocol

import jwt
from jwt import InvalidTokenError, PyJWKClient

from app.config import Settings
from app.infrastructure.keycloak.models import CurrentUser


# Algorithms that are safe to use with asymmetric Keycloak-issued tokens.
# Accepting ``none`` or symmetric algorithms (e.g. ``HS256``) would allow
# an attacker to forge tokens, so we restrict to RS256 only.
_ALLOWED_ALGORITHMS: frozenset[str] = frozenset({"RS256"})


class TokenValidationError(ValueError):
    """Raised when a JWT cannot be validated against the configured Keycloak realm."""


class SigningKeyResolver(Protocol):
    """Resolve the signing key for a given JWT."""

    def prime(self) -> None:
        """Warm any internal caches before the first validation attempt."""

    def resolve_signing_key(self, token: str) -> Any:
        """Resolve the signing key for the provided token."""


class PyJWKSigningKeyResolver:
    """Resolve signing keys from the Keycloak JWKS endpoint using PyJWT."""

    def __init__(self, jwks_url: str) -> None:
        self._jwk_client = PyJWKClient(jwks_url)

    def prime(self) -> None:
        """Populate the underlying JWKS cache before request handling begins."""

        self._jwk_client.get_signing_keys()

    def resolve_signing_key(self, token: str) -> Any:
        """Resolve the signing key for the provided token."""

        return self._jwk_client.get_signing_key_from_jwt(token).key


class KeycloakTokenValidator:
    """Validate Keycloak-issued access tokens and normalize their claim set."""

    def __init__(
        self,
        settings: Settings,
        signing_key_resolver: SigningKeyResolver | None = None,
    ) -> None:
        self._settings = settings
        self._signing_key_resolver = signing_key_resolver or PyJWKSigningKeyResolver(
            settings.keycloak_jwks_url
        )

    def prime_jwks_cache(self) -> None:
        """Warm the JWKS cache for the configured Keycloak realm."""

        self._signing_key_resolver.prime()

    def validate_token(self, token: str) -> CurrentUser:
        """Validate a JWT and return a normalized authenticated user model."""

        # Guard against algorithm confusion attacks: reject any algorithm that
        # is not on the explicit allowlist before reaching jwt.decode().
        algorithm = self._settings.jwt_algorithm
        if algorithm not in _ALLOWED_ALGORITHMS:
            raise TokenValidationError(
                f"Unsupported JWT algorithm configured: {algorithm!r}. "
                f"Allowed: {sorted(_ALLOWED_ALGORITHMS)}"
            )

        # Normalize the issuer URL to ensure trailing-slash variants do not
        # cause spurious validation mismatches.
        normalized_issuer = self._settings.keycloak_issuer_url.strip().rstrip("/")

        try:
            signing_key = self._signing_key_resolver.resolve_signing_key(token)
            claims = jwt.decode(
                token,
                key=signing_key,
                algorithms=[algorithm],
                audience=self._settings.jwt_audience,
                issuer=normalized_issuer,
            )
            return CurrentUser.from_claims(claims)
        except (InvalidTokenError, ValueError) as exc:
            raise TokenValidationError("Token validation failed.") from exc
