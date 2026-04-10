# Keycloak Realm Import Placeholder

Place exported realm JSON files in this directory to auto-import them when the `keycloak` service starts with `--import-realm`.

Example file path:

- `infra/keycloak/realm-import/dpp-realm.json`

The repository now includes a local development baseline at `infra/keycloak/realm-import/dpp-realm.json` with:

- Realm: `dpp`
- Frontend OIDC client: `dpp-frontend` (public client, Authorization Code + PKCE)
- Backend client: `dpp-backend` (confidential client placeholder for later service-to-service flows)
- Realm roles: `ADMIN`, `MANUFACTURER`, `SUPPLIER`, `AUDITOR`, `CUSTOMER`

Local issuer and audience contract:

- Issuer: `http://keycloak:8080/realms/dpp`
- Backend audience: `dpp-backend`
- Frontend client ID: `dpp-frontend`

This import is intended for local development only. Replace placeholder secrets and tighten client settings before production use.
