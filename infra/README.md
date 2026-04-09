# Infrastructure Scaffold

This directory contains the infrastructure layout for local development, deployment support, and operations assets.

## Intended Structure

```text
infra/
|-- backup/                Backup automation and helper scripts
|-- grafana/dashboards/    Provisioned dashboards
|-- keycloak/              Realm export and auth bootstrap material
|-- prometheus/            Metrics scrape configuration
|-- runbooks/              Recovery and operational procedures
`-- traefik/               Reverse proxy configuration
```

These directories are placeholders for the later Sprint 0 infrastructure issues. No Compose or service configuration is added here yet to keep this issue limited to structure enablement.