# Frontend Scaffold

This directory reserves the frontend implementation area for the React and TypeScript web application.

## Intended Structure

```text
frontend/
|-- public/                Static assets
`-- src/
    |-- auth/              OIDC integration and auth helpers
    |-- features/          Feature-sliced application modules
    |-- components/        Shared UI building blocks
    `-- api/               API clients and data hooks
```

The scaffold reflects the feature-based architecture defined in the planning documents. The actual Vite, TypeScript, ESLint, Prettier, and UI tooling setup is deferred to the dedicated frontend initialization issue.