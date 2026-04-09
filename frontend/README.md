# Frontend Foundation

This directory contains the initialized frontend foundation for the React and TypeScript web application.

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

## Tooling Baseline

The frontend foundation now includes:

- Vite build and development server configuration
- TypeScript project configuration
- ESLint configuration for TypeScript + React Hooks + React Refresh
- Prettier formatting configuration
- Vitest + Testing Library test setup

## Commands

Run the following commands from the `frontend/` directory:

- `npm install`
- `npm run dev`
- `npm run build`
- `npm run lint`
- `npm run test:run`

## Feature Compatibility

The existing `src/features/*` directories are kept intact and remain aligned with the planned frontend modules documented in `doc/planning/07_modules.md`.