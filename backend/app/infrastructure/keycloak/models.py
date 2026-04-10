"""Request-scoped identity models derived from Keycloak JWT claims."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class CurrentUser:
    """Normalized user context extracted from a validated access token."""

    subject: str
    roles: tuple[str, ...]
    tenant_id: str | None = None
    preferred_username: str | None = None
    email: str | None = None
    claims: Mapping[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_claims(cls, claims: Mapping[str, Any]) -> "CurrentUser":
        """Build a stable identity model from raw JWT claims."""

        subject = str(claims.get("sub", "")).strip()
        if not subject:
            raise ValueError("Token payload is missing the 'sub' claim.")

        realm_access = claims.get("realm_access") or {}
        raw_roles = realm_access.get("roles") or []
        roles = tuple(dict.fromkeys(str(role) for role in raw_roles if str(role).strip()))

        return cls(
            subject=subject,
            roles=roles,
            tenant_id=claims.get("tenant_id"),
            preferred_username=claims.get("preferred_username"),
            email=claims.get("email"),
            claims=dict(claims),
        )

    def has_role(self, role: str) -> bool:
        """Return whether the user holds the given realm role."""

        return role in self.roles
